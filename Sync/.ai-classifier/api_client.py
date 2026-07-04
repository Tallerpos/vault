#!/usr/bin/env python3
import os
import json
import time
import hashlib
import requests
from pathlib import Path

CACHE_DIR = Path(__file__).parent / "cache" / "prompts"

class DeepSeekClient:
    def __init__(self, config: dict):
        self.base_url = config["base_url"]
        self.model = config["model"]
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 2)
        self.timeout = config.get("timeout", 30)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def classify(self, system_prompt: str, user_prompt: str) -> dict:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise Exception("DEEPSEEK_API_KEY environment variable not set")
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.3,
                        "max_tokens": 1000
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return json.loads(content)
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise Exception(f"API call failed after {self.max_retries} attempts: {e}")
