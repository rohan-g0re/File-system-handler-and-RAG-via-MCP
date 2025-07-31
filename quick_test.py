#!/usr/bin/env python3
"""
Quick test to verify RAG helper functions work without API calls
"""

import os
import tempfile
from rag_helpers import extract_text, find_and_scan

def test_basic_functionality():
    """Test basic text extraction using local CLIP model"""
    print("🧪 Quick Test: Basic RAG functionality (CLIP model)")
    print("=" * 50)
    
    # Create a temporary test file
    temp_dir = tempfile.mkdtemp(prefix="quick_test_")
    test_file = os.path.join(temp_dir, "test.txt")
    
    test_content = """This is a test document.
It has multiple sentences.
We want to test text extraction."""
    
    try:
        # Write test file
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"✓ Created test file: {test_file}")
        
        # Test text extraction
        extracted_text = extract_text(test_file)
        if extracted_text.startswith("Error"):
            print(f"❌ Text extraction failed: {extracted_text}")
            return False
        
        print(f"✓ Text extraction successful: {len(extracted_text)} characters")
        
        # Test document scanning
        documents = find_and_scan([test_file])
        if not documents:
            print("❌ Document scanning failed")
            return False
        
        print(f"✓ Document scanning successful: {len(documents)} documents")
        print(f"  Document info: {documents[0]['filename']} ({documents[0]['file_size']} chars)")
        
        print("\n🎉 Basic functionality tests PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        # Cleanup
        try:
            import shutil
            shutil.rmtree(temp_dir)
            print(f"✓ Cleaned up test directory")
        except:
            pass

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\n✅ Ready to run full tests with OpenCLIP!")
        print("💡 Next steps:")
        print("   1. Install dependencies: pip install open-clip-torch torch torchvision")
        print("   2. Run: python test_rag_driver.py")
        print("   3. Test MCP server integration")
    else:
        print("\n❌ Basic tests failed. Check your setup.")
    
    exit(0 if success else 1)