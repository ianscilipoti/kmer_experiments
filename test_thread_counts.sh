#!/usr/bin/env bash
# Sweep crocsort run-gen threads x merge threads.
#
# First, $warmupRuns warmup runs of crocsort with default settings (results
# not saved). Then, for each of $repetitionCount repetitions, run every
# (genThreads, mergeThreads) combination and append results to
# experiment_results/$experimentID. All other crocsort parameters stay at
# runner.py's defaults.
set -euo pipefail

# runner.py uses paths relative to the project root (./bin, ./input_data, ...).
cd "$(dirname "$0")"

warmupRuns=2
repetitionCount=5
experimentID="crocThreadCountTests.csv"

mergeThreadCounts=(16 20 24 28)
genThreadCounts=(12 14 16)

for ((w = 1; w <= warmupRuns; w++)); do
  echo "=== crocsort warmup $w/$warmupRuns ==="
  python3 runner.py crocsort
done

for ((rep = 1; rep <= repetitionCount; rep++)); do
  for genThreads in "${genThreadCounts[@]}"; do
    for mergeThreads in "${mergeThreadCounts[@]}"; do
      echo "=== crocsort rep $rep/$repetitionCount genThreads=$genThreads mergeThreads=$mergeThreads ==="
      python3 runner.py crocsort \
        --genThreads "$genThreads" \
        --mergeThreads "$mergeThreads" \
        --experimentID "$experimentID"
    done
  done
done
