import os
import re
import csv
from collections import defaultdict

RAW_DIR = "../data/raw"

results = []

def parse_ab_file(filepath):
    data = {}
    with open(filepath, 'r') as f:
        text = f.read()

    rps = re.search(r"Requests per second:\s+([\d\.]+)", text)
    latency = re.search(r"Time per request:\s+([\d\.]+) \[ms\] \(mean\)", text)
    transfer = re.search(r"Transfer rate:\s+([\d\.]+)", text)

    if rps: data['requests_per_sec'] = float(rps.group(1))
    if latency: data['latency_ms'] = float(latency.group(1))
    if transfer: data['transfer_kbps'] = float(transfer.group(1))

    return data

def parse_perf_file(filepath):
    data = {}
    with open(filepath, 'r') as f:
        text = f.read()

    patterns = {
        'page_faults': r"([\d,]+)\s+page-faults",
        'minor_faults': r"([\d,]+)\s+minor-faults",
        'major_faults': r"([\d,]+)\s+major-faults",
        'dtlb_misses': r"([\d,]+)\s+dTLB-load-misses",
        'context_switches': r"([\d,]+)\s+context-switches",
        'cpu_migrations': r"([\d,]+)\s+cpu-migrations"
    }

    for key, pat in patterns.items():
        m = re.search(pat, text)
        if m:
            data[key] = int(m.group(1).replace(",", ""))
        else:
            data[key] = 0

    return data

for fname in os.listdir(RAW_DIR):
    if fname.startswith("ab_") and fname.endswith(".txt"):
        parts = fname.replace(".txt","").split("_")
        # ab_smallfile_thp_50_timestamp
        workload = parts[1]
        mode = parts[2]
        concurrency = int(parts[3])
        timestamp = "_".join(parts[4:])

        ab_path = os.path.join(RAW_DIR, fname)
        perf_name = f"perf_{workload}_{mode}_{concurrency}_{timestamp}.txt"
        perf_path = os.path.join(RAW_DIR, perf_name)

        if os.path.exists(perf_path):
            row = {
                "workload": workload,
                "mode": mode,
                "concurrency": concurrency,
                "timestamp": timestamp
            }
            row.update(parse_ab_file(ab_path))
            row.update(parse_perf_file(perf_path))
            results.append(row)

output_file = "final_results.csv"
with open(output_file, "w", newline="") as csvfile:
    fieldnames = [
        "workload","mode","concurrency","timestamp",
        "requests_per_sec","latency_ms","transfer_kbps",
        "page_faults","minor_faults","major_faults",
        "dtlb_misses","context_switches","cpu_migrations"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for r in results:
        writer.writerow(r)

print(f"Parsed {len(results)} experiment pairs into {output_file}")
