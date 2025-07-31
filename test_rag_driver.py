#!/usr/bin/env python3
"""
Test driver for RAG helper functions with recursive testing
"""

import os
import tempfile
from rag_helpers import (
    extract_text, 
    find_and_scan, 
    chunk_and_vectorize, 
    push_to_db, 
    ingest_documents_pipeline,
    init_chroma_db
)

def create_test_files():
    """Create temporary test files for testing"""
    test_files = []
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="rag_test_")
    
    # Test file 1: .txt file
    txt_content = """This is a test document for RAG ingestion. 
    It contains multiple sentences to test chunking functionality.
    The text should be properly extracted and processed.
    This will help verify that our pipeline works correctly.
    We can use this for comprehensive testing of the system."""
    
    txt_file = os.path.join(temp_dir, "test_document.txt")
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    test_files.append(txt_file)
    
    # Test file 2: .md file
    md_content = """# Test Markdown Document

This is a markdown document for testing RAG functionality.

## Section 1
This section contains important information about the test.
We want to ensure markdown files are processed correctly.

## Section 2
Another section with different content to create variety.
This helps test the chunking and vectorization process.
Multiple paragraphs should be handled properly."""
    
    md_file = os.path.join(temp_dir, "test_readme.md")
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    test_files.append(md_file)
    
    return test_files, temp_dir

def cleanup_test_files(temp_dir):
    """Clean up temporary test files"""
    import shutil
    try:
        shutil.rmtree(temp_dir)
        print(f"✓ Cleaned up test directory: {temp_dir}")
    except Exception as e:
        print(f"⚠ Warning: Could not clean up {temp_dir}: {e}")

def test_extract_text(test_files):
    """Test the extract_text function"""
    print("\n=== Testing extract_text function ===")
    
    for file_path in test_files:
        print(f"\nTesting file: {os.path.basename(file_path)}")
        text = extract_text(file_path)
        
        if text.startswith("Error"):
            print(f"❌ Failed: {text}")
            return False
        else:
            print(f"✓ Success: Extracted {len(text)} characters")
            print(f"Preview: {text[:100]}...")
    
    # Test non-existent file
    print(f"\nTesting non-existent file...")
    result = extract_text("non_existent_file.txt")
    if result.startswith("Error"):
        print(f"✓ Correctly handled missing file: {result}")
    else:
        print(f"❌ Should have returned error for missing file")
        return False
    
    return True

def test_find_and_scan(test_files):
    """Test the find_and_scan function"""
    print("\n=== Testing find_and_scan function ===")
    
    documents = find_and_scan(test_files)
    
    if not documents:
        print("❌ Failed: No documents returned")
        return False
    
    print(f"✓ Success: Processed {len(documents)} documents")
    
    for doc in documents:
        print(f"  - {doc['filename']}: {doc['file_size']} chars")
        if not all(key in doc for key in ['file_path', 'filename', 'text_content', 'extracted_at']):
            print("❌ Failed: Missing required keys in document")
            return False
    
    return True

def test_chunk_and_vectorize(documents):
    """Test the chunk_and_vectorize function"""
    print("\n=== Testing chunk_and_vectorize function ===")
    
    try:
        vectorized_chunks = chunk_and_vectorize(documents)
        
        if not vectorized_chunks:
            print("❌ Failed: No vectorized chunks returned")
            return False
        
        print(f"✓ Success: Generated {len(vectorized_chunks)} vectorized chunks")
        
        # Check first chunk structure
        first_chunk = vectorized_chunks[0]
        required_keys = ['chunk_id', 'file_path', 'filename', 'chunk_text', 'embedding', 'chunk_index']
        
        for key in required_keys:
            if key not in first_chunk:
                print(f"❌ Failed: Missing key '{key}' in chunk")
                return False
        
        print(f"  - First chunk ID: {first_chunk['chunk_id']}")
        print(f"  - Embedding dimensions: {len(first_chunk['embedding'])}")
        print(f"  - Chunk text preview: {first_chunk['chunk_text'][:80]}...")
        print(f"  - Using CLIP model (local, no API required)")
        
        return True, vectorized_chunks
        
    except Exception as e:
        print(f"❌ Failed: Error in CLIP vectorization: {e}")
        return False, None

def test_push_to_db(vectorized_chunks):
    """Test the push_to_db function"""
    print("\n=== Testing push_to_db function ===")
    
    try:
        result = push_to_db(vectorized_chunks)
        
        if result['status'] != 'success':
            print(f"❌ Failed: {result['message']}")
            return False
        
        print(f"✓ Success: {result['message']}")
        print(f"  - Chunks stored: {result['chunks_count']}")
        print(f"  - Collection: {result['collection_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: Error pushing to DB: {e}")
        return False

def test_db_persistence():
    """Test that DB persists across calls"""
    print("\n=== Testing DB persistence ===")
    
    try:
        # Initialize DB
        collection1 = init_chroma_db()
        collection_name1 = collection1.name
        
        # Call again - should return same collection
        collection2 = init_chroma_db()
        collection_name2 = collection2.name
        
        if collection_name1 == collection_name2:
            print("✓ Success: DB persistence working correctly")
            return True
        else:
            print(f"❌ Failed: Different collections returned ({collection_name1} vs {collection_name2})")
            return False
            
    except Exception as e:
        print(f"❌ Failed: Error testing persistence: {e}")
        return False

def test_complete_pipeline(test_files):
    """Test the complete ingestion pipeline"""
    print("\n=== Testing complete pipeline ===")
    
    try:
        result = ingest_documents_pipeline(test_files)
        
        if result['status'] != 'success':
            print(f"❌ Failed: {result['message']}")
            return False
        
        print(f"✓ Success: {result['message']}")
        print(f"  - Total chunks: {result['chunks_count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: Pipeline error: {e}")
        return False

def main():
    """Main test function - recursive testing approach"""
    print("🚀 Starting RAG Helper Functions Test Suite")
    print("=" * 50)
    
    # Setup
    test_files, temp_dir = create_test_files()
    print(f"Created test files in: {temp_dir}")
    
    all_tests_passed = True
    
    try:
        # Test 1: Extract text function
        if not test_extract_text(test_files):
            all_tests_passed = False
        
        # Test 2: Find and scan function
        documents = find_and_scan(test_files)
        if not test_find_and_scan(test_files):
            all_tests_passed = False
        
        # Test 3: Chunk and vectorize function (only if previous tests passed)
        if documents and all_tests_passed:
            vectorize_success, vectorized_chunks = test_chunk_and_vectorize(documents)
            if not vectorize_success:
                all_tests_passed = False
            
            # Test 4: Push to DB (only if vectorization passed)
            if vectorized_chunks and vectorize_success:
                if not test_push_to_db(vectorized_chunks):
                    all_tests_passed = False
        
        # Test 5: DB persistence
        if not test_db_persistence():
            all_tests_passed = False
        
        # Test 6: Complete pipeline
        if not test_complete_pipeline(test_files):
            all_tests_passed = False
        
    except Exception as e:
        print(f"❌ Critical error during testing: {e}")
        all_tests_passed = False
    
    finally:
        # Cleanup
        cleanup_test_files(temp_dir)
    
    # Final result
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! RAG helpers are working correctly.")
        return 0
    else:
        print("❌ SOME TESTS FAILED! Check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())