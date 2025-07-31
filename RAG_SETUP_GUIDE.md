# RAG Ingestion Tool Setup Guide

## 📋 Overview

This guide helps you set up and test the RAG (Retrieval-Augmented Generation) ingestion tool for your MCP File System project.

## 🔧 Setup Steps

### 1. Install Dependencies

```powershell
cd D:\STUFF\Projects\MCP_File_System
.\.venv\Scripts\activate
pip install chromadb nltk torch torchvision Pillow open-clip-torch
```

### 2. No API Keys Required! 

✅ **CLIP runs locally** - No API keys or internet connection needed for embeddings!

### 3. Test Installation

Run the quick test (no API key required):
```powershell
python quick_test.py
```

### 4. Run Full Tests

Run comprehensive tests (no API key required):
```powershell
python test_rag_driver.py
```

### 5. Test MCP Integration

Start the MCP server:
```powershell
uv run mcp_server.py
```

## 🛠️ Available MCP Tools

### 1. `get_path_to_file_based_on_parent_directory`
- **Purpose**: Find file paths
- **Input**: parent_directory, target_file
- **Output**: File path

### 2. `ingest_documents` (NEW)
- **Purpose**: Ingest documents into vector database
- **Input**: List of file paths
- **Output**: Success message with ingestion stats
- **Supported formats**: .txt, .md

## 📝 Usage Workflow

1. **Find Files**: Use `get_path_to_file_based_on_parent_directory` to locate files
2. **Ingest Documents**: Use `ingest_documents` with the file paths to vectorize content
3. **Vector DB**: Documents are stored in ChromaDB with 20-minute persistence

## 🗂️ Files Created/Modified

### New Files:
- `rag_helpers.py` - Core RAG functionality
- `test_rag_driver.py` - Comprehensive test suite  
- `quick_test.py` - Basic functionality test
- `RAG_SETUP_GUIDE.md` - This guide

### Modified Files:
- `mcp_server.py` - Added `ingest_documents` tool
- `pyproject.toml` - Added RAG dependencies

## 🧪 Testing Strategy

### Basic Test (No API):
```powershell
python quick_test.py
```

### Full Pipeline Test:
```powershell
python test_rag_driver.py
```

### MCP Integration Test:
1. Start MCP server: `uv run mcp_server.py`
2. Test in Claude Desktop with file paths

## 📊 Features

### Text Extraction:
- Supports .txt and .md files
- UTF-8 encoding with error handling
- File existence validation

### Chunking:
- Sentence-level chunking (4 sentences per chunk)
- Context preservation with overlap
- Handles empty chunks gracefully

### Vectorization:
- OpenCLIP ViT-B-32 model (open-source, local)
- Batch processing for efficiency
- Automatic CPU/GPU detection

### Storage:
- ChromaDB with persistent storage
- 20-minute session persistence
- Metadata preservation (file paths, timestamps)

## 🚨 Troubleshooting

### Import Errors:
```
pip install chromadb nltk torch torchvision Pillow open-clip-torch
```

### Model Loading Issues:
- First run downloads CLIP model (~340MB)
- Ensure stable internet for initial model download

### Permission Errors:
- Run PowerShell as Administrator
- Check file permissions

### ChromaDB Issues:
- Delete `./chroma_db` folder to reset
- Check disk space

## 💡 Next Steps

1. ✅ Test basic functionality
2. ✅ Test full pipeline
3. ✅ Test MCP integration
4. 🔄 **Build retrieval tool** (separate tool for querying)
5. 🔄 **Add more file formats** (PDF, DOCX, etc.)

## 📈 Performance Notes

- **Local**: No API calls or internet required after setup
- **Efficient**: Sentence-based chunking with batch processing
- **Persistent**: 20-minute vector DB sessions
- **Free**: No usage costs after initial setup

## 🔍 Example Usage

```python
# In Claude Desktop MCP client:
# 1. Find files
get_path_to_file_based_on_parent_directory("C:\\MyProject", "readme.md")

# 2. Ingest found files  
ingest_documents(["C:\\MyProject\\readme.md", "C:\\MyProject\\docs\\guide.txt"])
```