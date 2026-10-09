"""Analyses run in the background, so the browser can say where they are.

A sustainability report and an annual report take about two minutes on a laptop
CPU, longer with the stance model on. Holding one HTTP request open for that
long gave the reviewer a spinner and nothing else -- the intake screen had to
print "the server does not report progress, so no ticks are shown" -- and, for
uploads, ran the pipeline on the API's event loop, so even `/health` stalled
until the run finished.

A job is the same `OrchestratorAgent.run` on a worker thread, reporting each
step of its plan. One worker by default: the pipeline is CPU-bound, and two
runs on a four-core laptop finish later than the same two one after the other.
Jobs live in memory; what outlives the process is the run itself, written to
`runs_dir` exactly as before.
"""

from __future__ import annotations

import threading
import time
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field

# step key, 1-based index, number of steps, free-text detail
Progress = Callable[[str, int, int, str], None]


@dataclass
class Job:
    job_id: str
    label: str = ""
    state: str = "queued"  # queued | running | done | failed
    step: str = ""
    step_index: int = 0
    total_steps: int = 0
    detail: str = ""
    run_id: str | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    finished_at: float | None = None

    def to_json(self, ahead: int = 0) -> dict:
        payload = asdict(self)
        end = self.finished_at or time.time()
        payload["elapsed_seconds"] = round(end - self.started_at, 1) if self.started_at else 0.0
        payload["queue_position"] = ahead
        return payload


class JobRunner:
    def __init__(self, workers: int = 1, keep: int = 50):
        self._pool = ThreadPoolExecutor(max_workers=max(1, workers), thread_name_prefix="greenscan-job")
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._keep = keep

    def submit(self, work: Callable[[Progress], str], label: str = "") -> Job:
        """Queue `work(progress) -> run_id`; returns at once."""
        job = Job(job_id=uuid.uuid4().hex[:12], label=label)
        with self._lock:
            self._jobs[job.job_id] = job
            self._forget_old()

        def progress(step: str, index: int, total: int, detail: str = "") -> None:
            with self._lock:
                job.step, job.step_index, job.total_steps, job.detail = step, index, total, detail

        def run() -> None:
            with self._lock:
                job.state, job.started_at = "running", time.time()
            try:
                run_id = work(progress)
                with self._lock:
                    job.run_id, job.state = run_id, "done"
            except Exception as exc:  # noqa: BLE001 - a failed run is reported, not raised into a thread
                with self._lock:
                    job.state, job.error = "failed", str(exc) or exc.__class__.__name__
            finally:
                with self._lock:
                    job.finished_at = time.time()

        self._pool.submit(run)
        return job

    def status(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            ahead = sum(
                1 for other in self._jobs.values()
                if other.state in {"queued", "running"} and other.created_at < job.created_at
            ) if job.state == "queued" else 0
            return job.to_json(ahead)

    def _forget_old(self) -> None:
        finished = sorted(
            (j for j in self._jobs.values() if j.state in {"done", "failed"}),
            key=lambda j: j.created_at,
        )
        for job in finished[: max(0, len(self._jobs) - self._keep)]:
            self._jobs.pop(job.job_id, None)
