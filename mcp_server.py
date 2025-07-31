from typing import Any, List
import httpx
import json
from mcp.server.fastmcp import FastMCP
from tool_helpers.file_search_helpers import file_search_helper
from tool_helpers.rag_ingest_helpers import ingest_documents_pipeline
from tool_helpers.rag_retrieval_helpers import retrieve_documents_pipeline


mcp = FastMCP()

@mcp.tool()
def get_path_to_file_based_on_parent_directory(parent_directory: str, target_file: str) -> str:
    
    """
    Searches for a target file in a given parent directory using direct traversal.
    
    This tool performs a recursive search through the specified parent directory
    and all its subdirectories to find the target file. It uses direct traversal
    instead of generating a full directory tree first, making it efficient for
    finding single files.
    
    Args:
        parent_directory: The parent directory path to search in (e.g., "C:\\Users\\John\\Desktop")
        target_file: The name of the file to search for (e.g., "example.txt")
    
    Returns:
        str: Full path to the file if found, or an error message if not found
    
    Example:
        parent_directory: "C:\\Users\\John\\Desktop"
        target_file: "example.txt"
        Returns: "C:\\Users\\John\\Desktop\\subfolder\\example.txt"
    """

    try:
        # Use the file search helper to find the file
        file_path = file_search_helper(target_file, parent_directory)
        
        if file_path:
            return f"File found: {file_path}"
        else:
            return f"File '{target_file}' not found in directory '{parent_directory}' or its subdirectories."
            
    except Exception as e:
        return f"Error searching for file: {str(e)}"


@mcp.tool()
def ingest_documents(file_paths: List[str]) -> str:
    r"""
    Ingests documents from given file paths into a vector database for RAG capabilities.
    
    This tool performs the complete RAG ingestion pipeline:
    1. Extracts text from files (.txt, .md formats supported)
    2. Chunks text at sentence level for optimal context
    3. Generates embeddings using OpenAI's CLIP model (local, no API key required)
    4. Stores vectors in ChromaDB with 20-minute persistence

    IMPORTANT - Windows Path Format:
        Windows directory paths MUST use double backslashes (\\) to avoid escape character issues.
        Correct: "C:\\Users\\John\\Desktop" or "D:\\Projects"
        Incorrect: "C:\Users\John\Desktop" (may cause search to fail)
    
    Args:
        file_paths: List of file paths to ingest (e.g., ["C:\\path\\to\\file1.txt", "C:\\path\\to\\file2.md"])
    
    Returns:
        str: Success message with ingestion details or error message
    
    Example:
        file_paths: ["C:\\Users\\John\\Desktop\\doc1.txt", "C:\\Users\\John\\Desktop\\readme.md"]
        Returns: "Successfully ingested 2 documents with 15 chunks into vector database"
    """
    
    try:
        if not file_paths:
            return "Error: No file paths provided for ingestion"
        
        # Run the complete ingestion pipeline
        result = ingest_documents_pipeline(file_paths)
        
        if result['status'] == 'success':
            return f"✅ {result['message']}\n📊 Processed {len(file_paths)} files into {result['chunks_count']} chunks\n🗂️ Collection: {result['collection_name']}"
        else:
            return f"❌ Ingestion failed: {result['message']}"
            
    except Exception as e:
        return f"❌ Error during document ingestion: {str(e)}"


@mcp.tool()
def retrieve_relevant_chunks(user_question: str, top_k: int = 5) -> str:
    """
    Retrieves the most relevant document chunks for answering a user question using RAG.
    
    This tool performs semantic search on the ingested document chunks:
    1. Vectorizes the user question using the same CLIP model as ingestion
    2. Calculates cosine similarity with all stored chunk embeddings
    3. Returns the top-k most relevant chunks with similarity scores
    4. Ensures unique chunks (no duplicates) in results
    
    Args:
        user_question: The user's question/query to find relevant information for
        top_k: Number of most relevant chunks to retrieve (default: 5, max recommended: 10)
    
    Returns:
        str: JSON-formatted string containing relevant chunks with metadata and similarity scores
    
    Example:
        user_question: "What is machine learning?"
        top_k: 3
        Returns: JSON with 3 most relevant chunks, their text content, similarity scores, and source file info
    """
    
    try:
        if not user_question or not user_question.strip():
            return "❌ Error: No user question provided for retrieval"
        
        # Run the retrieval pipeline
        result = retrieve_documents_pipeline(user_question.strip(), top_k)
        
        if result['status'] == 'success':
            # Format response with rich information
            chunks_info = []
            for chunk in result['retrieved_chunks']:
                chunk_info = {
                    "chunk_text": chunk["chunk_text"],
                    # "similarity_score": round(chunk["similarity_score"], 4),
                    # "source_file": chunk["metadata"]["filename"],
                    "file_path": chunk["metadata"]["file_path"],
                    # "chunk_index": chunk["metadata"]["chunk_index"]
                }
                chunks_info.append(chunk_info)
            
            response_data = {
                "query": result["query"],
                "total_chunks_searched": result["total_chunks_searched"],
                "retrieved_count": result["retrieved_count"],
                "relevant_chunks": chunks_info
            }
            
            return f"✅ Retrieved {result['retrieved_count']} relevant chunks from vector database:\n\n{json.dumps(response_data, indent=2, ensure_ascii=False)}"
        else:
            return f"❌ Retrieval failed: {result['message']}"
            
    except Exception as e:
        return f"❌ Error during chunk retrieval: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")