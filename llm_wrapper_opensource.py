"""
LLM Wrapper - Support for Open Source Models
Provides abstraction layer for using free, open-source LLMs

Primary: Ollama (local, completely free, no API key needed)
Fallback: HuggingFace Inference API (free tier, cloud-based)

Models supported:
- mistral (7B) - Best balance of speed and quality
- neural-chat (7B) - Optimized for chat/instructions  
- llama2 (7B) - Reliable and powerful
"""

import requests
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class OllamaLLM:
    """
    Local LLM via Ollama - Completely free, runs on your machine
    No API key needed. Fast responses (GPU accelerated if available).
    
    Setup:
    1. Download Ollama from https://ollama.ai
    2. Run: ollama serve (keep running in background)
    3. Pull a model: ollama pull mistral
    4. Set OLLAMA_MODEL=mistral in .env (or use default)
    """
    
    def __init__(self, model: str = "mistral"):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", model)
        self.available = self._check_connection()
        
    def _check_connection(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def ask_ai(self, prompt: str) -> str:
        """
        Send prompt to Ollama and get response
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Generated text response
        """
        if not self.available:
            raise ConnectionError(
                f"❌ Ollama not running at {self.base_url}\n"
                "Start Ollama: ollama serve\n"
                "Or switch to HuggingFace in .env: LLM_PROVIDER=huggingface"
            )
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,  # Wait for complete response
                    "temperature": 0.1,  # Low temp for deterministic queries
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama response timeout - try shorter prompts")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}\n"
                "Make sure Ollama is running: ollama serve"
            )
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")


class HuggingFaceLLM:
    """
    HuggingFace Inference API - Free tier available
    Cloud-based, no local setup needed.
    Requires HUGGINGFACE_API_KEY in .env (get free key at huggingface.co)
    
    Models:
    - mistralai/Mistral-7B-Instruct-v0.1 (recommended)
    - meta-llama/Llama-2-7b-chat-hf
    - NeuralChat-7B
    """
    
    def __init__(self, model: str = "mistralai/Mistral-7B-Instruct-v0.1"):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        self.model = os.getenv("HUGGINGFACE_MODEL", model)
        self.base_url = "https://api-inference.huggingface.co/models"
        
        if not self.api_key:
            raise ValueError(
                "HUGGINGFACE_API_KEY not found in .env\n"
                "Get a free key at: https://huggingface.co/settings/tokens\n"
                "Add to .env: HUGGINGFACE_API_KEY=your_key_here"
            )
    
    def ask_ai(self, prompt: str) -> str:
        """
        Send prompt to HuggingFace and get response
        
        Args:
            prompt: The prompt to send
            
        Returns:
            Generated text response
        """
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(
                f"{self.base_url}/{self.model}",
                headers=headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_length": 1000,
                        "temperature": 0.1,
                    }
                },
                timeout=30
            )
            
            if response.status_code == 429:
                raise RateLimitError("HuggingFace rate limit exceeded - try later")
            
            response.raise_for_status()
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            return str(result)
            
        except requests.exceptions.Timeout:
            raise TimeoutError("HuggingFace response timeout")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Cannot connect to HuggingFace API")
        except Exception as e:
            raise Exception(f"HuggingFace error: {str(e)}")


class Custom_GenAI:
    """
    Main LLM wrapper - Automatically selects best available provider
    
    Priority:
    1. Ollama (local, fastest, no API key)
    2. HuggingFace (free cloud API)
    
    Configuration via .env:
    - LLM_PROVIDER: "ollama" or "huggingface" (auto-detect if not set)
    - OLLAMA_URL: http://localhost:11434 (default)
    - OLLAMA_MODEL: mistral (default)
    - HUGGINGFACE_API_KEY: your API key
    - HUGGINGFACE_MODEL: mistralai/Mistral-7B-Instruct-v0.1 (default)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM - automatically selects provider
        
        Args:
            api_key: Ignored (for backward compatibility with old code)
        """
        self.provider = None
        self.llm = None
        
        # Try Ollama first
        try:
            ollama = OllamaLLM()
            if ollama.available:
                self.provider = "ollama"
                self.llm = ollama
                print(f"✅ Using Ollama ({ollama.model})")
                return
        except Exception as e:
            print(f"⚠️ Ollama not available: {e}")
        
        # Fallback to HuggingFace
        try:
            huggingface = HuggingFaceLLM()
            self.provider = "huggingface"
            self.llm = huggingface
            print(f"✅ Using HuggingFace ({huggingface.model})")
            return
        except Exception as e:
            print(f"⚠️ HuggingFace not available: {e}")
        
        raise Exception(
            "❌ No LLM provider available!\n\n"
            "Setup options:\n"
            "1. Ollama (recommended): https://ollama.ai\n"
            "   - ollama pull mistral\n"
            "   - ollama serve\n\n"
            "2. HuggingFace: Add HUGGINGFACE_API_KEY to .env\n"
            "   - Get free key: https://huggingface.co/settings/tokens"
        )
    
    def ask_ai(self, prompt: str) -> str:
        """
        Get response from LLM
        
        Args:
            prompt: The prompt to send
            
        Returns:
            Generated response text
        """
        if not self.llm:
            raise Exception("LLM not initialized")
        return self.llm.ask_ai(prompt)


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded"""
    pass
