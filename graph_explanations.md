# Complete Breakdown of the 10 Performance Graphs

This guide pairs the actual graphs with exactly what you need to point out during your viva defense. Use this as your cheat sheet.

---

## 1. Throughput (Requests Per Second)

### Small File Throughput
![Small File Throughput](../IEEE_Report/graphs/small_throughput.png)
* **What you see:** The orange bar (THP) is consistently higher than the blue bar (4K) across all concurrency levels (50, 200, 400).
* **What it means:** For small lightweight files, Transparent Huge Pages reduces the TLB (Translation Lookaside Buffer) misses. Memory translation is faster, so Nginx can push out more requests per second.

### Large File Throughput
![Large File Throughput](../IEEE_Report/graphs/large_throughput.png)
* **What you see:** THP is slightly better at 50 and 400, but there is a clear **dip** at concurrency 200 (from 6.13 to 5.64 req/s).
* **What it means:** This is the first indicator of the "danger zone". At medium concurrency with 5MB files, the kernel struggles to coalesce 2MB contiguous blocks (compaction), which slightly degrades the actual file-serving speed.

---

## 2. Request Latency (Response Time)

### Small File Latency
![Small File Latency](../IEEE_Report/graphs/small_latency.png)
* **What you see:** The orange bar (THP) is lower (faster) than the blue bar across the board.
* **What it means:** Because memory translation is more efficient with huge pages, the time taken to process and respond to each lightweight HTTP request is physically shorter.

### Large File Latency
![Large File Latency](../IEEE_Report/graphs/large_latency.png)
* **What you see:** THP is slightly faster at 50 and 400, but at 200, the orange bar spikes higher (~35,453 ms vs ~32,639 ms).
* **What it means:** This confirms the throughput degradation. The Nginx worker processes are being delayed because the underlying Linux kernel is locking memory structures to perform background compaction.

---

## 3. Total Page Faults (The Core Metric)

### Small File Page Faults
![Small File Page Faults](../IEEE_Report/graphs/small_pagefaults.png)
* **What you see:** At concurrency 400, the blue bar is huge (~6,447) while the orange bar is less than half (~2,677). That's a 58% reduction.
* **What it means:** This is THP working beautifully. Because each page maps 2MB instead of 4KB, the kernel has to process far fewer page faults to cover the same amount of memory.

### Large File Page Faults (The Major Discovery)
![Large File Page Faults](../IEEE_Report/graphs/large_pagefaults.png)
* **What you see:** A catastrophic explosion of the orange bar at concurrency 200 (jumping to 263,899 faults).
* **What it means:** This is the centerpiece of your research. Nginx is allocating and freeing buffers so rapidly for large files that the kernel enters a thrashing cycle. `khugepaged` is aggressively trying to compact fragmented memory into huge pages, failing, and constantly generating faults. 

---

## 4. Minor Page Faults (Validating the Type of Overhead)

### Small File Minor Faults
![Small File Minor Faults](../IEEE_Report/graphs/small_minorfaults.png)
* **What you see:** Identical trend to the total page faults.
* **What it means:** Confirms that the system is not bottle-necking on disk reads (major faults). All overhead is purely memory-mapping related.

### Large File Minor Faults
![Large File Minor Faults](../IEEE_Report/graphs/large_minorfaults.png)
* **What you see:** Identical to the large total faults spike at 200.
* **What it means:** Confirms that the 263,899 fault anomaly is entirely due to "soft" memory faults (updating page tables during compaction and migration) rather than slow disk I/O. The files are cached in RAM, but managing the memory mapping is failing.

---

## 5. Context Switches (The Scheduler Impact)

### Small File Context Switches
![Small File Context Switches](../IEEE_Report/graphs/small_contextswitches.png)
* **What you see:** Blue and orange bars are almost exactly the same height at all levels.
* **What it means:** For small files, THP optimizes memory *without* disturbing the CPU scheduler. The Nginx event loop runs smoothly.

### Large File Context Switches (The Final Proof)
![Large File Context Switches](../IEEE_Report/graphs/large_contextswitches.png)
* **What you see:** The orange bar explodes at concurrency 200 (reaching over 16.6 Million context switches vs the baseline 0.9 Million).
* **What it means:** This is your final definitive proof of *why* throughput and latency degraded. A context switch happens when the CPU stops running Nginx and switches to the kernel. The kernel was pausing Nginx over 16 million times to manage memory defragmentation/compaction.

---

## Summary Strategy for the Interview:
1. Show **Graphs 1 & 5** to prove THP is a great idea in theory (lightweight requests).
2. Jump to **Graph 6** to show the shocking anomaly (heavy requests).
3. Use **Graph 10** to explain the *root cause* of the anomaly (the kernel paused the web server 16 million times to clean up memory).
