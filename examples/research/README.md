# Swarm Research

#TODO: Handoff between planner and researcher

## Quickstart
```
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev
```

## Search Tools 
 
### Playwright Browser Tool

[Playwright](https://playwright.dev/) offers several advantages over API-based solutions:

  1. Full browser access - can interact with entire websites, not just search results
  2. Can navigate complex pages, fill forms, click buttons like a human user
  3. Handles JavaScript-rendered content that APIs can't access
  4. Maintains session state across multiple interactions
  5. Better evades anti-scraping measures by mimicking legitimate browser traffic
  6. Can extract specific data elements from pages with precision
  7. Works well for research requiring deep site exploration

## Troubleshooting

### Playwright MCP Server

Some issues with the Playwright MCP Server are related to the npx cache. 

Clear the npx cache:
```
rm -rf ~/.npm/_npx/9833c18b2d85bc59
```

Create a minimal package.json:
```
cat > package.json << EOF
{
  "name": "zod-fix",
  "private": true,
  "dependencies": {
    "zod": "3.22.4",
    "@playwright/mcp": "latest"
  }
}
EOF
```
Install the dependencies:
```
npm install
```

Create the MCP server:
```
npx @playwright/mcp
mkdir -p ./node_modules/zod/lib/locales
echo 'export const errorMap = () => ({ message: "" });' > ./node_modules/zod/lib/locales/en.js
``` 

Run server in isolation, which will use `stdio` transport:
```
npx @playwright/mcp
```

Test with MCP inspector:
```
npx @modelcontextprotocol/inspector
```

Supply the path to npx directly in your MCP configuration: 
```
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp"],
    }
  }
}
```

