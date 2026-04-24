import json
import re

def extract_patches(response_text: str):
    # Intentar parsear si hay un bloque JSON con "patches"
    try:
        # Busca el bloque de código json
        match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
        if match:
            json_str = match.group(1)
            data = json.loads(json_str)
            if "patches" in data:
                return data["patches"]
    except:
        pass

    try:
        data = json.loads(response_text)
        if "patches" in data:
            return data["patches"]
    except:
        pass

    # Fallback
    match = re.search(r"### Patches(.*)", response_text, re.DOTALL)
    if not match:
        return []

    return [{
        "raw": match.group(1).strip()
    }]
