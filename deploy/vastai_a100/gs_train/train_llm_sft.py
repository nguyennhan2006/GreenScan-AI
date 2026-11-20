"""LoRA supervised fine-tuning of a chat model: loss = token cross-entropy on the answer only (prompt masked).

    python -u train_llm_sft.py --base Qwen/Qwen3-4B-Instruct-2507 --train out/teacher/explain_teacher.jsonl \
        --name explain-4b --epochs 2 --dtype fp16 [--merge]          # Kaggle T4
    python -u train_llm_sft.py --base Qwen/Qwen3-14B --train data/stance_sft.jsonl --name stance-14b --dtype bf16  # A100

Input rows: {"id", "company", "messages": [system, user], "target": "<assistant answer>"}. About 10% of companies are
held out for the validation loss (out-of-company). Writes out/<name>/adapter (+ merged/ with --merge) and
out/<name>/history.json (train loss every 10 steps, validation loss every epoch) for the charts.
"""
from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Timer, cell, jl, log, out_dir, save_json, seed_all  # noqa: E402


def encode(tok, row, max_len):
    prompt = tok.apply_chat_template(row["messages"], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    p = tok(prompt, add_special_tokens=False)["input_ids"]
    a = tok(row["target"] + (tok.eos_token or ""), add_special_tokens=False)["input_ids"]
    if len(p) + len(a) > max_len:
        return None
    return {"input_ids": p + a, "labels": [-100] * len(p) + a}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--train", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--epochs", type=float, default=2)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--r", type=int, default=16)
    ap.add_argument("--alpha", type=int, default=32)
    ap.add_argument("--max-len", type=int, default=2048)
    ap.add_argument("--accum", type=int, default=8)
    ap.add_argument("--dtype", choices=["fp16", "bf16"], default="fp16")
    ap.add_argument("--val-frac", type=float, default=0.1)
    ap.add_argument("--merge", action="store_true")
    ap.add_argument("--merge-dir", default="", help="where the merged fp16 model goes (Kaggle: /tmp, outside the 20 GB output)")
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()
    seed_all(args.seed)

    cell(f"sft load {args.base}")
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer, get_cosine_schedule_with_warmup
    dtype = torch.float16 if args.dtype == "fp16" else torch.bfloat16
    tok = AutoTokenizer.from_pretrained(args.base)
    rows = jl(args.train)
    comps = sorted({r.get("company") or "?" for r in rows})
    random.Random(args.seed).shuffle(comps)
    val_comps = set(comps[: max(1, round(len(comps) * args.val_frac))]) if len(comps) > 3 else set()
    enc = [(r, encode(tok, r, args.max_len)) for r in rows]
    dropped = sum(e is None for _, e in enc)
    train = [e for r, e in enc if e and (r.get("company") or "?") not in val_comps]
    val = [e for r, e in enc if e and (r.get("company") or "?") in val_comps]
    log(f"[sft] rows {len(rows)} · train {len(train)} · val {len(val)} (companies {sorted(val_comps)}) · "
        f"too long {dropped}")

    model = AutoModelForCausalLM.from_pretrained(args.base, torch_dtype=dtype, device_map={"": 0})
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    model = get_peft_model(model, LoraConfig(r=args.r, lora_alpha=args.alpha, lora_dropout=0.05, task_type="CAUSAL_LM",
                                             target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                                                             "gate_proj", "up_proj", "down_proj"]))
    model.print_trainable_parameters()
    params = [p for p in model.parameters() if p.requires_grad]
    steps = math.ceil(len(train) * args.epochs / args.accum)
    opt = torch.optim.AdamW(params, lr=args.lr, weight_decay=0.0)
    sch = get_cosine_schedule_with_warmup(opt, max(1, int(0.05 * steps)), steps)
    scaler = torch.amp.GradScaler(enabled=args.dtype == "fp16")
    hist = {"train": [], "val": [], "config": vars(args), "train_rows": len(train), "val_rows": len(val)}

    def loss_of(e):
        ids = torch.tensor([e["input_ids"]], device="cuda")
        lab = torch.tensor([e["labels"]], device="cuda")
        with torch.autocast("cuda", dtype=dtype):
            return model(input_ids=ids, labels=lab).loss

    def evaluate():
        if not val:
            return None
        model.eval()
        with torch.no_grad():
            v = [loss_of(e).float().item() for e in val]
        model.train()
        return round(sum(v) / len(v), 4)

    cell("sft train")
    t, step, seen, run, bad = Timer(), 0, 0, [], 0
    hist["val"].append({"epoch": 0, "loss": evaluate()})
    model.train()
    total = int(len(train) * args.epochs)
    order = []
    while len(order) < total:
        ep = list(range(len(train)))
        random.shuffle(ep)
        order += ep
    for i, j in enumerate(order[:total], 1):
        loss = loss_of(train[j]) / args.accum
        if not torch.isfinite(loss):
            bad += 1
            if bad >= 5:
                raise SystemExit("[sft] loss is not finite 5 times: try --dtype bf16 (A100) or a smaller --lr")
            opt.zero_grad(set_to_none=True)
            continue
        scaler.scale(loss).backward()
        run.append(loss.item() * args.accum)
        if i % args.accum == 0 or i == total:
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            scaler.step(opt)
            scaler.update()
            opt.zero_grad(set_to_none=True)
            sch.step()
            step += 1
            if step % 10 == 0 or i == total:
                hist["train"].append({"step": step, "epoch": round(i / len(train), 3), "loss": round(sum(run) / len(run), 4),
                                      "lr": sch.get_last_lr()[0]})
                log(f"[sft] step {step}/{steps} epoch {i / len(train):.2f} loss {sum(run) / len(run):.4f} · {t()} s")
                run = []
        if i % len(train) == 0 and i < total:
            v = evaluate()
            hist["val"].append({"epoch": round(i / len(train), 2), "loss": v})
            log(f"[sft] epoch {i / len(train):.0f} val loss {v}")
    hist["val"].append({"epoch": args.epochs, "loss": evaluate()})
    hist["seconds"] = t()
    log(f"[sft] val losses {hist['val']}")

    cell("sft save")
    od = out_dir(args.name)
    model.save_pretrained(od / "adapter")
    tok.save_pretrained(od / "adapter")
    save_json(od / "history.json", hist)
    if args.merge:
        mdir = Path(args.merge_dir) if args.merge_dir else od / "merged"
        merged = model.merge_and_unload()
        merged.save_pretrained(mdir, safe_serialization=True)
        tok.save_pretrained(mdir)
        log(f"[sft] merged model -> {mdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
