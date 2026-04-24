from typing import Dict, Any


class DeveloperAntigravity:

    def review(self, response: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        issues = []
        suggestions = []
        severity = "low"

        if not response:
            return {
                "risk": False,
                "issues": [],
                "suggestions": [],
                "severity": "low"
            }

        r = response.lower()

        # ─────────────────────────────
        # REGLAS ANTIGRAVITY
        # ─────────────────────────────

        # 1. Bypass backend
        if "fetch(" in r and "http" in r:
            issues.append("Posible bypass de backend detectado")
            suggestions.append("Usar rutas /api internas en lugar de llamadas directas a providers")
            severity = "high"

        # 2. Hardcode providers
        if "api.openai.com" in r or "anthropic.com" in r:
            issues.append("Provider hardcodeado detectado")
            suggestions.append("Usar provider_registry y cascade")
            severity = "high"

        # 3. Duplicación de lógica
        if "nuevo backend" in r or "crear otro servicio" in r:
            issues.append("Posible duplicación de servicios")
            suggestions.append("Reutilizar servicios existentes (Anima, Nexus, etc)")
            severity = "medium"

        # 4. Frontend haciendo lógica pesada
        if "hacer todo en frontend" in r:
            issues.append("Lógica crítica en frontend")
            suggestions.append("Mover lógica al backend (FastAPI)")
            severity = "high"

        # 5. Anti-ACSP patterns
        if "directo al provider" in r:
            issues.append("Violación de ACSP detectada")
            suggestions.append("Pasar siempre por Anima y provider cascade")
            severity = "high"

        return {
            "risk": len(issues) > 0,
            "issues": issues,
            "suggestions": suggestions,
            "severity": severity
        }


developer_antigravity = DeveloperAntigravity()
