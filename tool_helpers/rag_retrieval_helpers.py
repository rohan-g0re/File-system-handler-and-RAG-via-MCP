import os
import json
from typing import List, Dict, Any
import numpy as np
import open_clip
import torch
from datetime import datetime, timedelta

# Import existing globals and functions from ingest helpers
from .rag_ingest_helpers import (
    init_clip_model, init_chroma_db, 
    CHROMA_CLIENT, CHROMA_COLLECTION, DB_EXPIRY_TIME
)


def vectorize_user_query(user_query: str) -> np.ndarray:
    """
    Vectorize user query using the same CLIP model used for document chunks.
    
    Args:
        user_query: The user's question/query as a string
        
    Returns:
        np.ndarray: Normalized embedding vector for the query
    """
    try:
        # Initialize CLIP model (reuses existing global model)
        model, device = init_clip_model()
        
        # Tokenize and encode the user query
        tokenizer = open_clip.get_tokenizer('ViT-B-32')
        text_tokens = tokenizer([user_query]).to(device)
        
        with torch.no_grad():
            query_features = model.encode_text(text_tokens)
            # Normalize the features (same as chunk embeddings)
            query_features = query_features / query_features.norm(dim=-1, keepdim=True)
        
        return query_features.cpu().numpy()[0]  # Return single embedding
        
    except Exception as e:
        raise Exception(f"Error vectorizing user query: {str(e)}")


def cosine_similarity_and_retrieve(user_query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Retrieve most relevant chunks based on cosine similarity with user query.
    Uses ChromaDB's built-in similarity search for efficiency.
    
    Args:
        user_query: The user's question/query as a string
        top_k: Number of most similar chunks to retrieve (default: 5)
        
    Returns:
        Dict containing status, retrieved chunks, and metadata
    """
    try:
        # Get ChromaDB collection
        collection = init_chroma_db()
        
        if not collection:
            return {"status": "error", "message": "ChromaDB collection not available"}
        
        # Check if collection has any documents
        collection_count = collection.count()
        if collection_count == 0:
            return {"status": "error", "message": "No documents found in vector database"}
        
        # Vectorize user query
        query_embedding = vectorize_user_query(user_query)
        
        # Use ChromaDB's built-in similarity search (more efficient than manual calculation)
        query_results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=min(top_k, collection_count),  # Don't request more than available
            include=["documents", "metadatas", "distances"]
        )
        
        # Prepare results with unique chunks
        retrieved_chunks = []
        seen_chunk_ids = set()
        
        # ChromaDB returns results in lists (even for single query)
        ids = query_results["ids"][0]
        documents = query_results["documents"][0]
        metadatas = query_results["metadatas"][0]
        distances = query_results["distances"][0]
        
        for i, chunk_id in enumerate(ids):
            # Ensure uniqueness
            if chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(chunk_id)
                
                # Convert distance to similarity score (ChromaDB uses cosine distance)
                # Cosine distance = 1 - cosine similarity, so similarity = 1 - distance
                similarity_score = 1.0 - distances[i]
                
                chunk_info = {
                    "chunk_id": chunk_id,
                    "chunk_text": documents[i],
                    "similarity_score": float(similarity_score),
                    "metadata": metadatas[i]
                }
                retrieved_chunks.append(chunk_info)
        
        return {
            "status": "success",
            "query": user_query,
            "total_chunks_searched": collection_count,
            "retrieved_chunks": retrieved_chunks,
            "retrieved_count": len(retrieved_chunks)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error during retrieval: {str(e)}"
        }


def retrieve_documents_pipeline(user_query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Complete retrieval pipeline - main function to call for RAG retrieval.
    
    Args:
        user_query: The user's question/query as a string
        top_k: Number of most similar chunks to retrieve (default: 5)
        
    Returns:
        Dict containing retrieval results in JSON format
    """
    try:
        print(f"Starting retrieval pipeline for query: '{user_query[:50]}...'")
        
        # Perform retrieval
        result = cosine_similarity_and_retrieve(user_query, top_k)
        
        if result["status"] == "success":
            print(f"Retrieved {result['retrieved_count']} relevant chunks from {result['total_chunks_searched']} total chunks")
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Pipeline error: {str(e)}"
        }