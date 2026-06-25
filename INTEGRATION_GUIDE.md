# Third-Party AI Integration Guide

The Drunken-Agy repository is configured to be seamlessly compatible with various third-party AI coding agents. We employ a strict Jira and Confluence Single Source of Truth (SSOT) workflow, and we have pre-configured native files to force third-party agents to adhere to these rules automatically.

## Supported Agents & Native Configs

By simply cloning this repository, the following agents will automatically load their respective configuration files and adopt the project's SDLC:

### 1. Claude Code (CLI)
- **Native File:** `CLAUDE.md`
- **Behavior:** When you launch `claude` in the terminal, it reads `CLAUDE.md`. It learns that it must execute `python scripts/jira_bridge.py get-todo` to find tasks and use the bridge scripts to manage state.

### 2. Aider
- **Native File:** `CONVENTIONS.md`
- **Behavior:** Aider parses `CONVENTIONS.md` upon startup. It is instructed to strictly follow the branching and testing conventions, and to interface with Jira via the provided python scripts instead of guessing instructions.

### 3. Cursor IDE
- **Native File:** `.cursorrules`
- **Behavior:** The Cursor Agent and Chat features will respect `.cursorrules`, reminding the developer to use the Jira bridge for task management and the Confluence bridge for documentation syncs, preventing accidental direct edits to `main`.

## Manual Setup Requirements

For the agents to successfully execute the bridge scripts, you must provide the necessary Atlassian credentials in the environment.

1. Create a `.env` file at the root of the project:
```env
JIRA_URL="https://your-domain.atlassian.net"
JIRA_EMAIL="your_email@example.com"
JIRA_TOKEN="your_api_token"
JIRA_PROJECT_KEY="YOUR_KEY"
```
*(Note: `.env` is ignored by Git to protect your secrets).*

2. Ensure Python dependencies are installed:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Once configured, simply launch your preferred AI agent and watch it navigate the Jira and Confluence integrations effortlessly!
