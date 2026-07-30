# 🤖 AI AGENT INSTRUCTIONS FOR `whisper_dictation`

> **CRITICAL DIRECTIVE:** All AI agents (Antigravity, Cursor, Claude, Copilot) MUST read and strictly adhere to these instructions before modifying any files in this repository.

## 1. 🛑 Initialization Protocol (DO THIS FIRST)
1. **Read the Docs:** Read `README.md` (and `INFRASTRUCTURE_POLICY.md` if present) to understand the tech stack, deployment target, and architecture of this specific project.
2. **Check Git Status:** Run `git status` to check if the user has uncommitted manual changes. **NEVER** overwrite or stash the user's uncommitted work without their explicit permission.
3. **Verify Context:** Check `package.json` or `requirements.txt` to confirm the environment before running installation commands.

## 2. 💻 Coding Standards
- **Respect Existing Code:** Follow the existing project code style (e.g., PEP8, ESLint). Do NOT reformat the entire file just to fix one line.
- **Preserve Documentation:** Do NOT delete existing comments, docstrings, or type hints unless instructed by the user or unless they are factually incorrect due to your code changes.
- **Dependencies:** Do NOT add heavy third-party libraries (e.g., Pandas, heavy UI frameworks) without asking the user, unless it's the standard solution for the requested task.

## 3. 🚀 Deployment Protocol
- **Target:** Local Execution / Standalone scripts.
- **Method:** Run locally via `python` or `npm start`. If the project has a `docker-compose.yml`, use `docker-compose up -d`.

## 4. ✅ Testing & Verification
- After writing code or executing a command, **VERIFY** that it worked.
- Write a quick test script, run a `curl` check, or use `ping` to ensure services are alive before telling the user the task is completed.
- If you encounter an error, **DO NOT GIVE UP**. Read the error logs carefully and fix the issue.

---
*Generated centrally by Master Infrastructure Policy on 2026-07-30.*
