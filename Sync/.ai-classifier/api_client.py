#!/usr/bin/env python3
import os, json, time, requests

class DeepSeekClient:
    def __init__(self, config):
        self.base_url = config['base_url']
        self.model = config['model']
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 2)
        self.timeout = config.get('timeout', 30)

    def classify(self, system_prompt, user_prompt):
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError('DEEPSEEK_API_KEY not set')
        for attempt in range(self.max_retries):
            try:
                resp = requests.post(
                    f'{self.base_url}/chat/completions',
                    headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                    json={
                        'model': self.model,
                        'messages': [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}],
                        'response_format': {'type': 'json_object'},
                        'temperature': 0.1,
                        'max_tokens': 1000
                    },
                    timeout=self.timeout
                )
                resp.raise_for_status()
                return json.loads(resp.json()['choices'][0]['message']['content'])
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise RuntimeError(f'API call failed: {e}')
