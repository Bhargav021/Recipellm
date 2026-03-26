# Import from parent directory's open-source LLM wrapper
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_wrapper_opensource import Custom_GenAI

# This module now uses open-source models via Ollama or HuggingFace
# See ../llm_wrapper_opensource.py for configuration



