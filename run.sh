#!/usr/bin/env bash
# Sobe a aplicação em modo desenvolvimento.
set -e
cd "$(dirname "$0")"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
