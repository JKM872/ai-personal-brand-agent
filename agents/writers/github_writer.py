"""
GitHub / Open-Source Demo Agent.
Generates working Python snippets and GitHub-ready project outlines
to build tangible engineering credibility for the personal brand.
"""

def generate_github_content(topic, persona):
    title = topic.get("title", "")
    url = topic.get("url", "")
    
    readme = f"""# 🛡️ Safe Agent Runtime Boilerplate (Inspiracja: {title})

Ten mini-projekt demonstruje, jak zaimplementować deterministyczną warstwę uprawnień (Permission Guard)
dla autonomicznych agentów AI, izolując wykonywane polecenia.

## 🚀 Szybki start

```bash
# Klonowanie i uruchomienie
python agent_guard.py
```

## 📐 Architektura

```mermaid
graph TD
    User([Zadanie]) --> Agent[Agent LLM]
    Agent --> Guard{{Permission Guard}}
    Guard -- Zezwolone polecenie --> Sandbox[Środowisko Wykonawcze]
    Guard -- Zablokowane polecenie --> Error[Odmowa & Bezpieczny Fallback]
```

## 📜 Kod demonstracyjny (`agent_guard.py`)

Gotowa implementacja wzorca 'Least Privilege' w Pythonie, którą możesz wdrożyć w swoich agentach.
"""

    demo_code = f"""# agent_guard.py
# Bezpieczna warstwa kontroli poleceń dla autonomicznych agentów AI

import re
import shlex

class AgentPermissionGuard:
    def __init__(self, allowed_command_prefixes):
        self.allowed_prefixes = allowed_command_prefixes
        self.audit_log = []

    def can_execute(self, command: str) -> bool:
        cmd_clean = command.strip()
        is_safe = any(cmd_clean.startswith(prefix) for prefix in self.allowed_prefixes)
        
        self.audit_log.append({{"command": cmd_clean, "allowed": is_safe}})
        return is_safe

    def execute_safely(self, command: str):
        if not self.can_execute(command):
            raise PermissionError(f"[BLOKADA BEZPIECZEŃSTWA] Polecenie niedozwolone: '{{command}}'")
        print(f"[OK] Wykonywanie autoryzowanego polecenia: '{{command}}'")
        # Tutaj następuje faktyczne wykonanie w piaskownicy

if __name__ == "__main__":
    guard = AgentPermissionGuard(allowed_command_prefixes=["git status", "pytest", "python -m unittest"])
    
    print("Test 1 - Bezpieczne polecenie:")
    guard.execute_safely("git status")
    
    print("\\nTest 2 - Próba wykonania niedozwolonego polecenia:")
    try:
        guard.execute_safely("rm -rf /")
    except PermissionError as e:
        print(e)
"""

    return {
        "readme": readme.strip(),
        "demo_code": demo_code.strip()
    }
