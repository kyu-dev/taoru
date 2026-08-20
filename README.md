# taoru

Bac à sable d'apprentissage LangGraph / LangChain : un agent conversationnel
minimal (un seul node `llm_call` branché sur Mistral).

## Démarrage

```bash
uv sync
cp .env.example .env   # puis renseigner MISTRAL_API_KEY
uv run langgraph dev   # ouvre LangGraph Studio
```

## Structure

```
src/taoru/
  agent/        state, graph, nodes, prompt
  api/          (vide)
  retreival/    (vide)
  infrastructure/ (vide)
langgraph.json  déclare le graph `taoru` pour `langgraph dev`
```
