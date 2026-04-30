# Page Size Nginx Project

This project evaluates the performance implications of Linux Transparent Huge Pages (THP) on Nginx static web workloads under varying request concurrency.

## Experimental Variables
- Memory Modes: Standard 4K Paging vs Transparent Huge Pages
- Workloads: Small static file (4KB), Large static file (5MB)
- Concurrency Levels: 50, 200, 400
- Metrics: Throughput, Latency, Page Faults, Context Switches

## Tools Used
- Nginx
- Apache Benchmark (ab)
- Linux perf
- Python data analysis scripts
- IEEE LaTeX paper generation

## Repository Structure
- scripts/ : automation benchmark scripts
- data/raw/ : raw ApacheBench and perf logs
- analysis/ : CSV extraction, averaging, plotting scripts
- paper/ : IEEE research paper source

## Authors
- Saurabh Pandey
- Poojan Pandya
