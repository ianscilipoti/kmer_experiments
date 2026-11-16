#!/usr/bin/env bash
# Run every sort supported by runner.py, repeatedly.
#
# The first $warmupRuns iterations are warmups: they run each sort but do not
# pass --experimentID, so no results are saved. The following $repetitions
# iterations save results to experiment_data/<sortAlg>.csv.
set -euo pipefail

# runner.py uses paths relative to the project root (./bin, ./3.hashes, ...).
cd "$(dirname "$0")"

warmupRuns=1
repetitions=5

sorts=(bsort dtsort ips2ra_sort crocsort)

totalRuns=$((repetitions + warmupRuns))

for ((i = 0; i < totalRuns; i++)); do
  for sortAlg in "${sorts[@]}"; do
    if ((i < warmupRuns)); then
      echo "=== $sortAlg (warmup $((i + 1))/$warmupRuns) ==="
      python3 runner.py "$sortAlg"
    else
      echo "=== $sortAlg (repetition $((i - warmupRuns + 1))/$repetitions) ==="
      python3 runner.py "$sortAlg" --experimentID "$sortAlg.csv"
    fi
  done
done
