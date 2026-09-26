"""CLI: purge old parquet run artifacts and archive meta_runs rows."""

from __future__ import annotations

import argparse
import logging
import sys

from quant import config
from quant.data.cleanup import cleanup_old_artifacts
from quant.logging_setup import configure_logging

logger = logging.getLogger(__name__)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Purge parquet artifacts older than N days and archive runs.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Archive runs finished more than this many days ago (default: 30)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report actions without deleting files or updating the database",
    )
    return parser


def main() -> None:
    configure_logging()
    args = build_arg_parser().parse_args()

    result = cleanup_old_artifacts(
        runs_db_path=config.runs_db_path(),
        artifacts_dir=config.artifacts_dir(),
        older_than_days=args.days,
        dry_run=args.dry_run,
    )

    freed_mb = result.bytes_freed / (1024 * 1024)
    print(  # noqa: T201
        f"scanned={result.runs_scanned} archived={result.runs_archived} "
        f"deleted={result.dirs_deleted} freed={freed_mb:.2f} MB "
        f"(dry_run={args.dry_run})",
    )

    if result.errors:
        for err in result.errors:
            print(err, file=sys.stderr)  # noqa: T201
        sys.exit(1)


if __name__ == "__main__":
    main()
