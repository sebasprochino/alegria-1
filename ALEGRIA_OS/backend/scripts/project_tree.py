import os
from pathlib import Path

def generate_tree(dir_path, prefix='', ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = {'node_modules', '.git', '__pycache__', 'venv', '.next', 'dist', '.gemini'}
    
    output = []
    try:
        contents = sorted([p for p in dir_path.iterdir() if p.name not in ignore_dirs])
        count = len(contents)
        for i, path in enumerate(contents):
            connector = '+-- ' if i < count - 1 else '\\-- '
            output.append(f"{prefix}{connector}{path.name}")
            if path.is_dir():
                output.extend(generate_tree(path, prefix + ('|   ' if i < count - 1 else '    '), ignore_dirs))
    except PermissionError:
        pass
    return output

if __name__ == "__main__":
    project_root = Path(os.getcwd())
    tree_lines = generate_tree(project_root)
    print("ALEGRIA_OS PROJECT TREE")
    print("========================")
    print("\n".join(tree_lines))
