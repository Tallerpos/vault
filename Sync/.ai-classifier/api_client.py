#!/usr/bin/env python3
"""DeepSeek API Client — Resilient Edition.

Features:
- Exponential backoff retry
- Timeout handling
- Rate limit detection
- Detailed error categorization
- Response validation
"""
import os
import json
import time
import logging
import requests

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom error with categorization."""
    def __init__(self, message, category='unknown', retryable=False):
        super().__init__(message)
        self.category = category
        self.retryable = retryable


class DeepSeekClient:
    def __init__(self, config):
        self.base_url = config['base_url'].rstrip('/')
        self.model = config['model']
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 2)
        self.timeout = config.get('timeout', 30)

    def classify(self, system_prompt, user_prompt):
        """Envía prompt al LLM y retorna JSON parseado.
        
        Raises:
            APIError: si falla después de todos los reintentos
            ValueError: si DEEPSEEK_API_KEY no está configurada
        """
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError(
                'DEEPSEEK_API_KEY not set. '
                'Check /etc/ai-classifier.env'
            )

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f'{self.base_url}/chat/completions',
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json',
                    },
                    json={
                        'model': self.model,
                        'messages': [
                            {'role': 'system', 'content': system_prompt},
                            {'role': 'user', 'content': user_prompt},
                        ],
                        'response_format': {'type': 'json_object'},
                        'temperature': 0.1,
                        'max_tokens': 1000,
                    },
                    timeout=self.timeout,
                )

                # Handle HTTP errors
                if response.status_code == 429:
                    # Rate limited — wait longer
                    retry_after = int(response.headers.get('Retry-After', 10))
                    logger.warning(
                        f'Rate limited (429). Waiting {retry_after}s. '
                        f'Attempt {attempt + 1}/{self.max_retries}'
                    )
                    time.sleep(retry_after)
                    continue

                if response.status_code == 401:
                    raise APIError(
                        'Invalid API key', category='auth', retryable=False
                    )

                if response.status_code >= 500:
                    raise APIError(
                        f'Server error {response.status_code}',
                        category='server', retryable=True
                    )

                response.raise_for_status()

                # Parse response
                data = response.json()
                choices = data.get('choices', [])
                if not choices:
                    raise APIError(
                        'Empty choices in response',
                        category='response', retryable=True
                    )

                content = choices[0].get('message', {}).get('content', '')
                if not content:
                    raise APIError(
                        'Empty content in response',
                        category='response', retryable=True
                    )

                # Parse JSON from content
                try:
                    result = json.loads(content)
                except json.JSONDecodeError:
                    # Try to extract JSON from markdown code block
                    import re
                    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```',
                                     content, re.DOTALL)
                    if match:
                        result = json.loads(match.group(1))
                    else:
                        raise APIError(
                            f'Invalid JSON in response: {content[:200]}',
                            category='response', retryable=True
                        )

                # Validate that we got the expected fields
                if not isinstance(result, dict):
                    raise APIError(
                        f'Response is not a dict: {type(result)}',
                        category='response', retryable=True
                    )

                logger.info(
                    f'API call successful. '
                    f'Tags: {result.get("tags", [])}, '
                    f'Category: {result.get("category", "")}'
                )
                return result

            except APIError as e:
                last_error = e
                if not e.retryable:
                    raise
                delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(
                    f'API error ({e.category}): {e}. '
                    f'Retrying in {delay}s. '
                    f'Attempt {attempt + 1}/{self.max_retries}'
                )
                time.sleep(delay)

            except requests.exceptions.Timeout:
                last_error = APIError(
                    f'Request timed out after {self.timeout}s',
                    category='timeout', retryable=True
                )
                delay = self.retry_delay * (2 ** attempt)
                logger.warning(
                    f'Timeout. Retrying in {delay}s. '
                    f'Attempt {attempt + 1}/{self.max_retries}'
                )
                time.sleep(delay)

            except requests.exceptions.ConnectionError as e:
                last_error = APIError(
                    f'Connection error: {e}',
                    category='network', retryable=True
                )
                delay = self.retry_delay * (2 ** attempt)
                logger.warning(
                    f'Connection error. Retrying in {delay}s. '
                    f'Attempt {attempt + 1}/{self.max_retries}'
                )
                time.sleep(delay)

            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        f'Unexpected error: {e}. '
                        f'Retrying in {delay}s. '
                        f'Attempt {attempt + 1}/{self.max_retries}'
                    )
                    time.sleep(delay)
                    continue
                raise RuntimeError(
                    f'API call failed after {self.max_retries} attempts: {e}'
                )

        raise RuntimeError(
            f'API call failed after {self.max_retries} attempts: {last_error}'
        )
