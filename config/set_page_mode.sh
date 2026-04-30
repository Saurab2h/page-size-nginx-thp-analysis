#!/bin/bash

MODE=$1

if [ "$MODE" == "4k" ]; then
    echo "Disabling Transparent Huge Pages..."
    echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
elif [ "$MODE" == "thp" ]; then
    echo "Enabling Transparent Huge Pages..."
    echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
else
    echo "Usage: ./set_page_mode.sh [4k|thp]"
    exit 1
fi

echo "Current THP status:"
cat /sys/kernel/mm/transparent_hugepage/enabled
