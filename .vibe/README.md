# Vibe Project Configuration

This directory contains Vibe-specific configuration for the timekpr-app project.

## Structure

```
.vibe/
├── config.toml          # Project-specific Vibe configuration
├── agents/              # Agent definitions (TOML format)
│   ├── scrum_master.toml
│   ├── devops.toml
│   ├── fullstack.toml
│   ├── security.toml
│   ├── qa.toml
│   └── ux.toml
└── README.md           # This file
```

## Agents

The project uses 6 role-based agents:

| Agent | Role | Prefix | Description |
|-------|------|--------|-------------|
| scrum_master | Scrum Master | [Scrum Master] | Team coordination, Linear management |
| devops | DevOps | [DevOps] | Infrastructure, CI/CD, environment |
| fullstack | Fullstack Developer | [Fullstack] | Backend & frontend implementation |
| security | Security Specialist | [Security] | Security analysis, OWASP |
| qa | QA Engineer | [QA] | Testing, automation |
| ux | UX Designer | [UX] | Design, accessibility |

### Usage

Switch between agents during a session:
```
/agent scrum_master    # Become Scrum Master
/agent devops         # Switch to DevOps
/agent security       # Switch to Security
... etc
```

## MCP Servers

The following MCP servers are configured:
- **linear**: For Linear issue management (via `linear_*` tools)

Configured via:
```bash
vibe mcp add linear --url https://mcp.linear.app/mcp --transport streamable-http --api-key-env LINEAR_API_KEY
```

Available Linear tools:
- `linear_list_issues` - List all issues
- `linear_get_issue` - Get issue details
- `linear_update_issue` - Update issue state/comment
- `linear_create_comment` - Add comment to issue
- ... and more

## Going Back to Generic Setup

If you want to return to the generic multi-AI setup (Copilot, Ollama, etc.):

### Option 1: Disable Vibe Configuration
1. Move this directory: `mv .vibe .vibe_disabled`
2. Remove MCP server: `vibe mcp remove linear`
3. Continue using `.prompts/` files as before

### Option 2: Use Both (Hybrid)
- Keep `.vibe/agents/` for Vibe optimization
- Keep `.prompts/` for documentation (works with all AI tools)
- MCP servers will only be used by Vibe

### Option 3: Full Reset
1. Delete `.vibe/` directory
2. Remove MCP servers: `vibe mcp remove linear`
3. Revert to manual prefix switching in `.prompts/`

## Benefits of Native Vibe Setup

✅ **Faster workflow**: Instant agent switching with `/agent`
✅ **Better integration**: Native MCP tools for Linear
✅ **Context preservation**: Vibe remembers context between agents
✅ **Immediate updates**: Each agent updates Linear immediately
✅ **Less manual work**: No custom scripts needed

## Trade-offs

⚖️ **Vendor lock-in**: Primarily optimized for Vibe
⚖️ **Learning curve**: Need to learn Vibe's agent system
⚖️ **Configuration**: Requires MCP and agent setup

## Migration Notes

- `.prompts/` files are still available for reference
- All documentation in `.prompts/` remains universally compatible
- Linear MCP uses `LINEAR_API_KEY` from `.env.agent`
- Git operations use native `bash` tools (already in allowlist)
