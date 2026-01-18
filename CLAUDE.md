# CLAUDE.md — NatCat Event Monitor

## Project Documentation

Read these files before starting work:

- `tech-spec.md` — Technology stack, coding standards, testing approach, interface contracts
- `functional-spec.md` — Requirements, user stories, acceptance criteria
- `AGENTS.md` — Additional agent instructions including beads usage (if exists)

## Your Identity

Run this command to determine your agent ID:
```bash
/usr/bin/tmux display-message -p '#{pane_title}'
```

Parse the suffix (e.g., `natcat__cc_1` → `cc_1`) and look up your role:

| Agent ID | Role        |
|----------|-------------|
| `cc_1`   | LeadDev     |
| `cc_2`   | DataDev     |
| `cc_3`   | UIDev       |

Agent Mail will assign you a unique name (e.g., BlueHill, GreenCastle). Always use Agent Mail names when addressing other agents, not roles.

## Roles

| Role        | Responsibility                                 |
|-------------|------------------------------------------------|
| **LeadDev** | Creates plan, assigns tasks, implements domain |
| **DataDev** | USGS API client, mock treaty data              |
| **UIDev**   | Streamlit interface                            |

## Startup Sequence

1. Ensure project exists in Agent Mail
2. Register with Agent Mail (you will receive an assigned name)
3. Pause 30 seconds to wait other agents to register and ask user to tell you when you can proceed
4. Check registered agents using Agent Mail resource system (see "Agent Discovery" below)
5. If you see less than 2 other agents registered, wait 30 seconds more and go to step 4.
6. Send introduction to all other agents (see "Introduction Protocol" below)
7. Pause 30 seconds to wait other agents to introduce themselves 
8. Check the introductions thread to learn who has which role
9. Check your inbox for task assignments
10. Acknowledge messages that require acknowledgment

## Introduction Protocol

After registering in Agent Mail, introduce yourself to all other agents by sending message to all other agents (discovered via Agent Discovery below) with subject="Introduction: I am <your role>", body_md="I am <your assigned name>, role **<your role>**.", and thread_id="introductions".

Check the "introductions" thread to learn the name-to-role mapping for all agents.

## Agent Discovery

To discover all agents registered in the project, use the MCP resource system:

```
ReadMcpResourceTool with:
- server: "mcp-agent-mail"
- uri: "resource://agents/{project_key}"
```

Where `{project_key}` is the absolute path to your working directory (e.g., `/data/projects/demo-natcat-monitor`).

This returns a list of all registered agents with their names and details. Use the agent names from this list when sending messages via Agent Mail.

## LeadDev: First Steps

If your role is **LeadDev**:
1. Read the spec and constitution
2. Create epic and tasks in beads based on the requirements. Use ultrathink for this work.
3. Wait for other agents to introduce themselves so you know their names
4. Send task assignments via Agent Mail using their Agent Mail names
5. Begin your own implementation work

## All Roles, other than LeadDev: First Steps

If your role is **DataDev** or **UIDev***
1. Read the spec and constitution
2. Wait for other agents to introduce themselves so you know their names
3. Wait for task assignments from LeadDev via Agent Mail
4. Begin your implementation work

## Landing the Plane (Session Completion)

**When I say "Let's land the plane"**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
