import ollama
import asyncio
import os
import re
import base64
from typing import Tuple


class AzureArchitect:
    """Azure Cloud Architect AI Agent"""

    SYSTEM_PROMPT = """Jesteś doświadczonym architektem chmury Microsoft Azure. Odpowiadaj WYŁĄCZNIE PO POLSKU.

Twoja odpowiedź musi zawierać DOKŁADNIE te cztery sekcje w tej kolejności:

## Architektura
Lista komponentów w formacie:
- **[Nazwa usługi Azure]** (wariant/SKU) – rola w systemie

## Uzasadnienie
Wyjaśnij wybór każdej usługi: skalowalność, SLA, dlaczego nie alternatywy, best practices.

## Szacunkowe koszty miesięczne
- Każda usługa: ~X USD/miesiąc
- **Łącznie: ~X USD/miesiąc**

## Diagram
Na samym końcu wstaw JEDEN blok mermaid i nic więcej po nim:

```mermaid
graph TD
    A[Użytkownik] --> B[Azure Front Door]
    B --> C[Azure App Service]
    C --> D[(Azure SQL Database)]
    C --> E[Azure Cache for Redis]
```

ZASADY DIAGRAMU:
- Zawsze używaj graph TD
- Etykiety węzłów: krótka nazwa usługi po polsku, np. A[App Service - API]
- Bazy danych zapisuj z nawiasami: D[(Azure SQL)]
- Maksymalnie 12 węzłów
- Strzałki pokazują przepływ danych/żądań
- Zamknij blok trzema odwrotnymi apostrofami
- Po zamknięciu bloku mermaid NIE dodawaj żadnego tekstu ani komentarza"""

    client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))

    @staticmethod
    def _extract_mermaid(full_text: str) -> Tuple[str, str]:
        """Extracts (explanation, mermaid_code) from model response."""
        match = re.search(r'```mermaid\s*(.+?)\s*```', full_text, re.DOTALL | re.IGNORECASE)
        if match:
            explanation = full_text[:match.start()].strip()
            code = match.group(1).strip()
        else:
            graph_match = re.search(r'(graph\s+(?:TD|LR|RL|BT|TB)\b.+?)(?=\n\n|\Z)', full_text, re.DOTALL)
            if graph_match:
                explanation = full_text[:graph_match.start()].strip()
                code = graph_match.group(1).strip()
            else:
                return full_text.strip(), "graph TD\nA[Brak diagramu] --> B[Spróbuj ponownie]"

        code = code.replace('```', '').strip()
        if not code.startswith('graph'):
            code = 'graph TD\n' + code

        return explanation, code

    @staticmethod
    def _to_html(mermaid_code: str) -> str:
        encoded = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('ascii')
        return (
            f'<div style="text-align:center;padding:16px">'
            f'<img src="https://mermaid.ink/img/{encoded}" '
            f'style="max-width:100%;height:auto;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.15);" '
            f'alt="Diagram architektury Azure"/>'
            f'</div>'
        )

    @staticmethod
    async def generate(user_prompt: str) -> Tuple[str, str]:
        if not user_prompt.strip():
            return (
                "Wpisz opis aplikacji...",
                '<p style="color:gray;text-align:center">Diagram pojawi się tutaj po wygenerowaniu architektury.</p>'
            )

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    AzureArchitect.client.chat,
                    model="phi4-mini",
                    messages=[
                        {"role": "system", "content": AzureArchitect.SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    options={"temperature": 0.2, "num_ctx": 8192}
                ),
                timeout=90.0
            )

            full_text = response.message.content or ""
            print(full_text)

            explanation, mermaid_code = AzureArchitect._extract_mermaid(full_text)
            diagram_html = AzureArchitect._to_html(mermaid_code)

            return explanation, diagram_html

        except asyncio.TimeoutError:
            return (
                "❌ Timeout – model zbyt długo generował odpowiedź. Spróbuj ponownie.",
                '<p style="color:red;text-align:center">Błąd: przekroczono czas oczekiwania.</p>'
            )
        except Exception as e:
            return (
                f"❌ Błąd: {str(e)}",
                f'<p style="color:red;text-align:center">Błąd: {str(e)}</p>'
            )
