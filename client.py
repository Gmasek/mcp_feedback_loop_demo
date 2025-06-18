import httpx
import os


OLLAMA_URL = "http://localhost:11434"


async def query_ollama(prompt: str, model: str = "mistral:7b") -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
            res.raise_for_status()
            return res.json()["response"]
    except httpx.ReadTimeout:
        print("Ollama connection failed maybe not running?")
    except httpx.TimeoutException:
        print("timeout error model took longer then 10s to respond")
