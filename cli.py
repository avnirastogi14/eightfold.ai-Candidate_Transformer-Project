from __future__ import annotations
import argparse
import json
import sys

from transformer.pipeline import run


def main():
    parser = argparse.ArgumentParser( description="Multi-Source Candidate Data Transformer")
    parser.add_argument("--inputs", nargs="+", required=True, help="Input files / URLs",)
    parser.add_argument("--config", default=None, help="Custom config JSON",)
    parser.add_argument("--out", default=None, help="Output file",)
    args = parser.parse_args()

    cfg = {}
    if args.config:
        with open(args.config) as fh:
            cfg = json.load(fh)

    res = run(args.inputs, cfg)
    txt = json.dumps(res, indent=2, default=str)

    if args.out:
        with open(args.out, "w") as fh:
            fh.write(txt)
        print(f"Wrote {len(res['records'])} record(s) to {args.out}", file=sys.stderr)
    else:
        print(txt)

    # validation errors if any
    if res["errors"]:
        print(f"\n[validation] {len(res['errors'])} record(s) had issues",file=sys.stderr,)
        sys.exit(1)

if __name__ == "__main__":
    main()