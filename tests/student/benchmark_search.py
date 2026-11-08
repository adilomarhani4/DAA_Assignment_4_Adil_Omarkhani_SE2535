"""Reproduce the naive/KMP/Rabin-Karp comparison recorded in ANALYSIS.md."""
import random
import statistics
import time
import pathlib
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from Python.source import algorithms

METHODS = {
    "naive": algorithms.naive,
    "kmp": algorithms.kmp,
    "rk": algorithms.rk,
}

def main():
    rng = random.Random(20261108)
    print("case,n,m,algorithm,run1_ms,run2_ms,run3_ms,median_ms,matches")
    for case in ("random", "repetitive"):
        for n in (300, 900, 1800):
            m = n // 10
            if case == "random":
                text = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(n))
                pattern = text[n // 2:n // 2 + m]
            else:
                text, pattern = "a" * n, "a" * m
            request = {"text": text, "pattern": pattern}
            expected = METHODS["naive"](request)
            for name, method in METHODS.items():
                assert method(request) == expected
                method(request)  # one warm-up; CPython has no JIT
                timings = []
                for _ in range(3):
                    start = time.perf_counter()
                    actual = method(request)
                    timings.append((time.perf_counter() - start) * 1000)
                    assert actual == expected
                print(",".join(map(str, (
                    case, n, m, name,
                    *(f"{x:.4f}" for x in timings),
                    f"{statistics.median(timings):.4f}",
                    len(expected["positions"]),
                ))))

if __name__ == "__main__":
    main()
