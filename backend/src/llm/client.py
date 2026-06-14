"""Multi-provider LLM client: Ollama, Groq, OpenAI, DeepSeek."""

import time
from typing import Optional

import httpx
import structlog

from src.config import settings

logger = structlog.get_logger(__name__)


class LLMClient:
    """Universal LLM client supporting Ollama, Groq, OpenAI, and DeepSeek."""

    def __init__(self) -> None:
        self.provider = settings.llm_provider
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature

        if self.provider == "ollama":
            self.base_url = settings.ollama_base_url
            self.model = settings.ollama_model
            logger.info("llm_client_ollama", model=self.model, url=self.base_url)
        elif self.provider == "groq":
            self.api_key = settings.groq_api_key
            self.model = settings.groq_model
            self.base_url = "https://api.groq.com/openai/v1"
            if not self.api_key:
                logger.warning("groq_api_key_not_set", hint="Get free key at groq.com")
            logger.info("llm_client_groq", model=self.model)
        elif self.provider == "deepseek":
            self.api_key = settings.deepseek_api_key
            self.model = settings.deepseek_model
            self.base_url = "https://api.deepseek.com/v1"
            if not self.api_key:
                logger.warning("deepseek_api_key_not_set", hint="Get free key at platform.deepseek.com")
            logger.info("llm_client_deepseek", model=self.model)
        else:
            self.api_key = settings.openai_api_key
            self.model = settings.openai_model
            self.base_url = settings.openai_base_url
            logger.info("llm_client_openai", model=self.model)

    def generate(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        quality_tier: str = "standard",
    ) -> tuple[str, int]:
        start_time = time.time()

        tier_multipliers = {"brief": 0.5, "standard": 1.0, "detailed": 2.0}
        multiplier = tier_multipliers.get(quality_tier, 1.0)
        max_tokens = int(self.max_tokens * multiplier)

        if self.provider == "ollama":
            return self._generate_ollama(query, system_prompt, max_tokens, start_time)
        elif self.provider == "groq":
            return self._generate_groq(query, system_prompt, max_tokens, start_time)
        elif self.provider == "deepseek":
            return self._generate_deepseek(query, system_prompt, max_tokens, start_time)
        else:
            return self._generate_openai(query, system_prompt, max_tokens, start_time)

    def _generate_ollama(
        self, query: str, system_prompt: Optional[str], max_tokens: int, start_time: float
    ) -> tuple[str, int]:
        payload = {
            "model": self.model,
            "prompt": query,
            "system": system_prompt or "You are a helpful assistant.",
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": max_tokens,
            },
        }
        try:
            resp = httpx.post(f"{self.base_url}/api/generate", json=payload, timeout=120.0)
            resp.raise_for_status()
            data = resp.json()
            text = data.get("response", "")
            tokens = data.get("eval_count", len(text.split()) * 2)
            latency_ms = (time.time() - start_time) * 1000
            logger.info("ollama_response", latency_ms=round(latency_ms, 2), tokens=tokens)
            return text, tokens
        except httpx.ConnectError:
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Run: ollama pull {self.model} && ollama serve"
            )
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {e}")

    def _generate_groq(
        self, query: str, system_prompt: Optional[str], max_tokens: int, start_time: float
    ) -> tuple[str, int]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": query},
            ],
            "max_tokens": max_tokens,
            "temperature": self.temperature,
        }
        try:
            resp = httpx.post(
                f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=60.0
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("completion_tokens", max_tokens // 2)
            latency_ms = (time.time() - start_time) * 1000
            logger.info("groq_response", latency_ms=round(latency_ms, 2), tokens=tokens)
            return text, tokens
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise RuntimeError("Groq API key invalid. Get one free at groq.com")
            raise RuntimeError(f"Groq API error: {e}")
        except Exception as e:
            raise RuntimeError(f"Groq generation failed: {e}")

    def _generate_deepseek(
        self, query: str, system_prompt: Optional[str], max_tokens: int, start_time: float
    ) -> tuple[str, int]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": query},
            ],
            "max_tokens": max_tokens,
            "temperature": self.temperature,
        }
        try:
            resp = httpx.post(
                f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=60.0
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("completion_tokens", max_tokens // 2)
            latency_ms = (time.time() - start_time) * 1000
            logger.info("deepseek_response", latency_ms=round(latency_ms, 2), tokens=tokens)
            return text, tokens
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise RuntimeError("DeepSeek API key invalid. Get one free at platform.deepseek.com")
            raise RuntimeError(f"DeepSeek API error: {e}")
        except Exception as e:
            raise RuntimeError(f"DeepSeek generation failed: {e}")

    def _generate_openai(
        self, query: str, system_prompt: Optional[str], max_tokens: int, start_time: float
    ) -> tuple[str, int]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": query},
            ],
            "max_tokens": max_tokens,
            "temperature": self.temperature,
        }
        try:
            resp = httpx.post(
                f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=60.0
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("completion_tokens", max_tokens // 2)
            latency_ms = (time.time() - start_time) * 1000
            logger.info("openai_response", latency_ms=round(latency_ms, 2), tokens=tokens)
            return text, tokens
        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {e}")


_llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
