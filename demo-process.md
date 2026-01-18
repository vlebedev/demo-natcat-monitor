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

## What's in demo-files-ready

- `CLAUDE.md` — Agent coordination instructions with role mapping
- `functional-spec.md` — Requirements and user stories
- `tech-spec.md` — Technology stack and coding standards
- `.beads/` — Beads configuration (empty task database)

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
