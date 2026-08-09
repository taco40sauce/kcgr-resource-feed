#!/bin/bash
set -euo pipefail

cd "$HOME/kcgr-pipeline"

POLL_INTERVAL_SECONDS="${POLL_INTERVAL_SECONDS:-900}"

echo "$(date -Iseconds) kcgr-pipeline starting, polling every ${POLL_INTERVAL_SECONDS}s"

while true; do
    echo "$(date -Iseconds) --- run start ---"

    if python3 run_cycle.py; then
        echo "$(date -Iseconds) run complete"
    else
        echo "$(date -Iseconds) run_cycle.py failed this cycle — will retry next interval"
    fi

    sleep "$POLL_INTERVAL_SECONDS"
done
