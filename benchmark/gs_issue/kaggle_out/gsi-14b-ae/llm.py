"""Greedy chat generation shared by the screening runs: vLLM (LLM_BACKEND=vllm, default) or transformers (LLM_BACKEND=hf).

    m = LLM("Qwen/Qwen3-4B-Instruct-2507", max_len=16384, tp=1)
    texts = m.gen([[{"role": "system", "content": ...}, {"role": "user", "content": ...}], ...], max_tokens=512)

One process loads one repo; trying the next candidate (fp16 -> AWQ, vllm -> hf) is multirun.py's job, in a new process.
Prompts are tokenized here (chat template, enable_thinking off unless think=True) and passed as token ids, so no double BOS.
A prompt longer than max_len - max_tokens comes back as None and is counted in m.overflow (never crashes the batch).
Text after </think> is kept when a model still thinks. m.ntok_in / m.ntok_out count tokens of every call.
"""
import os
import time

# ChatML, for tokenizers that ship no chat template (vilm/vinallama-2.7b-chat): the format its model card describes
CHATML = ("{% for m in messages %}{{ '<|im_start|>' + m['role'] + '\n' + m['content'] + '<|im_end|>\n' }}{% endfor %}"
          "{% if add_generation_prompt %}{{ '<|im_start|>assistant\n' }}{% endif %}")


class LLM:
    def __init__(self, repo, max_len=16384, tp=1, think=False, **kw):
        self.repo, self.max_len, self.think = repo, max_len, think
        self.overflow = self.ntok_in = self.ntok_out = 0
        self.backend = os.environ.get("LLM_BACKEND", "vllm")
        t0 = time.time()
        if self.backend == "vllm":
            from vllm import LLM as V
            self.eng = V(model=repo, dtype="float16", max_model_len=max_len, tensor_parallel_size=tp, seed=0,
                         gpu_memory_utilization=float(os.environ.get("GPU_UTIL", "0.90")), trust_remote_code=True, **kw)
            self.tok = self.eng.get_tokenizer()
        else:
            import torch
            import transformers
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import transformers.integrations.sdpa_attention as sd
            if hasattr(sd, "use_gqa_in_sdpa"):  # T4: enable_gqa only runs in the math kernel (heads x L x L scores, OOM): repeat K/V instead
                sd.use_gqa_in_sdpa = lambda *a, **k: False
            dkw = "dtype" if int(transformers.__version__.split(".")[0]) >= 5 else "torch_dtype"
            self.tok = AutoTokenizer.from_pretrained(repo, trust_remote_code=True)
            cuda = torch.cuda.is_available()
            load = lambda remote: AutoModelForCausalLM.from_pretrained(repo, **{dkw: torch.float16 if cuda else torch.float32},
                                                                       device_map="auto" if cuda else None, trust_remote_code=remote).eval()
            try:
                self.model = load(True)
            except ImportError as e:  # repo code written for an older transformers (Phi-4-mini: LossKwargs); the built-in class works
                print(f"[llm] remote code failed ({e}); loading the built-in transformers class", flush=True)
                self.model = load(False)
        if not getattr(self.tok, "chat_template", None):
            self.tok.chat_template = CHATML
            print(f"[llm] {repo}: no chat template, using ChatML", flush=True)
        print(f"[llm] {repo} loaded with {self.backend} in {time.time() - t0:.0f}s", flush=True)

    def ids(self, msgs):
        kw = dict(tokenize=False, add_generation_prompt=True, enable_thinking=self.think)
        try:
            text = self.tok.apply_chat_template(msgs, **kw)
        except Exception:  # templates without a system role: fold it into the first user turn
            if msgs[0]["role"] != "system":
                raise
            text = self.tok.apply_chat_template([dict(msgs[1], content=msgs[0]["content"] + "\n\n" + msgs[1]["content"])] + msgs[2:], **kw)
        if os.environ.get("STRIP_EMPTY_THINK") == "1":  # models fine-tuned by PIPE-T1-04 train.py on Qwen3.5 (no empty think block)
            text = text.replace("<think>\n\n</think>\n\n", "")
        return self.tok(text, add_special_tokens=False).input_ids

    def gen(self, batch, max_tokens):
        ids = [self.ids(m) for m in batch]
        ok = [i for i, x in enumerate(ids) if len(x) <= self.max_len - max_tokens]
        self.overflow += len(ids) - len(ok)
        self.ntok_in += sum(len(ids[i]) for i in ok)
        out = [None] * len(batch)
        if self.backend == "vllm":
            from vllm import SamplingParams
            sp = SamplingParams(temperature=0.0, max_tokens=max_tokens, seed=0)
            res = self.eng.generate([{"prompt_token_ids": ids[i]} for i in ok], sp, use_tqdm=False)
            for i, r in zip(ok, res):
                out[i] = r.outputs[0].text
                self.ntok_out += len(r.outputs[0].token_ids)
        else:
            import torch
            bs = int(os.environ.get("HF_BATCH", "4"))
            pad = self.tok.pad_token_id if self.tok.pad_token_id is not None else self.tok.eos_token_id
            dev = next(self.model.parameters()).device
            order = sorted(ok, key=lambda i: len(ids[i]))
            for k in range(0, len(order), bs):
                part = order[k:k + bs]
                n = max(len(ids[i]) for i in part)
                x = torch.tensor([[pad] * (n - len(ids[i])) + ids[i] for i in part], device=dev)
                mask = torch.tensor([[0] * (n - len(ids[i])) + [1] * len(ids[i]) for i in part], device=dev)
                with torch.no_grad():
                    y = self.model.generate(input_ids=x, attention_mask=mask, max_new_tokens=max_tokens, do_sample=False, pad_token_id=pad)
                for i, row in zip(part, y[:, n:].tolist()):
                    row = [t for t in row if t != pad]
                    self.ntok_out += len(row)
                    out[i] = self.tok.decode(row, skip_special_tokens=True)
        return [o.split("</think>")[-1].strip() if o is not None else None for o in out]
