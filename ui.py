from __future__ import annotations
import requests
import gradio as gr

API_URL = "http://localhost:8000/chat"

def chat_call(user_id: str, message: str, k: int, th: float, temp: float):
    try:
        r = requests.post(API_URL, json={
            "user_id": user_id,
            "message": message,
            "top_k": k,
            "distance_threshold": th,
            "temperature": temp,
        }, timeout=60)
        if r.status_code != 200:
            return f"Error {r.status_code}: {r.text}"
        data = r.json()
        sources = "\n".join(data.get("sources", []))
        return f"{data.get('answer','')}\n\nFuentes:\n{sources}" if sources else data.get("answer","")
    except Exception as e:
        return f"UI error: {e}"

with gr.Blocks(title="Asistente de Aprendizaje") as demo:
    gr.Markdown("## Asistente de Aprendizaje (RAG sobre PDFs)")
    with gr.Row():
        user_in = gr.Textbox(label="Usuario (perfil)", value="ana")
        k_in = gr.Slider(1, 10, value=4, step=1, label="Top-K")
        th_in = gr.Slider(0.0, 1.5, value=0.4, step=0.05, label="Umbral distancia (cosine)")
        temp_in = gr.Slider(0.0, 1.0, value=0.3, step=0.05, label="Temperatura")
    msg = gr.Textbox(label="Tu pregunta", lines=3)
    out = gr.Markdown(label="Respuesta")
    btn = gr.Button("Preguntar")
    btn.click(chat_call, inputs=[user_in, msg, k_in, th_in, temp_in], outputs=[out])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)