#!/bin/sh

set -u

uvicorn app.main:app --host 0.0.0.0 --port 8000 &
server_pid=$!

cleanup() {
    kill "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
}

trap cleanup INT TERM

if ! python -m seeds.run_all; then
    cleanup
    exit 1
fi

wait "$server_pid"
