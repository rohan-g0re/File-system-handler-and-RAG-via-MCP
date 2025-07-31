import os
import json
import time
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
import open_clip
import torch
from datetime import datetime, timedelta
import nltk
from nltk.tokenize import sent_tokenize

# Download required NLTK data (only if not already present)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

# Global ChromaDB client and collection
CHROMA_CLIENT = None
CHROMA_COLLECTION = None
DB_EXPIRY_TIME = 100 
DB_PERSIST_PATH = "./chroma_db"

# Global CLIP model (initialized lazily)
CLIP_MODEL = None
CLIP_DEVICE = None

def init_clip_model():
    """Initialize CLIP model with CPU/GPU detection"""
    global CLIP_MODEL, CLIP_DEVICE
    
    if CLIP_MODEL is None:
        print("Loading OpenCLIP model...")
        CLIP_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        CLIP_MODEL, _, _ = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
        CLIP_MODEL = CLIP_MODEL.to(CLIP_DEVICE)
        print(f"OpenCLIP model loaded on {CLIP_DEVICE}")
    
    return CLIP_MODEL, CLIP_DEVICE

def init_chroma_db():
    """Initialize ChromaDB with 20-minute persistence"""
    global CHROMA_CLIENT, CHROMA_COLLECTION, DB_EXPIRY_TIME
    
    current_time = datetime.now()
    
    # Check if DB is still valid (within 20 minutes)
    if CHROMA_CLIENT and DB_EXPIRY_TIME and current_time < DB_EXPIRY_TIME:
        return CHROMA_COLLECTION
    
    # Clean up old client if exists
    if CHROMA_CLIENT:
        CHROMA_CLIENT = None
        CHROMA_COLLECTION = None
    
    # Initialize new ChromaDB client with persistence
    CHROMA_CLIENT = chromadb.PersistentClient(path=DB_PERSIST_PATH)
    
    # Create or get collection
    collection_name = f"documents_{int(current_time.timestamp())}"
    try:
        CHROMA_COLLECTION = CHROMA_CLIENT.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    except Exception:
        # Collection might already exist
        CHROMA_COLLECTION = CHROMA_CLIENT.get_collection(name=collection_name)
    
    # Set expiry time (20 minutes from now)
    DB_EXPIRY_TIME = current_time + timedelta(minutes=20)
    
    return CHROMA_COLLECTION

def extract_text(file_path: str) -> str:
    """Extract text from file based on format (.txt, .md)"""
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                return content.strip()
        else:
            return f"Unsupported file format: {file_ext}"
            
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

def find_and_scan(file_paths: List[str]) -> List[Dict[str, Any]]:
    """Process multiple file paths and extract text, return as JSON format"""
    results = []
    
    for file_path in file_paths:
        text_content = extract_text(file_path)
        
        if not text_content.startswith("Error"):
            result = {
                "file_path": file_path,
                "filename": os.path.basename(file_path),
                "text_content": text_content,

                "extracted_at": datetime.now().isoformat(),
                
                "file_size": len(text_content)
            }
            results.append(result)
        else:
            print(f"Skipping {file_path}: {text_content}")
    
    return results

def chunk_and_vectorize(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Chunk text at sentence level and vectorize using CLIP embeddings"""
    vectorized_chunks = []
    
    # Initialize CLIP model (local, no API key required)
    model, device = init_clip_model()
    
    for doc in documents:
        text_content = doc["text_content"]
        
        # Chunk at sentence level
        sentences = sent_tokenize(text_content)
        
        # Group sentences into chunks (3-5 sentences per chunk for context)
        chunk_size = 4
        chunks = []
        for i in range(0, len(sentences), chunk_size):
            chunk_text = " ".join(sentences[i:i + chunk_size])
            if chunk_text.strip():  # Only add non-empty chunks
                chunks.append(chunk_text.strip())
        
        # Generate embeddings for chunks using CLIP
        if chunks:
            try:
                # Process chunks in batches for efficiency
                batch_size = 32  # CLIP can handle larger batches
                for batch_start in range(0, len(chunks), batch_size):
                    batch_chunks = chunks[batch_start:batch_start + batch_size]
                    
                    # Tokenize and encode text using OpenCLIP
                    tokenizer = open_clip.get_tokenizer('ViT-B-32')
                    text_tokens = tokenizer(batch_chunks).to(device)
                    
                    with torch.no_grad():
                        text_features = model.encode_text(text_tokens)
                        # Normalize the features (common practice for embeddings)
                        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                    
                    # Convert to list and store chunk info
                    for i, embedding in enumerate(text_features.cpu().numpy()):
                        chunk_idx = batch_start + i
                        chunk_info = {
                            "chunk_id": f"{doc['filename']}_{chunk_idx}",
                            "file_path": doc["file_path"],
                            "filename": doc["filename"],
                            "chunk_text": batch_chunks[i],
                            "embedding": embedding.tolist(),  # Convert numpy array to list
                            "chunk_index": chunk_idx,
                            "total_chunks": len(chunks),
                            "created_at": datetime.now().isoformat()
                        }
                        vectorized_chunks.append(chunk_info)
                    
            except Exception as e:
                print(f"Error generating CLIP embeddings for {doc['filename']}: {str(e)}")
    
    return vectorized_chunks

def push_to_db(vectorized_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Push embeddings to ChromaDB"""
    try:
        collection = init_chroma_db()
        
        if not vectorized_chunks:
            return {"status": "error", "message": "No chunks to store"}
        
        # Prepare data for ChromaDB
        ids = [chunk["chunk_id"] for chunk in vectorized_chunks]
        embeddings = [chunk["embedding"] for chunk in vectorized_chunks]
        documents = [chunk["chunk_text"] for chunk in vectorized_chunks]
        metadatas = []
        
        for chunk in vectorized_chunks:
            metadata = {
                "file_path": chunk["file_path"],
                "filename": chunk["filename"],
                "chunk_index": chunk["chunk_index"],
                "total_chunks": chunk["total_chunks"],
                "created_at": chunk["created_at"]
            }
            metadatas.append(metadata)
        
        # Add to ChromaDB
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        return {
            "status": "success",
            "message": f"Successfully stored {len(vectorized_chunks)} chunks in vector DB",
            "chunks_count": len(vectorized_chunks),
            "collection_name": collection.name
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error storing in vector DB: {str(e)}"
        }

def ingest_documents_pipeline(file_paths: List[str]) -> Dict[str, Any]:
    """Complete ingestion pipeline - main function to call"""
    try:
        print(f"Starting ingestion pipeline for {len(file_paths)} files...")
        
        # Step 1: Extract text from files
        documents = find_and_scan(file_paths)
        if not documents:
            return {"status": "error", "message": "No documents could be processed"}
        
        print(f"Extracted text from {len(documents)} files")
        
        # Step 2: Chunk and vectorize
        vectorized_chunks = chunk_and_vectorize(documents)
        if not vectorized_chunks:
            return {"status": "error", "message": "No chunks could be vectorized"}
        
        print(f"Generated {len(vectorized_chunks)} vectorized chunks")
        
        # Step 3: Push to database
        result = push_to_db(vectorized_chunks)
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Pipeline error: {str(e)}"
        }