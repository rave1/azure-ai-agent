import gradio as gr
import os
from dotenv import load_dotenv

load_dotenv()

# ====================== MOCK / PLACEHOLDER ======================
def generate_architecture(user_prompt: str):
    if not user_prompt or user_prompt.strip() == "":
        return (
            "**Wpisz opis aplikacji powyżej**",
            "```mermaid\ngraph TD\nA[Brak promptu] --> B[Spróbuj jeszcze raz]\n```"
        )

    explanation = f"""### Propozycja architektury Azure dla:  
        **{user_prompt}**

        **Główne komponenty:**
        - **Azure App Service** – hosting aplikacji (skalowanie automatyczne)
        - **Azure Cosmos DB** – baza NoSQL (globalnie rozproszona)
        - **Azure Redis Cache** – cache + sesje
        - **Azure Front Door** – CDN + load balancing + WAF
        - **Application Insights** – monitoring + AI alerts

        **Dlaczego akurat tak?**  
        - Skalowalność do 50k użytkowników  
        - Koszt miesięczny ~180–250 zł (przy małym ruchu)  
        - Pełna zgodność z Well-Architected Framework Microsoftu

        **Następne kroki:** kliknij "Pokaż diagram" lub zapytaj o koszty/Terraform."""

    mermaid_diagram = f"""```mermaid
        graph TD
            A[Klient / Internet] -->|HTTPS| B[Azure Front Door\nCDN + WAF]
            B -->|traffic| C[Azure App Service\nPlan Premium]
            C --> D[Azure Redis Cache\nSesje + cache]
            C --> E[Azure Cosmos DB\nNoSQL – multi-region]
            C --> F[Azure Key Vault\nSekrety]
            C -.-> G[Application Insights\nMonitoring + alerts]
            E --> H[Azure Storage\nBackup / blob]
            
            style B fill:#0078D4,stroke:#fff,color:#fff
            style C fill:#0078D4,stroke:#fff,color:#fff
            style E fill:#0078D4,stroke:#fff,color:#fff
            style G fill:#107C10,stroke:#fff,color:#fff
        ```"""

    return explanation, mermaid_diagram

# ====================== GRADIO UI ======================
with gr.Blocks(title="AzureArchAI", theme=gr.themes.Soft(), css="#mermaid {height: 100% !important;}") as demo:
    gr.Markdown("# 🌩️ AzureArchAI\n**Inteligentny asystent architektur chmurowych Azure**  \nWklej opis aplikacji → dostajesz gotową architekturę + piękny diagram w 3 sekundy")
    
    with gr.Row():
        with gr.Column(scale=2):
            prompt_input = gr.Textbox(
                label="Opisz swoją aplikację (np. e-commerce, system rezerwacji, API dla mobilki...)",
                placeholder="Chcę aplikację webową do rezerwacji biletów kinowych z 10 tys. użytkowników dziennie...",
                lines=5,
                max_lines=10
            )
            
            with gr.Row():
                generate_btn = gr.Button("Generuj architekturę Azure", variant="primary")
                clear_btn = gr.Button("Wyczyść", variant="secondary")

            gr.Markdown("### Wynik")
            
            with gr.Tabs():
                with gr.TabItem("Wyjaśnienie + uzasadnienie"):
                    explanation_output = gr.Markdown(label="Propozycja", value="Tu pojawi się tekst...")
                
                with gr.TabItem("Diagram Mermaid"):
                    diagram_output = gr.Markdown(label="Diagram (kopiuj do dowolnego edytora)", value="```mermaid")
    
    # Przycisk demo (żeby od razu pokazać koledze jak super wygląda)
    with gr.Row():
        demo_btn = gr.Button("Pokaż przykładowy projekt (e-commerce)", variant="secondary")
    
    gr.Markdown("---\n**Historia będzie tu później (z bazy SQLite)** – na razie tylko demo")

    # ====================== LOGIKA ======================
    generate_btn.click(
        fn=generate_architecture,
        inputs=prompt_input,
        outputs=[explanation_output, diagram_output]
    )
    
    demo_btn.click(
        fn=lambda: generate_architecture("e-commerce z 10 tys. użytkowników dziennie + płatności online"),
        outputs=[explanation_output, diagram_output]
    )
    
    clear_btn.click(
        fn=lambda: ("", ""),
        outputs=[explanation_output, diagram_output]
    )

# ====================== URUCHOMIENIE ======================
if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,          # zmień na True jeśli chcesz link publiczny
        show_error=True,
        debug=True
    )
