#!/usr/bin/env bash
#
# reset-demo.sh - Reset demo-natcat-monitor to clean slate
#
# This script properly cleans up all demo artifacts and resets beads
# to an empty state, ready for a fresh multi-agent demo run.
#
# Usage: ./scripts/reset-demo.sh [--push]
#   --push    Also force-push to origin/main after reset

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

DO_PUSH=false
if [[ "${1:-}" == "--push" ]]; then
    DO_PUSH=true
fi

cd "$PROJECT_DIR"
log_info "Working in: $PROJECT_DIR"

# =============================================================================
# Step 1: Stop beads daemon
# =============================================================================
log_info "Stopping beads daemon..."
if bd daemon stop 2>/dev/null; then
    log_success "Beads daemon stopped"
else
    log_warn "Beads daemon was not running (or stop failed)"
fi
sleep 1

# =============================================================================
# Step 2: Clean up generated demo artifacts
# =============================================================================
log_info "Cleaning up generated demo artifacts..."

# Remove Python artifacts
rm -rf .venv .pytest_cache __pycache__ .mypy_cache .ruff_cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Remove generated source code directories (created during demo)
rm -rf src/ tests/ data/

# Remove generated config files
rm -f requirements.txt README.md

# Remove any .bv local config/cache
rm -rf .bv/

log_success "Cleaned up demo artifacts"

# =============================================================================
# Step 3: Reset beads database
# =============================================================================
log_info "Resetting beads database..."

# Remove SQLite database and related files
rm -f .beads/beads.db .beads/beads.db-shm .beads/beads.db-wal
rm -f .beads/daemon.log .beads/daemon.pid .beads/daemon.lock
rm -f .beads/bd.sock .beads/.sync.lock .beads/.local_version
rm -f .beads/last-touched .beads/sync-state.json

# Truncate issues.jsonl to empty (keep the file for git tracking)
: > .beads/issues.jsonl

log_success "Beads database files removed"

# =============================================================================
# Step 4: Reinitialize beads from empty JSONL
# =============================================================================
log_info "Reinitializing beads from empty JSONL..."

# --from-jsonl prevents importing from git history
bd init --from-jsonl --quiet

log_success "Beads reinitialized with empty database"

# =============================================================================
# Step 5: Verify beads state
# =============================================================================
log_info "Verifying beads state..."

ISSUE_COUNT=$(bd list --status=all --json 2>/dev/null | jq 'length' 2>/dev/null || echo "error")
if [[ "$ISSUE_COUNT" == "0" ]]; then
    log_success "Beads database is empty (0 issues)"
else
    log_error "Beads database has $ISSUE_COUNT issues - expected 0!"
    exit 1
fi

# =============================================================================
# Step 6: Prime bv for demo (export initial state)
# =============================================================================
log_info "Priming bv for demo..."

# Generate initial triage data so bv works immediately
# This creates the internal caches/indices that bv needs
bv -robot-triage > /dev/null 2>&1 || true

log_success "bv primed and ready"

# =============================================================================
# Step 7: Git cleanup
# =============================================================================
log_info "Cleaning untracked files..."

# Remove untracked files, but exclude scripts/ to preserve this script
git clean -fd --exclude=scripts/

log_success "Git cleaned"

# =============================================================================
# Step 8: Commit and push (optional)
# =============================================================================
if [[ "$DO_PUSH" == "true" ]]; then
    log_info "Syncing and pushing to origin/main..."

    # Sync beads changes (commits the empty issues.jsonl)
    bd sync --no-push --quiet 2>/dev/null || true

    # Force push to reset remote to our clean state
    if git push --force origin main; then
        log_success "Pushed to origin/main"
    else
        log_error "Failed to push - you may need to resolve manually"
        exit 1
    fi
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Demo Reset Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Status:"
echo "  - Demo artifacts: cleaned"
echo "  - Beads database: empty (0 issues)"
echo "  - bv: primed and ready"
if [[ "$DO_PUSH" == "true" ]]; then
    echo "  - Remote: force-pushed to origin/main"
else
    echo "  - Remote: NOT pushed (run with --push to push)"
fi
echo ""
echo "Next steps:"
echo "  1. Start agents: ntm spawn natcat --cc=3"
echo "  2. Monitor: ntm (TUI) or bv"
echo ""
