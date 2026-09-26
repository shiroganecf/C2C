"""Week-1 sanity check: Qwen3-0.6B KV cache layout and hidden_states indexing.
Only uses torch + transformers (no rosetta code)."""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.cache_utils import DynamicCache

model_name = "Qwen/Qwen3-0.6B"
tok = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16).to("cuda")
model.eval()

cfg = model.config
print("=== config ===")
print("num_hidden_layers       :", cfg.num_hidden_layers)
print("num_attention_heads (Q) :", cfg.num_attention_heads)
print("num_key_value_heads (KV):", cfg.num_key_value_heads)
print("head_dim                :", cfg.head_dim)
print("hidden_size             :", cfg.hidden_size)

text = "Cache-to-Cache lets two language models talk through their KV caches."
inputs = tok(text, return_tensors="pt").to("cuda")
input_ids = inputs["input_ids"]
T = input_ids.shape[1]
print("\n=== input ===")
print("T (num tokens):", T)

with torch.no_grad():
    out = model(**inputs, use_cache=True, output_hidden_states=True)

pkv = out.past_key_values
print("\n=== past_key_values ===")
print("type                 :", type(pkv).__name__, "| is DynamicCache:", isinstance(pkv, DynamicCache))
print("len(key_cache)       :", len(pkv.key_cache))
print("key_cache[0].shape   :", tuple(pkv.key_cache[0].shape))
print("value_cache[0].shape :", tuple(pkv.value_cache[0].shape))
print("all layers same shape:", all(k.shape == pkv.key_cache[0].shape for k in pkv.key_cache))

hs = out.hidden_states
with torch.no_grad():
    emb = model.model.embed_tokens(input_ids)
print("\n=== hidden_states ===")
print("len(hidden_states)     :", len(hs))
print("hidden_states[0].shape :", tuple(hs[0].shape))
print("hidden_states[0] == embed_tokens(input_ids):", torch.equal(hs[0], emb))
print("max abs diff           :", (hs[0] - emb).abs().max().item())

print("\npeak GPU memory (GB):", round(torch.cuda.max_memory_allocated() / 1e9, 2))
