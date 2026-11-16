import argparse
import csv
import shlex
import shutil
import subprocess
import time
from pathlib import Path

hash_size_bytes = 8
pos_size_bytes = 8

bin_path = Path("./bin")
hashes_file = "./input_data/3.hashes"
# In-place sorts run on a fresh copy of hashes_file, deleted after each run.
work_file = "./work.hashes"

resultsPath = Path("./experiment_results")

# Columns of the results CSV. Add new columns here and include them in the
# row dict passed to write_result.
# Tunable crocsort arguments, recorded alongside each result. Sorts that
# don't take these arguments write NA in these columns.
CROC_ARG_COLUMNS = ['genThreads', 'mergeThreads', 'fanIn', 'bufMb', 'partitionType']
RESULT_COLUMNS = ['runningTime (ms)'] + CROC_ARG_COLUMNS

SORT_ALGS = ['bsort', 'dtsort', 'ips2ra_sort', 'crocsort']
IN_PLACE_SORTS = {'bsort', 'dtsort', 'ips2ra_sort'}
CROC_PARTITION = ['key-only', 'count-balanced', 'size-balanced']


def sort(sortAlg, **kwargs):
    """Run sortAlg. In-place sorts operate on a temporary copy of hashes_file
    (so the original stays unsorted); the copy is deleted afterwards. The copy
    is not included in the measured running time."""
    if sortAlg not in IN_PLACE_SORTS:
        return _sort(sortAlg, hashes_file, **kwargs)
    shutil.copyfile(hashes_file, work_file)
    try:
        return _sort(sortAlg, work_file, **kwargs)
    finally:
        Path(work_file).unlink(missing_ok=True)


def _sort(sortAlg, inputFile, genThreads = 8, mergeThreads = 8, fanIn = 128, bufMb = 64, partitionType = 'size-balanced'):
    if sortAlg == 'bsort':
        cmd = [bin_path / 'bsort',
                "-k", str(hash_size_bytes),
                "-r", str(hash_size_bytes + pos_size_bytes),
                inputFile]
    elif sortAlg == 'dtsort':
        # not ooc, works best at 1/4 mem size, since it uses
        # double the size of data [so not really inplace?]. About
        # 2x faster than bsort on large sizes of data (8G) even
        # with 16/32x threads.

        cmd = [bin_path / 'dtsort',
                inputFile]
    elif sortAlg == 'ips2ra_sort':
        cmd = [bin_path / 'ips2ra_sort',
                inputFile]
    elif sortAlg == 'crocsort':
        outputFilePath = "./crocsort.hashes"
        cmd = [bin_path / 'crocsort_out',
                '-i', inputFile,
                '-o', outputFilePath,
                '-d', "./tmp",
                '--run-gen-threads', str(genThreads),
                '--merge-threads', str(mergeThreads),
                '--rg-buf-mb', str(bufMb),
                '--merge-fanin', str(fanIn),
                '--imbalance-factor', str(1),
                '--sparse-index-fraction', str(0.05),
                '--partition-type', partitionType,
                '--write-output', 'false'
                ]
    else:
        raise NotImplementedError(f"Unsupported sort {sortAlg}")

    runningTime = _run_cmd('sort', cmd)
    return runningTime


def write_result(experimentID, row):
    """Append one row to resultsPath / experimentID, creating it with a header if needed."""
    out = resultsPath / experimentID
    out.parent.mkdir(parents=True, exist_ok=True)
    is_new = not out.exists()
    with open(out, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_COLUMNS)
        if is_new:
            writer.writeheader()
        writer.writerow(row)


def _run_cmd(name, cmd, *args, **kwargs):
    print(f"Running {name}: ", shlex.join(str(s) for s in cmd))
    start = time.perf_counter_ns()
    kwargs.setdefault('stdout', subprocess.DEVNULL)
    kwargs.setdefault('stderr', subprocess.PIPE)
    try:
        subprocess.run(cmd, *args, check=True, **kwargs)
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(e.stderr.decode(errors='replace'))
        raise
    end = time.perf_counter_ns()
    print(f"Time (ms) for {name}: ", (end - start) / 1E6)
    return (end - start) / 1E6


def parse_args():
    p = argparse.ArgumentParser(description="Run a sort experiment.")
    p.add_argument('sortAlg', choices=SORT_ALGS, help="sort algorithm to run")
    p.add_argument('--genThreads', type=int, default=8, help="run generation threads (crocsort)")
    p.add_argument('--mergeThreads', type=int, default=8, help="merge threads (crocsort)")
    p.add_argument('--fanIn', type=int, default=128, help="merge fan-in (crocsort)")
    p.add_argument('--bufMb', type=int, default=64, help="run-gen buffer size in MB (crocsort)")
    p.add_argument('--partitionType', choices=CROC_PARTITION, default='size-balanced', help="partition type (crocsort)")
    p.add_argument('--experimentID', help="if given, append results to resultsPath/experimentID (CSV)")
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    runningTime = sort(args.sortAlg,
         genThreads=args.genThreads,
         mergeThreads=args.mergeThreads,
         fanIn=args.fanIn,
         bufMb=args.bufMb,
         partitionType=args.partitionType)
    if args.experimentID:
        row = {'runningTime (ms)': runningTime}
        for col in CROC_ARG_COLUMNS:
            row[col] = getattr(args, col) if args.sortAlg == 'crocsort' else 'NA'
        write_result(args.experimentID, row)
