"""Optional maintenance check against an original pinned Parquet download.

Not needed for participant lessons. Requires separately installed pyarrow.
Usage: python3 -m scripts.verify_upstream /path/to/file.parquet
This script never downloads anything.
"""

import argparse
import hashlib
import json
from pathlib import Path

from routing_workshop.backends import read_data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parquet", type=Path)
    args = parser.parse_args()

    manifest = read_data("recorded_manifest.json")
    actual_hash = hashlib.sha256(args.parquet.read_bytes()).hexdigest()
    if actual_hash != manifest["upstream_sha256"]:
        parser.error("upstream file hash differs from pinned original")

    try:
        import pyarrow.parquet as parquet
    except ImportError:
        parser.error("Optional maintainer check requires pyarrow; core commands do not.")

    upstream_rows = parquet.read_table(args.parquet).to_pylist()
    selected_rows = read_data("recorded_source_rows.json")
    for row in selected_rows:
        expected = {
            key: value for key, value in row.items() if key != "source_row_index"
        }
        if upstream_rows[row["source_row_index"]] != expected:
            parser.error("source row differs from original Parquet")

    print(json.dumps({
        "original_sha256_verified": True,
        "selected_rows_equal_original": len(selected_rows),
    }, indent=2))


if __name__ == "__main__":
    main()
