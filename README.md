# An MCP Server to access RDF Portal
- To setup this server please follow the instructions [here](https://github.com/modelcontextprotocol/python-sdk).
- To utilize this server from Claude Desktop please follow the instructions [here](https://modelcontextprotocol.io/quickstart/user)  
An example configuration for this server is as follows:
```
      "ask_rdfportal": {
        "command": "/Users/awsome_user/.local/bin/uv",
        "args": [
          "--directory",
          "/Users/awsome_user/git/mcp-servers-for-rdfportal",
          "run",
          "server.py"
        ]
      }
```