#!/bin/bash

MODE=$1
CONCURRENCY=$2
REQUESTS=$3
FILE=$4

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "Clearing page cache..."
sudo sync
echo 3 | sudo tee /proc/sys/vm/drop_caches

echo "Restarting nginx..."
sudo systemctl restart nginx

echo "Running perf system-wide during workload..."

sudo perf stat -a -e \
page-faults,minor-faults,major-faults,\
dTLB-load-misses,cache-misses,\
cycles,instructions,context-switches,cpu-migrations \
-o ../data/raw/perf_${FILE}_${MODE}_${CONCURRENCY}_${TIMESTAMP}.txt \
ab -n $REQUESTS -c $CONCURRENCY http://localhost/$FILE \
> ../data/raw/ab_${FILE}_${MODE}_${CONCURRENCY}_${TIMESTAMP}.txt

echo "Experiment completed."
