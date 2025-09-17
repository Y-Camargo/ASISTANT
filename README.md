
# Asistente de Aprendizaje (RAG local)

Asistente privado que indexa tus PDFs/textos, recupera contexto por similitud y responde citando `[source#chunk]` con un LLM local vía Ollama.

Se sube  materiales (PDF o texto), se trocean y vectorizan con Ollama y se guardan en ChromaDB. 
Al preguntar por /chat, recupera los fragmentos más parecidos, arma un prompt y el modelo (p. ej. phi3:mini) responde en español con citas tipo [source#chunk], adaptándose al perfil del usuario. 
Todo se prueba automáticamente con promptfoo, y en GitHub Actions se levanta Ollama real, se reindexa, se corren los tests y se publica un reporte/mini dashboard.
En resumen, representa un pipeline confiable, reproducible y auditable para asistente interno con datos propios.

![1](https://github.com/user-attachments/assets/2cecf2ca-45a7-45a1-a971-c27416abc4a8)

![2](https://github.com/user-attachments/assets/5c89beb6-b109-4a20-9c46-977d8d5e6177)


![3](https://github.com/user-attachments/assets/ebbb54cf-6c0c-4961-8907-829ea48616b9)


## 1) Requisitos

    - **Python 3.11+**
    - **Node 18+** (para promptfoo via `npx`)
    - **Ollama** (`curl -fsSL https://ollama.com/install.sh | sh`)
    - Modelos Ollama:
      ```bash
      ollama pull nomic-embed-text
      ollama pull phi3:mini

## 2) Instalación

    python -m venv .venv && . .venv/bin/activate   # (Windows: .venv\Scripts\activate)
    python -m pip install -U pip
    pip install -r requirements.txt

## 3) Ingesta de materiales

    Copia PDFs con texto seleccionable en ./materiales/.
    Se debe ejecutar python build_index.py
    tambien se puede ejecutar la ingesta desde postman con el curl:
      
      curl -s -X POST http://localhost:8000/ingest_text \
        -H "Content-Type: application/json" \
        -d '{"source_name":"kpis.md","text":"CSAT, NPS, FCR, AHT, SLA..."}'

## 4) Ejecutar API   # en otra terminal
 
      ollama serve &                        
      uvicorn server:app --reload --port 8000
      
      En postman se ejecuta para ver la salud del API
      curl -s http://localhost:8000/health | jq .
      curl -s http://localhost:8000/sources | jq .

## 5) Consultar (/chat)

  curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"ana","message":"¿Qué responsabilidades tiene el facilitador durante la sesión?","top_k":8,"distance_threshold":0.9,"temperature":0.1}' | jq .

## 6) Configuración rápida

    Edita app/config.py:
    
    CHAT_MODEL="phi3:mini"
    
    EMBED_MODEL="nomic-embed-text"
    
    TOP_K=8, DISTANCE_THRESHOLD=0.9
    
    MAX_CHARS=2800, OVERLAP_CHARS=400
    
    Perfiles: perfiles/<user_id>.json (estilo, nivel, max_words).

## 7) Pruebas con promptfoo

   promptfooconfig.yaml            # Archivo de configuración
   tests.yaml                      # Casos de prueba
   tests.out_of_context.yaml       # Casos fuera de contexto 

   Ejecutar en el terminal :

   promptfoo eval -c promptfooconfig.yaml -c tests.yaml -c tests.out_of_context.yaml

   

## 8) CI/CD (GitHub Actions)

    Workflow recomendado: levanta Ollama real (cache ~/.ollama), indexa, corre promptfoo, publica reportes y dashboard (Pages).
    
    Archivo: .github/workflows/rag-ci.yml (ver pipeline del repo).


## 9) Troubleshooting

    used_chunks=0: índice vacío, PDFs sin texto, umbral bajo → re-indexa, sube top_k (8–10) y threshold (0.9–0.95).
    
    PDF escaneado: usa OCR o genera un PDF nativo.
    
    Ollama: verifica http://127.0.0.1:11434/api/tags.


## Idea clave:

    Todo es local y reproducible: datos propios → recuperación auditable → respuesta con citas.



