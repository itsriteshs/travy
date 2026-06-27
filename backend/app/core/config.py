import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Base directory is the workspace root
BASE_DIR = Path(__file__).resolve().parents[3]
env_path = BASE_DIR / ".env"

# Load env variables
load_dotenv(dotenv_path=env_path)

class Settings:
    OTARI_BASE_URL: str = os.getenv("OTARI_BASE_URL", "https://api.otari.ai/v1")
    OTARI_API_KEY: str = os.getenv("OTARI_API_KEY", "")
    OTARI_MODE: str = os.getenv("OTARI_MODE", "connected")
    
    OTARI_LOCAL_LLM_MODEL: str = os.getenv("OTARI_LOCAL_LLM_MODEL", "")
    OTARI_CHEAP_MODEL: str = os.getenv("OTARI_CHEAP_MODEL", "")
    OTARI_BALANCED_MODEL: str = os.getenv("OTARI_BALANCED_MODEL", "")
    OTARI_STRONG_MODEL: str = os.getenv("OTARI_STRONG_MODEL", "")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./travy.db")
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    NEXT_PUBLIC_BACKEND_URL: str = os.getenv("NEXT_PUBLIC_BACKEND_URL", "http://localhost:8080")

    def validate_models(self):
        pricing_path = BASE_DIR / "config" / "model-pricing.json"
        if not pricing_path.exists():
            raise FileNotFoundError(f"Model pricing config not found at {pricing_path}")
        with open(pricing_path, "r") as f:
            pricing = json.load(f)
        
        valid_model_names = set(pricing.keys())
        
        model_vars = {
            "OTARI_LOCAL_LLM_MODEL": self.OTARI_LOCAL_LLM_MODEL,
            "OTARI_CHEAP_MODEL": self.OTARI_CHEAP_MODEL,
            "OTARI_BALANCED_MODEL": self.OTARI_BALANCED_MODEL,
            "OTARI_STRONG_MODEL": self.OTARI_STRONG_MODEL,
        }
        
        for var_name, value in model_vars.items():
            if not value:
                raise ValueError(f"{var_name} is not set in environment.")
            
            if ":" not in value:
                raise ValueError(f"{var_name} must have a provider prefix format 'provider:model_name', got '{value}'")
            
            provider, model_name = value.split(":", 1)
            model_name_lower = model_name.lower()
            mapped_key = None
            
            # Check direct match
            if model_name_lower in valid_model_names:
                mapped_key = model_name_lower
            else:
                # Substring check
                for key in valid_model_names:
                    if key in model_name_lower or model_name_lower in key:
                        mapped_key = key
                        break
                
                # Fallback fuzzy checks
                if not mapped_key:
                    if "gemma" in model_name_lower:
                        mapped_key = "gemma-3-27b-it"
                    elif "qwen" in model_name_lower:
                        mapped_key = "qwen-2.5-32b"
                    elif "llama" in model_name_lower:
                        mapped_key = "llama-3.3-70b"
            
            if not mapped_key:
                raise ValueError(
                    f"Model '{model_name}' configured in {var_name} is not defined in config/model-pricing.json. "
                    f"Allowed: {valid_model_names}"
                )

settings = Settings()
settings.validate_models()
