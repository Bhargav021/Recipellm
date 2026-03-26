"""
LLM Fallback Handler - Provides graceful degradation when Gemini API quota is exhausted.
When the API is unavailable, returns template-based responses or cached results.
"""

import json
from pathlib import Path
from typing import Dict, Any

class FallbackLLM:
    """
    Fallback LLM that returns pre-configured responses when quota is exceeded.
    This allows the app to continue functioning with limited capabilities.
    """
    
    # Pre-configured response templates for common queries
    RESPONSE_TEMPLATES = {
        "chicken": {
            "collection": "recipes",
            "query": {"ingredients": {"$regex": "chicken", "$options": "i"}},
            "limit": 5,
            "explanation": "(Fallback: Pre-cached chicken recipes)"
        },
        "pasta": {
            "collection": "recipes",
            "query": {"ingredients": {"$regex": "pasta", "$options": "i"}},
            "limit": 5,
            "explanation": "(Fallback: Pre-cached pasta recipes)"
        },
        "salad": {
            "collection": "recipes",
            "query": {"ingredients": {"$regex": "lettuce|greens", "$options": "i"}},
            "limit": 5,
            "explanation": "(Fallback: Pre-cached salad recipes)"
        },
        "vegetarian": {
            "collection": "recipes",
            "query": {"dietary": "vegetarian"},
            "limit": 5,
            "explanation": "(Fallback: Pre-cached vegetarian recipes)"
        },
    }
    
    @staticmethod
    def get_fallback_response(query: str) -> Dict[str, Any]:
        """
        Returns a fallback response based on query keywords.
        If no matching template, returns helpful error message.
        """
        query_lower = query.lower()
        
        # Try to find a matching template
        for keyword, template in FallbackLLM.RESPONSE_TEMPLATES.items():
            if keyword in query_lower:
                return template
        
        # Default fallback: return generic search instruction
        return {
            "collection": "recipes",
            "query": {},
            "limit": 10,
            "explanation": "(Fallback: Showing all recipes - Gemini API quota exceeded)"
        }
    
    @staticmethod
    def is_quota_error(error_text: str) -> bool:
        """Check if error is related to API quota exhaustion."""
        error_lower = error_text.lower()
        return any(keyword in error_lower for keyword in [
            "429",
            "quota",
            "rate limit",
            "exceeded",
            "limit: 0"
        ])
