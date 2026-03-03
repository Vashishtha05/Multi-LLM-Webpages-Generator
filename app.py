import json
import logging
import os
import time
from typing import Generator

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request
from openai import OpenAI

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("llm-benchmark-app")


def create_clients():
    """Create OpenAI and OpenRouter clients for different LLM services."""
    openai_key = os.getenv("OPENAI_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    clients = {}
    if openai_key:
        clients["openai"] = OpenAI(api_key=openai_key)
    if openrouter_key:
        clients["claude"] = OpenAI(
            api_key=openrouter_key, base_url="https://openrouter.ai/api/v1"
        )
        clients["gemini"] = OpenAI(
            api_key=openrouter_key, base_url="https://openrouter.ai/api/v1"
        )
    return clients


SYSTEM_PROMPT = """You are a professional landing page HTML generator. 
Create a complete, beautiful, single-file HTML landing page for the given product or service.
Include:
- A compelling hero section with CTA
- Features section
- Pricing or benefits
- Testimonials (you can create realistic ones)
- Footer with contact
- Modern CSS with gradients
- Responsive design
- NO external dependencies - all CSS must be inline <style> tags

Return ONLY the complete HTML code, nothing else."""


def generate_landing_page(
    client: OpenAI, product_description: str, model: str, max_tokens: int = 2000
) -> Generator[str, None, None]:
    """Generate a landing page using the specified LLM model."""
    start_time = time.time()

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": product_description},
            ],
            temperature=0.7,
            max_tokens=max(500, min(max_tokens, 4000)),
            stream=True,
        )

        full_content = ""
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                full_content += delta.content
                yield delta.content

        elapsed = time.time() - start_time
        yield f"\n\n<!-- Generated in {elapsed:.2f}s -->"

    except Exception as exc:
        logger.exception(f"Error generating with {model}")
        yield f"\n\n<!-- Error: {exc} -->"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "change-me-in-production")

    clients = create_clients()
    available_models = list(clients.keys())

    @app.get("/")
    def home():
        return render_template(
            "index.html", available_models=available_models, model_count=len(available_models)
        )

    @app.get("/health")
    def health():
        return jsonify(
            {"status": "ok", "available_models": available_models}
        ), 200

    @app.post("/api/generate")
    def generate():
        payload = request.get_json(silent=True) or {}
        description = (payload.get("description") or "").strip()
        selected_models = payload.get("models", [])
        max_tokens = int(payload.get("max_tokens", 2000))

        if not description:
            return jsonify({"error": "Product description is required."}), 400

        if not selected_models:
            return (
                jsonify({"error": "Select at least one model."}),
                400,
            )

        invalid_models = [m for m in selected_models if m not in available_models]
        if invalid_models:
            return (
                jsonify({"error": f"Invalid models: {invalid_models}"}),
                400,
            )

        def generate_all():
            """Generate landing pages sequentially and stream progress."""
            for model in selected_models:
                yield f'data: {{"model": "{model}", "status": "generating"}}\n\n'

                if model not in clients:
                    yield f'data: {{"model": "{model}", "error": "Client not configured"}}\n\n'
                    continue

                html_content = ""
                for chunk in generate_landing_page(clients[model], description, model, max_tokens):
                    html_content += chunk
                    yield f'data: {{"model": "{model}", "chunk": {json.dumps(chunk)}}}\n\n'

                yield f'data: {{"model": "{model}", "status": "complete", "html": {json.dumps(html_content)}}}\n\n'

        return Response(generate_all(), mimetype="text/event-stream")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
