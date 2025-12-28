# Free ChatGPT API (Unofficial)

A simple self-hosted API that lets you chat with ChatGPT for free using Playwright to control a browser.

## Quick Start

1. Install dependencies:
   ```bash
   pip install fastapi uvicorn playwright playwright-stealth
   python -m playwright install chromium
   ```

2. Run the server:
   ```bash
   uvicorn chatgpt:app --reload
   ```

3. Send a message:
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello, how are you?"}'
   ```

   Response example:
   ```json
   {"response": "Hi! I'm doing great, thanks for asking..."}
   ```
