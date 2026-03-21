import gradio as gr
from dotenv import load_dotenv
from agent import AzureArchitect

load_dotenv()

async def generate_architecture(user_prompt: str):
    yield (
        "⏳ Generuję architekturę Azure... (pierwszy raz może potrwać 10-15s)",
        "Trwa generowanie wyjaśnienia...",
        '<p style="color:gray;text-align:center">Trwa generowanie diagramu...</p>'
    )

    explanation, diagram_html = await AzureArchitect.generate(user_prompt)

    yield (
        "✅ Gotowe!",
        explanation,
        diagram_html
    )

with gr.Blocks(title="AzureArchAI") as demo:
    gr.Markdown("# 🌩️ AzureArchAI\n**Inteligentny asystent architektur Azure**")

    with gr.Row():
        with gr.Column(scale=2):
            prompt_input = gr.Textbox(
                label="Opisz aplikację...",
                lines=5,
                placeholder="np. system rezerwacji biletów z 10k użytkowników dziennie..."
            )
            generate_btn = gr.Button("Generuj architekturę", variant="primary", size="lg")

        with gr.Column(scale=3):
            status_output = gr.Markdown(value="Gotowy. Czekam na prompt.")

            with gr.Tabs():
                with gr.TabItem("📝 Wyjaśnienie"):
                    explanation_output = gr.Markdown()
                with gr.TabItem("📊 Diagram"):
                    diagram_output = gr.HTML()

demo.queue(max_size=20, default_concurrency_limit=5)

generate_btn.click(
    fn=generate_architecture,
    inputs=prompt_input,
    outputs=[status_output, explanation_output, diagram_output],
    show_progress="full",
    concurrency_limit=1
)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
    )
