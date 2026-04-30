import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("averaged_results.csv")

# separate datasets
small_4k = df[(df.workload=="smallfile") & (df.mode=="4k")]
small_thp = df[(df.workload=="smallfile") & (df.mode=="thp")]
large_4k = df[(df.workload=="largefile") & (df.mode=="4k")]
large_thp = df[(df.workload=="largefile") & (df.mode=="thp")]

def plot_metric(metric, ylabel, title, filename, d1, d2, d3, d4):
    plt.figure()
    plt.plot(d1['concurrency'], d1[metric], marker='o', label='SmallFile-4K')
    plt.plot(d2['concurrency'], d2[metric], marker='o', label='SmallFile-THP')
    plt.plot(d3['concurrency'], d3[metric], marker='o', label='LargeFile-4K')
    plt.plot(d4['concurrency'], d4[metric], marker='o', label='LargeFile-THP')
    plt.xlabel("Concurrency")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(filename, dpi=300)
    plt.close()

plot_metric("requests_per_sec","Requests/sec","Throughput Comparison","graph_throughput.png",small_4k,small_thp,large_4k,large_thp)
plot_metric("latency_ms","Latency (ms)","Latency Comparison","graph_latency.png",small_4k,small_thp,large_4k,large_thp)
plot_metric("page_faults","Page Faults","Total Page Fault Comparison","graph_pagefaults.png",small_4k,small_thp,large_4k,large_thp)
plot_metric("minor_faults","Minor Faults","Minor Fault Comparison","graph_minorfaults.png",small_4k,small_thp,large_4k,large_thp)
plot_metric("context_switches","Context Switches","Context Switch Comparison","graph_contextswitch.png",small_4k,small_thp,large_4k,large_thp)

print("All graphs generated.")
