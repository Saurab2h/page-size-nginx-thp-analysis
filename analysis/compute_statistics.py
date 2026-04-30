import pandas as pd

INPUT = "data/processed/results.csv"
OUTPUT = "data/statistics/summary.csv"

df = pd.read_csv(INPUT)

# Group by file_type ALSO (CRITICAL FIX)
summary = df.groupby(["file_type", "mode", "concurrency"]).agg(
    requests_per_sec_mean=("requests_per_sec", "mean"),
    requests_per_sec_std=("requests_per_sec", "std"),
    p95_latency_mean=("p95_latency_ms", "mean"),
    page_faults_mean=("page_faults", "mean"),
    minor_faults_mean=("minor_faults", "mean"),
    major_faults_mean=("major_faults", "mean"),
    context_switches_mean=("context_switches", "mean")
).reset_index()

summary.to_csv(OUTPUT, index=False)

print("Statistical summary saved to", OUTPUT)
print(summary)
