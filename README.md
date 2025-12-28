# Free ChatGPT API (Unofficial)

A simple self-hosted API that lets you chat with ChatGPT for free using Playwright to control a real browser session.

## Quick Start

```bash
git clone https://github.com/mahdi-marjani/free-llm-api.git
cd free-llm-api
```

### 1. Set up a virtual environment (recommended)

```bash
python -m venv venv

# Activate it
# On Linux / macOS
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn playwright playwright-stealth

# Install browser (Chromium)
playwright install chromium
```

### 3. Run the server

```bash
uvicorn chatgpt:app
```

### 4. Send a message

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?"}'
```

Example response:
```json
{"response": "Hi! I'm doing great, thanks for asking..."}
```

Enjoy your free LLM API! 🚀
