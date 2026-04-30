import pandas as pd

df = pd.read_csv("final_results.csv")

# remove today's validation outlier
df = df[df['timestamp'] != '20260426_085045']

grouped = df.groupby(['workload','mode','concurrency']).agg({
    'requests_per_sec':'mean',
    'latency_ms':'mean',
    'transfer_kbps':'mean',
    'page_faults':'mean',
    'minor_faults':'mean',
    'major_faults':'mean',
    'dtlb_misses':'mean',
    'context_switches':'mean',
    'cpu_migrations':'mean'
}).reset_index()

grouped = grouped.round(2)

grouped.to_csv("averaged_results.csv", index=False)

print(grouped)
print("\nSaved to averaged_results.csv")
