import os

exclude_dirs = {'.git', '__pycache__', '.venv'}

def directory_tree_generator(dir_path, prefix='', file=None):
    entries = [e for e in os.listdir(dir_path) if e not in exclude_dirs]
    entries_count = len(entries)

    # print(entries)
    
    # print(entries_count)

    for i, entry in enumerate(sorted(entries, key=str.lower)):
        path = os.path.join(dir_path, entry)
        connector = '└── ' if i == entries_count - 1 else '├── '

        line = prefix + connector + entry + '\n'
        if file:
            file.write(line)
        else:
            print(line, end='')

        if os.path.isdir(path):
            extension = '    ' if i == entries_count - 1 else '│   '

            # recursive call for traversing directories
            directory_tree_generator(path, prefix + extension, file)

# Usage example:
# root_folder = r'D:\\STUFF\\Projects\\MCP_File_System'
# directory_tree_generator(root_folder)




def file_search_helper(file_name, directory_path):
    """
    Direct traversal search for a target file in a given parent directory.
    
    Args:
        file_name (str): Name of the target file to search for
        directory_path (str): Parent directory path to search in
    
    Returns:
        str: Full path to the file if found, None if not found
    """
    try:
        # Check if the directory exists
        if not os.path.exists(directory_path):
            return None
        
        # Check if the directory is actually a directory
        if not os.path.isdir(directory_path):
            return None
        
        # Walk through all directories and subdirectories
        for root, dirs, files in os.walk(directory_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            # Check if target file is in current directory
            if file_name in files:
                return os.path.join(root, file_name)
        
        # File not found
        return None
        
    except (OSError, PermissionError) as e:
        # Handle permission errors or other OS-related errors
        print(f"Error accessing directory {directory_path}: {e}")
        return None


# Test the function (uncomment to test)
if __name__ == "__main__":
    # Test with current project directory
    test_directory = r'D:\\STUFF\\songs'
    test_file = "test.py"
    
    result = file_search_helper(test_file, test_directory)
    if result:
        print(f"Found: {result}")
    else:
        print(f"Not found")