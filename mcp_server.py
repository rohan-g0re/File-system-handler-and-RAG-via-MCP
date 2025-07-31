from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from file_search_helpers import file_search_helper


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


if __name__ == "__main__":
    mcp.run(transport="stdio")