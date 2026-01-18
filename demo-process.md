# Demo Process

This document describes how to reset the project to a clean state for running the multi-agent demo.

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Active development |
| `demo-files-ready` | Clean state with specs only, no generated code |

## Resetting for a New Demo Run

To reset the project to the initial state (specs defined, no source code):

```bash
cd /data/projects/demo-natcat-monitor

# Discard all local changes and untracked files
git checkout demo-files-ready
git clean -fd

# Optionally, reset main to this state
git branch -D main
git checkout -b main
git push --force origin main
```

## Quick Reset (keep on main)

If you just want to reset `main` to the demo-ready state without switching branches:

```bash
cd /data/projects/demo-natcat-monitor

# Hard reset main to demo-files-ready
git reset --hard demo-files-ready
git clean -fd
```

## Beads Database Cleanup

The beads issue tracker can accumulate leftover demo data that interferes with fresh agent sessions. Here's how to ensure a completely clean slate:

### Problem
- Beads imports issues from git history during `bd init`
- Old demo sessions leave behind closed issues and tombstones
- Agents see leftover tasks instead of starting fresh

### Solution: Clean Slate Process

```bash
cd /data/projects/demo-natcat-monitor

# 1. Remove all beads data from git tracking
git rm -rf .beads

# 2. Remove local beads directory
rm -rf .beads

# 3. Commit the removal
git commit -m "Remove beads database for clean demo state"

# 4. Initialize with empty database (prevents git history import)
mkdir -p .beads
touch .beads/issues.jsonl
bd init --from-jsonl

# 5. Commit clean initialization
git add .beads/ .gitattributes .gitignore
git commit -m "Initialize clean beads database for demo sessions"

# 6. Push to both branches
git push origin main
git checkout demo-files-ready
git cherry-pick HEAD~1 HEAD  # Apply both commits
git push origin demo-files-ready
```

### Verification

Check that beads database is completely empty:

```bash
# Should return empty array []
bd list --status=all --json

# Should show issue_count: 0
bv --robot-triage | jq '.triage.meta.issue_count'
```

### Why `--from-jsonl` is Required

- `bd init` normally imports all issues from git history
- Using `--from-jsonl` with an empty issues.jsonl file bypasses git history import
- This ensures no leftover demo data is resurrected during initialization

## What's in demo-files-ready

- `CLAUDE.md` — Agent coordination instructions with role mapping
- `functional-spec.md` — Requirements and user stories
- `tech-spec.md` — Technology stack and coding standards
- `.beads/` — Beads configuration (clean, empty task database)

## Running the Demo

1. Reset to clean state (see above)
2. Start agents: `ntm spawn natcat --cc=3`
3. Agents will:
   - Identify their roles via tmux pane title (cc_1=LeadDev, cc_2=DataDev, cc_3=UIDev)
   - Register with Agent Mail
   - Introduce themselves
   - LeadDev creates tasks, assigns work
   - DataDev and UIDev implement their parts
4. Monitor progress via `ntm` TUI or Agent Mail inbox
