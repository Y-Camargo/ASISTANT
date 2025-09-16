from __future__ import annotations
import argparse, time, sys, requests

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--interval", type=float, default=1.5)
    args = ap.parse_args()
    deadline = time.time() + args.timeout
    last_err = None
    while time.time() < deadline:
        try:
            r = requests.get(args.url, timeout=5)
            if 200 <= r.status_code < 300:
                print(f"OK {args.url} -> {r.status_code}")
                return
            last_err = f"status {r.status_code}"
        except Exception as e:
            last_err = str(e)
        time.sleep(args.interval)
    print(f"Timeout esperando {args.url}: {last_err}", file=sys.stderr)
    sys.exit(1)
if __name__ == "__main__":
    main()