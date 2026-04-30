import os
import re
import csv

RAW_DIR = "data/raw"
OUTPUT = "data/processed/results.csv"


def extract_ab_metrics(filepath):
    with open(filepath) as f:
        content = f.read()

    rps = re.search(r"Requests per second:\s+([\d.]+)", content)
    tpr = re.search(r"Time per request:\s+([\d.]+) \[ms\] \(mean\)", content)
    p95 = re.search(r"\s95%\s+(\d+)", content)

    return {
        "requests_per_sec": float(rps.group(1)) if rps else 0,
        "time_per_request_ms": float(tpr.group(1)) if tpr else 0,
        "p95_latency_ms": int(p95.group(1)) if p95 else 0
    }


def extract_perf_metrics(filepath):
    with open(filepath) as f:
        content = f.read()

    def find(metric):
        match = re.search(rf"([\d,]+)\s+{metric}", content)
        return int(match.group(1).replace(",", "")) if match else 0

    return {
        "page_faults": find("page-faults"),
        "minor_faults": find("minor-faults"),
        "major_faults": find("major-faults"),
        "dtlb_misses": find("dTLB-load-misses"),
        "context_switches": find("context-switches"),
    }


rows = []

for file in os.listdir(RAW_DIR):
    if file.startswith("ab_") and file.endswith(".txt"):
        parts = file.replace(".txt", "").split("_")

        # NEW FORMAT:
        # ab_smallfile_4k_50_20260301_120000.txt

        file_type = parts[1]
        mode = parts[2]
        concurrency = parts[3]
        timestamp = parts[4] + "_" + parts[5]

        ab_path = os.path.join(RAW_DIR, file)
        ab_metrics = extract_ab_metrics(ab_path)

        perf_file = f"perf_{file_type}_{mode}_{concurrency}_{timestamp}.txt"
        perf_path = os.path.join(RAW_DIR, perf_file)

        if not os.path.exists(perf_path):
            continue

        perf_metrics = extract_perf_metrics(perf_path)

        row = {
            "file_type": file_type,
            "mode": mode,
            "concurrency": int(concurrency),
            **ab_metrics,
            **perf_metrics
        }

        rows.append(row)


# Safety check
if not rows:
    print("No matching experiment pairs found.")
    exit()

# Ensure processed directory exists
os.makedirs("data/processed", exist_ok=True)

with open(OUTPUT, "w", newline="") as csvfile:
    fieldnames = rows[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("Results extracted to", OUTPUT)
