from typing  import Any
import httpx
from mcp.server.fastmcp import FastMCP


mcp = FastMCP()

@mcp.tool()
def get_path_to_file_based_on_parent_directory(parent_directory: str, target_file: str) -> str:
    """
    If a parent directory is mentioned in the chat and we have to find a file in it,
    then pass the parent drive or the parent directory path given by the user as a string argument.
    
    Returns the path to the file based on the parent directory.

    Example Input:
    parent_directory: "C:\\Users\\John\Desktop"
    target_file: "example.txt"
    
    Example Output:
    "C:\Users\John\Desktop\example.txt"
    """


    
    
    
    
    return path



