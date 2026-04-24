import os
import difflib

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def generate_diff(file_path: str, new_content: str) -> str:
    abs_path = os.path.join(BASE_PATH, file_path)
    abs_path = os.path.normpath(abs_path)

    old_content = read_file(abs_path).splitlines()
    new_content_lines = new_content.splitlines()

    diff = difflib.unified_diff(
        old_content,
        new_content_lines,
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
        lineterm=""
    )

    return "\n".join(diff)
