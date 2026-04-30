import pandas as pd
import matplotlib.pyplot as plt
import os

# Paths
SUMMARY_FILE = "data/statistics/summary.csv"
PLOT_DIR = "analysis/plots"

# Create plots directory if not exists
os.makedirs(PLOT_DIR, exist_ok=True)

# Load data
df = pd.read_csv(SUMMARY_FILE)

# -----------------------------
# 1. Throughput vs Concurrency
# -----------------------------
plt.figure()
for mode in df['mode'].unique():
    subset = df[df['mode'] == mode]
    plt.plot(subset['concurrency'],
             subset['requests_per_sec_mean'],
             marker='o',
             label=mode)

plt.xlabel("Concurrency")
plt.ylabel("Requests per Second")
plt.title("Throughput vs Concurrency")
plt.legend()
plt.savefig(f"{PLOT_DIR}/throughput.png")
plt.close()

# -----------------------------
# 2. Minor Page Faults
# -----------------------------
plt.figure()
for mode in df['mode'].unique():
    subset = df[df['mode'] == mode]
    plt.plot(subset['concurrency'],
             subset['minor_faults_mean'],
             marker='o',
             label=mode)

plt.xlabel("Concurrency")
plt.ylabel("Minor Page Faults")
plt.title("Minor Page Faults vs Concurrency")
plt.legend()
plt.savefig(f"{PLOT_DIR}/minor_faults.png")
plt.close()

# -----------------------------
# 3. Context Switches
# -----------------------------
plt.figure()
for mode in df['mode'].unique():
    subset = df[df['mode'] == mode]
    plt.plot(subset['concurrency'],
             subset['context_switches_mean'],
             marker='o',
             label=mode)

plt.xlabel("Concurrency")
plt.ylabel("Context Switches")
plt.title("Context Switches vs Concurrency")
plt.legend()
plt.savefig(f"{PLOT_DIR}/context_switches.png")
plt.close()

print("Plots saved to analysis/plots/")
