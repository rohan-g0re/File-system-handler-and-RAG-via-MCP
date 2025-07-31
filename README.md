<div align="center">

# MCP File System

**RAG over local files without uploading stuff anywhere**  
**Just give ROUGH direction of file location**

*An MCP (Model Context Protocol) server for intelligent file search  and semantic document retrieval*

![Python](https://img.shields.io/badge/python-3.11+-ff6b6b.svg?style=flat-square)
![MCP](https://img.shields.io/badge/MCP-compatible-4ecdc4.svg?style=flat-square)
![ChromaDB](https://img.shields.io/badge/ChromaDB-vector%20storage-45b7d1.svg?style=flat-square)

</div>

## This is what we do!

**Recursive directory traversal** so the user does not need to specify exact file paths. Just tell me the parent directory and we will find it.

**RAG document ingest and retrieval**  on all your local files - separated across directories and disks - to answer your intuitive queries.

## Architecture

```
mcp_server.py           # main mcp server with 3 tools
├── tool_helpers/
│   ├── file_search_helpers.py      # file system operations  
│   ├── rag_ingest_helpers.py       # document processing pipeline
│   └── rag_retrieval_helpers.py    # vector search & retrieval
└── chroma_db/          # persistent vector storage
```

## Quick start

#### *Installation*
```bash
git clone <repository>
cd MCP_File_System

# Setup uv for faster processing
uv init
uv venv
.\.venv\Scripts\activate

uv add "mcp[cli]" httpx chromadb open-clip-torch torch torchvision nltk Pillow

```

#### *Claude Desktop Integration*

```json
{
  "mcpServers": {
    "mcp_file_system": {
      "command": "uv",
      "args": ["--directory",
      "/path/to/MCP_File_System",
      "run",
      "mcp_server.py"
      ]
    }
  }
}
```

## Tech Recipe

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Server** | FastMCP | mcp protocol implementation |
| **Embeddings** | openai clip | easy and free init |
| **storage** | chromadb | vector database |

#### *Supported formats*

- ✅ **text files** (.txt)
- ✅ **markdown** (.md)  
- ⏳ *PDF functionality coming soon*

<br>

<div align="center">

**built for the busy people with doc heavy work**

*local processing • persistent storage*

</div>