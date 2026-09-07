#!/usr/bin/env bash

set -euo pipefail

MODE="${1:-}"
OPTION="${2:-}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

log() {
  printf '\n[Inhealth] %s\n' "$1"
}

fail() {
  printf '\n[Inhealth] ERROR: %s\n' "$1" >&2
  exit 1
}

show_help() {
  cat <<'EOF'
Inhealth setup

Usage:
  ./setup.sh local [--init-db]
  ./setup.sh vm [--init-db]

local       Create/update .venv and install frontend dependencies.
vm          Create/update the VM environment and install systemd units.
--init-db   Apply database/schema.sql. Seed data is never loaded.

Run commands are documented in README.md. This script prepares the environment;
it does not start local development servers.
EOF
}

validate_arguments() {
  [[ "$MODE" == "local" || "$MODE" == "vm" ]] || {
    show_help
    exit 1
  }
  [[ -z "$OPTION" || "$OPTION" == "--init-db" ]] || \
    fail "Unknown option: $OPTION"
}

load_env() {
  if [[ ! -f .env ]]; then
    cp .env.example .env
    fail "Created .env. Set DB_PASSWORD, then run this command again."
  fi

  set -a
  # shellcheck disable=SC1091
  source .env
  set +a

  [[ -n "${DB_USER:-}" ]] || fail "DB_USER is missing from .env"
  [[ -n "${DB_NAME:-}" ]] || fail "DB_NAME is missing from .env"
}

find_python() {
  if command -v python3 >/dev/null 2>&1; then
    printf '%s' python3
  elif command -v python >/dev/null 2>&1; then
    printf '%s' python
  else
    fail "Python is not installed."
  fi
}

setup_python() {
  local venv_path="$1"
  local system_python
  local venv_python="$venv_path/bin/python"
  system_python="$(find_python)"

  if [[ ! -d "$venv_path" ]]; then
    log "Creating Python environment: $venv_path"
    "$system_python" -m venv "$venv_path"
  fi

  # A Windows environment uses Scripts instead of bin.
  if [[ ! -x "$venv_python" && -x "$venv_path/Scripts/python.exe" ]]; then
    venv_python="$venv_path/Scripts/python.exe"
  fi
  [[ -x "$venv_python" ]] || fail "Python environment is incomplete: $venv_path"

  log "Installing Python dependencies"
  "$venv_python" -m pip install -r requirements.txt
}

setup_frontend() {
  command -v pnpm >/dev/null 2>&1 || \
    fail "pnpm is not installed. Install Node.js and pnpm first."

  log "Installing frontend dependencies"
  pnpm --dir frontend install
}

initialize_database() {
  [[ "$OPTION" == "--init-db" ]] || return 0
  command -v mysql >/dev/null 2>&1 || \
    fail "MariaDB/MySQL client is required for --init-db."

  log "Applying database schema; sensor seed data is not loaded"
  mysql \
    --host="${DB_HOST:-127.0.0.1}" \
    --port="${DB_PORT:-3306}" \
    --user="$DB_USER" \
    -p < database/schema.sql
}

setup_local() {
  log "Preparing local development environment"
  setup_python ".venv"
  setup_frontend
  initialize_database

  cat <<'EOF'

Local setup complete.

Backend:
  .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000

Frontend (separate terminal):
  pnpm --dir frontend dev

API docs:
  http://127.0.0.1:8000/docs
EOF
}

setup_vm() {
  [[ "$(uname -s)" == "Linux" ]] || \
    fail "VM mode must run inside the Debian/Linux edge VM."
  [[ -d frontend/dist ]] || \
    fail "frontend/dist is missing. Build and copy the Vue production files first."

  log "Preparing edge VM"
  local vm_root
  local vm_venv
  vm_root="$(dirname "$PROJECT_ROOT")"
  vm_venv="$vm_root/venv"

  setup_python "$vm_venv"
  initialize_database

  log "Installing systemd service files"
  sudo install -m 0644 deploy/inhealth-backend.service \
    /etc/systemd/system/inhealth-backend.service
  sudo install -m 0644 deploy/inhealth-edge.service \
    /etc/systemd/system/inhealth-edge.service

  log "Starting MariaDB and Inhealth services"
  sudo systemctl enable --now mariadb
  sudo systemctl daemon-reload
  sudo systemctl enable --now inhealth-backend inhealth-edge
  sudo systemctl restart inhealth-backend inhealth-edge

  sudo systemctl --no-pager --full status \
    inhealth-backend inhealth-edge || true

  cat <<'EOF'

VM setup complete.

Follow the edge log:
  sudo journalctl -u inhealth-edge -n 40 -f

Show the VM address:
  hostname -I

Open:
  http://<VM-IP>:8000
EOF
}

validate_arguments
load_env

case "$MODE" in
  local) setup_local ;;
  vm) setup_vm ;;
esac
