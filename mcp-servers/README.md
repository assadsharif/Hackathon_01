# MCP Servers

This directory contains Model Context Protocol (MCP) servers for the Physical AI & Humanoid Robotics project.

## Purpose

MCP servers enable LLMs to interact with external services through well-designed tools. Servers in this directory will provide specialized capabilities for:

- Physical AI research and development
- Robotics simulation integrations
- Data collection and processing
- Documentation and knowledge management
- Custom tools for the Docusaurus book site

## Development

To build MCP servers in this directory, use the **mcp-developer skill**:

```bash
# The skill is available at:
.claude/skills/mcp-developer/SKILL.md
```

The skill provides spec-driven development guidance for creating high-quality MCP servers using:
- **FastMCP** (Python)
- **MCP SDK** (@modelcontextprotocol/sdk - TypeScript/Node.js)

## Structure

Each MCP server should have its own subdirectory:

```
mcp-servers/
├── robotics-data-server/
│   ├── spec.md
│   ├── plan.md
│   ├── src/
│   └── README.md
├── physical-ai-docs-server/
│   └── ...
└── README.md (this file)
```

## Getting Started

1. Use the mcp-developer skill to guide development
2. Follow spec-driven development process (spec → plan → implement)
3. Test servers with Claude Code or other MCP clients
4. Document server capabilities in each server's README

## Related

- **Skill Guide**: `.claude/skills/mcp-developer/SKILL.md`
- **Project Constitution**: `.specify/memory/constitution.md`
- **MCP Protocol**: https://modelcontextprotocol.io
