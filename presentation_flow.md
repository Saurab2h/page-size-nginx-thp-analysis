# Nginx THP Analysis - Viva Presentation Flow

## Part 1: The Elevator Pitch (1-2 minutes)
* **Goal:** Explain what you did and why it matters immediately.
* **Script:** "Good morning. Our project investigates the performance impact of Transparent Huge Pages (THP) on an Nginx web server. By default, Linux uses 4KB pages for memory. THP automatically coalesces these into 2MB pages to reduce CPU translation overhead (TLB misses). We wanted to see if this actually helps a static web server. We tested Nginx under both 4KB and THP modes, using small (4KB) and large (5MB) files, across low to high client concurrencies (50, 200, 400). We measured throughput, latency, page faults, and context switches."
* **The Big Reveal:** "What we discovered is a sharp bifurcation. For lightweight workloads, THP is fantastic—it reduces page faults by up to 58% and boosts throughput. But for memory-intensive large-file workloads at sustained concurrency, THP backfires catastrophically. The kernel's aggressive background memory compaction stalls the server, causing page faults to spike by nearly 75x and context switches to jump from 900,000 to over 16.6 million. Our paper proves that THP is a conditional optimization that can actually harm web servers under heavy memory pressure."

## Part 2: Explaining the Methodology (1 minute)
* **Setup:** Ubuntu 24.04 VM, 2 vCPUs, 4GB RAM. Nginx 1.24.0.
* **Tools:** Apache Benchmark (`ab`) for generating traffic (10,000 requests per run) and Linux `perf stat` for capturing kernel metrics.
* **Control:** We flushed the page cache (`drop_caches`) and restarted Nginx before every single run. We ran everything 3 times and averaged the results to eliminate VM noise.

## Part 3: Walking Through the Results (3 minutes)

**1. Throughput & Latency (The User Perspective)**
*   **Small Files (Figs 1 & 3):** Show that THP consistently wins (3-5% better throughput, lower latency).
*   **Large Files (Figs 2 & 4):** Point directly to the drop at concurrency 200. "Here, standard 4K paging gave us 6.13 req/sec, but THP dropped to 5.64 req/sec, and latency worsened by nearly 3 seconds."

**2. Page Faults (The Kernel Perspective)**
*   **Small Files (Figs 5 & 7):** Point to the 400 concurrency mark. "Under heavy lightweight load, THP cuts faults from ~6.4k down to ~2.6k. This is THP working exactly as intended."
*   **Large Files (Figs 6 & 8):** Point to the massive spike at 200 concurrency. "This is the core discovery of our paper. Faults exploded from 3,500 to 263,899. This means the kernel is thrashing trying to allocate huge pages for temporary file-serving buffers."

**3. Context Switches (The Scheduler Perspective)**
*   **Context Switches (Figs 9 & 10):** "To prove this wasn't just a memory quirk, we looked at the CPU scheduler. Figure 10 shows context switches jumping from 0.9 million to 16.6 million. This proves the kernel is pausing Nginx worker processes to migrate physical memory pages around (compaction)."

## Part 4: Conclusion (1 minute)
* "Our research concludes that THP is highly effective for lightweight API or HTML serving. However, for serving large assets like video or heavy images, system administrators should be cautious. The overhead of `khugepaged` memory compaction can dominate execution. In production, careful monitoring of `/proc/meminfo` is required."

---

# Possible Cross-Questions & Perfect Answers

**Q1. Why did the massive page fault spike happen exactly at 200 concurrency and not 400?**
* **Answer:** "At concurrency 50, there is enough free, unfragmented memory for THP to easily allocate 2MB pages. At concurrency 400, memory pressure is so extreme from the start that the kernel likely falls back to standard 4KB pages immediately, avoiding compaction overhead. Concurrency 200 represents the 'danger zone'—memory is heavily fragmented, but the kernel *still tries* to aggressively compact it, leading to a sustained thrashing cycle."

**Q2. How did you know THP was actually working if Nginx doesn't explicitly request huge pages?**
* **Answer:** "We monitored `/proc/meminfo` and specifically tracked the `AnonHugePages` counter. During the large-file 200-concurrency benchmark, we saw `AnonHugePages` grow to over 550MB. This proves the kernel daemon (`khugepaged`) was actively promoting anonymous memory buffers in the background, confirming our hypothesis."

**Q3. Why did you use a Virtual Machine instead of bare metal? Doesn't the hypervisor add noise?**
* **Answer:** "Yes, hypervisor scheduling can add variance, which we acknowledged in our 'Threats to Validity'. However, we controlled for this by running an idle host, executing repeated benchmark runs, and taking the arithmetic mean. Furthermore, VM deployments represent how most cloud-native Nginx servers actually run today, making our findings highly relevant to real-world cloud infrastructure."

**Q4. Nginx uses `epoll` and non-blocking I/O. Why would memory compaction affect its throughput?**
* **Answer:** "While `epoll` makes network I/O non-blocking, page faults are synchronous hardware exceptions. When an Nginx worker triggers a page fault that requires kernel-level memory compaction, that specific worker process is stalled by the kernel until the compaction completes. If all workers get stalled, throughput drops and latency spikes."

**Q5. I see that your Minor Faults match your Total Faults almost exactly. Why are there no Major Faults?**
* **Answer:** "Major faults require fetching data from the physical disk. Because we tested 5MB and 4KB files on a machine with 4GB of RAM, the files were heavily cached in the Linux Page Cache after the initial reads. Therefore, almost all faults were 'soft' or 'minor' faults—meaning the data was in memory, but the CPU's page tables just needed to be updated to map it to the process."

**Q6. If you had more time, what would you add to this research?**
* **Answer:** "We would use kernel tracing tools like `perf trace` or `eBPF` to track exactly how much time is spent inside the `khugepaged` daemon. We would also test THP under `madvise` mode to see if restricting huge pages only to specific applications resolves the compaction overhead."
