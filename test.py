import os

exclude_dirs = {'.git', '__pycache__', '.venv', 'weather'}

def tree(dir_path, prefix='', file=None):
    entries = [e for e in os.listdir(dir_path) if e not in exclude_dirs]
    entries_count = len(entries)

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
            tree(path, prefix + extension, file)

# Usage:
root_folder = r'D:\\STUFF\\Projects\\MCP_Projects'

with open('tree_output.txt', 'w', encoding='utf-8') as f:
    tree(root_folder, file=f)
