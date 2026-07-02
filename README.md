# Universal VibeT Search MCP

**Free multi-engine web search MCP server — no API keys required.**

Built with [FastMCP](https://github.com/jlowin/fastmcp) and [ddgs](https://github.com/deedy5/ddgs).

> **Acknowledgment:** The multi-engine search logic is based on the `web_search` tool from [Vibe-Trading](https://github.com/HKUDS/Vibe-Trading) (MIT License) — an open-source AI trading research workspace by [HKUDS](https://github.com/HKUDS).

## Features

- **Zero API keys** — queries DuckDuckGo, Google, Bing, Brave, Mojeek, Yahoo directly
- **Retry with backoff** — 3 attempts with exponential backoff for transient failures
- **News search** — dedicated tool for recent news results
- **Lightweight** — single file, minimal dependencies

## Quick Start

### Install

```bash
pip install universal-vibet-search-mcp
```

Or from source:

```bash
git clone https://github.com/hdworker/universal-vibet-search-mcp.git
cd universal-vibet-search-mcp
pip install -e .
```

### Run as MCP Server

```bash
universal-vibet-search-mcp
```

Or directly:

```bash
python -m src.server
```

### Add to Claude Desktop / OpenCode / Cursor

Add to your MCP config:

```json
{
  "mcpServers": {
    "web-search": {
      "command": "universal-vibet-search-mcp",
      "transport": "stdio"
    }
  }
}
```

Or with Python module:

```json
{
  "mcpServers": {
    "web-search": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/universal-vibet-search-mcp",
      "transport": "stdio"
    }
  }
}
```

## Tools

### `web_search`

Search the web across free engines.

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `query` | string | required | Search query |
| `max_results` | int | 5 | Max results (1-10) |

**Returns:** JSON with `status`, `query`, and `results` array.

### `web_search_news`

Search recent news across free engines.

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `query` | string | required | News search query |
| `max_results` | int | 5 | Max results (1-10) |

**Returns:** JSON with `status`, `query`, and `results` array (includes `date` and `source`).

## Example Output

```
User query
    │
    ▼
┌─────────────────────────────────────────┐
│  ddgs (DuckDuckGo Search library)       │
│                                         │
│  Queries multiple search engines        │
│  (DuckDuckGo, Google, Bing, etc.)       │
│                                         │
│  If rate-limited → retry (3x)           │
│  If transient error → exponential backoff
└─────────────────────────────────────────┘
    │
    ▼
  JSON results
```

The `ddgs` library is a metasearch aggregator that queries multiple search engines without requiring API keys. It works by scraping public search results pages.

## Example Output

```json
{
  "status": "ok",
  "query": "Python MCP server tutorial",
  "results": [
    {
      "title": "Building an MCP Server with FastMCP",
      "url": "https://example.com/fastmcp-tutorial",
      "snippet": "Learn how to build a Model Context Protocol server..."
    }
  ]
}
```

## Limitations

- **Rate limits** — Free engines rate-limit aggressively from cloud/shared IPs (~100 req/hour per engine). The multi-engine fallback mitigates this.
- **No guaranteed uptime** — Engines may change their scraping targets.
- **CAPTCHA** — Occasionally engines may present CAPTCHAs; the retry logic handles most transient cases.

## Credits

- **[Vibe-Trading](https://github.com/HKUDS/Vibe-Trading)** (MIT License) — Original multi-engine search implementation by [HKUDS](https://github.com/HKUDS) at HKU
- **[ddgs](https://github.com/deedy5/ddgs)** — DuckDuckGo Search library
- **[FastMCP](https://github.com/jlowin/fastmcp)** — FastMCP framework for building MCP servers

## License

MIT License — see [LICENSE](LICENSE) for details.
