#!/usr/bin/env python3
"""Check whether the first NUM_RECORDS records of a binary key/value file are sorted.

Records are packed as key,val,key,val,... with no header or padding.
Keys are compared as unsigned integers in the configured byte order.

Usage: python check_sorted.py <filepath>
"""

import sys

NUM_RECORDS = 1000      # how many records to check from the start of the file
KEY_SIZE = 8            # bytes per key
VALUE_SIZE = 8          # bytes per value
BYTE_ORDER = "little"   # "little" (LE) or "big" (BE)

RECORD_SIZE = KEY_SIZE + VALUE_SIZE


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <filepath>", file=sys.stderr)
        return 2

    path = sys.argv[1]
    with open(path, "rb") as f:
        data = f.read(NUM_RECORDS * RECORD_SIZE)

    n = len(data) // RECORD_SIZE
    if len(data) % RECORD_SIZE:
        print(f"warning: trailing {len(data) % RECORD_SIZE} bytes ignored (partial record)",
              file=sys.stderr)
    if n < NUM_RECORDS:
        print(f"note: file only has {n} records; checking all of them", file=sys.stderr)

    prev = None
    for i in range(n):
        off = i * RECORD_SIZE
        key = int.from_bytes(data[off:off + KEY_SIZE], BYTE_ORDER, signed=False)
        if prev is not None and key < prev:
            print(f"NOT SORTED: record {i} key {key:#x} < record {i - 1} key {prev:#x}")
            return 1
        prev = key

    print(f"SORTED: first {n} records are in non-decreasing key order")
    return 0


if __name__ == "__main__":
    sys.exit(main())
