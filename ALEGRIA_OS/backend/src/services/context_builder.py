import os
from typing import List, Dict

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

def select_files_by_prompt(prompt: str) -> List[str]:
    files = []
    prompt_lower = prompt.lower()

    if "audit" in prompt_lower:
        files.append("backend/src/services/audit_emitter.py")
        files.append("backend/src/routes/anima.py")

    if "anima" in prompt_lower:
        files.append("backend/src/routes/anima.py")

    if "ui" in prompt_lower or "timeline" in prompt_lower:
        files.append("frontend/src/anima/AnimaUI.tsx")

    if "brand" in prompt_lower:
        files.append("backend/src/services/brand_service.py")

    # fallback mínimo
    if not files:
        files.append("backend/src/services/developer.py")

    return files


def read_file_safe(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"# ERROR leyendo {path}: {e}"


def build_context(prompt: str = "", files: List[str] = None, max_chars: int = 12000) -> Dict:
    files = files or select_files_by_prompt(prompt)

    context_blocks = []
    total_size = 0

    for rel_path in files:
        abs_path = os.path.join(BASE_PATH, rel_path)
        
        # Fix paths for windows backward compatibility
        abs_path = os.path.normpath(abs_path)

        if not os.path.exists(abs_path):
            continue

        content = read_file_safe(abs_path)

        block = f"\n### FILE: {rel_path}\n{content}\n"

        if total_size + len(block) > max_chars:
            break

        context_blocks.append(block)
        total_size += len(block)

    return {
        "files_included": files,
        "context": "\n".join(context_blocks)
    }
