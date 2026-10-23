# 🛡️ Safe Agent Runtime Boilerplate (Inspiracja: EpiSEM-Bench: Evaluating Safety and Evidence Recovery in LLM Agents under Missing Evidence)

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
    Agent --> Guard{Permission Guard}
    Guard -- Zezwolone polecenie --> Sandbox[Środowisko Wykonawcze]
    Guard -- Zablokowane polecenie --> Error[Odmowa & Bezpieczny Fallback]
```

## 📜 Kod demonstracyjny (`agent_guard.py`)

Gotowa implementacja wzorca 'Least Privilege' w Pythonie, którą możesz wdrożyć w swoich agentach.