import gc
import os
import sys
import time
import psutil
import torch
from pathlib import Path

# Ensure repository root is in sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from sentence_transformers import SentenceTransformer


def run_hardware_audit():
    models_to_profile = [
        "ytu-ce-cosmos/turkish-e5-large",
        "intfloat/multilingual-e5-large-instruct",
        "ytu-ce-cosmos/modernbert-tr-embed",
        "Qwen/Qwen3-Embedding-0.6B",
        "Qwen/Qwen3-Embedding-4B",
        "Qwen/Qwen3-Embedding-8B",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    ]

    print("=================================================================")
    print("  NSOSYAL PUSULA — STRICT HARDWARE & DEVICE AUDIT               ")
    print("=================================================================")
    process = psutil.Process(os.getpid())

    results = {}

    for model_id in models_to_profile:
        print(f"\n>>> Profiling: {model_id}")
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()

        ram_before = process.memory_info().rss / (1024**3)

        t0 = time.perf_counter()
        try:
            device_target = "cuda" if torch.cuda.is_available() else "cpu"
            model = SentenceTransformer(model_id, device=device_target)
            load_time = time.perf_counter() - t0

            # Inspect devices of all model parameters
            devices = set(str(p.device) for p in model.parameters())
            param_count = sum(p.numel() for p in model.parameters())
            dtype = next(model.parameters()).dtype

            test_sentence = (
                "Yapay zekâ ve açık kaynak yazılımlar üniversitelerde yeni bir eğitim modeli başlatıyor."
            )

            # Warmup
            _ = model.encode([test_sentence], show_progress_bar=False)

            # Latency over 20 iterations
            t_start = time.perf_counter()
            iters = 20
            for _ in range(iters):
                _ = model.encode([test_sentence], show_progress_bar=False)
            avg_lat = ((time.perf_counter() - t_start) / iters) * 1000.0

            cuda_alloc = (
                torch.cuda.memory_allocated() / (1024**3)
                if torch.cuda.is_available()
                else 0.0
            )
            cuda_peak = (
                torch.cuda.max_memory_allocated() / (1024**3)
                if torch.cuda.is_available()
                else 0.0
            )
            cuda_reserved = (
                torch.cuda.memory_reserved() / (1024**3)
                if torch.cuda.is_available()
                else 0.0
            )
            ram_now = process.memory_info().rss / (1024**3)

            is_fully_gpu = all(d.startswith("cuda") for d in devices)

            info = {
                "model_id": model_id,
                "status": "SUCCESS",
                "load_time_sec": round(load_time, 2),
                "param_count_m": round(param_count / 1e6, 1),
                "dtype": str(dtype),
                "devices": list(devices),
                "is_fully_on_gpu": is_fully_gpu,
                "cuda_allocated_gb": round(cuda_alloc, 2),
                "cuda_peak_allocated_gb": round(cuda_peak, 2),
                "cuda_reserved_gb": round(cuda_reserved, 2),
                "process_ram_gb": round(ram_now, 2),
                "ram_delta_gb": round(ram_now - ram_before, 2),
                "avg_latency_ms": round(avg_lat, 2),
            }
            results[model_id] = info

            print(f"  Status: SUCCESS")
            print(f"  Parameter Count: {info['param_count_m']}M")
            print(f"  Dtype: {info['dtype']}")
            print(f"  Parameter Device(s): {info['devices']}")
            print(f"  Is Fully on GPU: {info['is_fully_on_gpu']}")
            print(f"  CUDA Allocated: {info['cuda_allocated_gb']} GB (Peak: {info['cuda_peak_allocated_gb']} GB, Reserved: {info['cuda_reserved_gb']} GB)")
            print(f"  Process RAM: {info['process_ram_gb']} GB (Delta: {info['ram_delta_gb']} GB)")
            print(f"  Avg Single-Sentence Latency: {info['avg_latency_ms']} ms")

            # Clean up model from GPU memory for next model
            del model
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        except Exception as e:
            print(f"  Status: FAILED -> {e}")
            results[model_id] = {"status": "FAILED", "error": str(e)}

    print("\n=================================================================")
    return results


if __name__ == "__main__":
    run_hardware_audit()
