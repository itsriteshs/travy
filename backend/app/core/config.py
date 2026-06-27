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
    OTARI_TIMEOUT_SECONDS: float = float(os.getenv("OTARI_TIMEOUT_SECONDS", "900"))
    DAILY_BUDGET_USD: float = float(os.getenv("DAILY_BUDGET_USD", "2.0"))
    
    OTARI_LOCAL_LLM_MODEL: str = os.getenv("OTARI_LOCAL_LLM_MODEL", "")
    OTARI_CHEAP_MODEL: str = os.getenv("OTARI_CHEAP_MODEL", "")
    OTARI_BALANCED_MODEL: str = os.getenv("OTARI_BALANCED_MODEL", "")
    OTARI_STRONG_MODEL: str = os.getenv("OTARI_STRONG_MODEL", "")

    LLAMAFILE_BASE_URL: str = os.getenv("LLAMAFILE_BASE_URL", "http://127.0.0.1:8081/v1")
    LLAMAFILE_MODEL: str = os.getenv("LLAMAFILE_MODEL", "local-router")
    LLAMAFILE_API_KEY: str = os.getenv("LLAMAFILE_API_KEY", "")
    ENCODERFILE_BASE_URL: str = os.getenv("ENCODERFILE_BASE_URL", "http://127.0.0.1:8082")
    MCPD_BASE_URL: str = os.getenv("MCPD_BASE_URL", "http://127.0.0.1:8090")
    TRAVY_MCP_STREAMABLE_URL: str = os.getenv("TRAVY_MCP_STREAMABLE_URL", "http://127.0.0.1:8090/mcp")
    ANY_AGENT_MODEL_ID: str = os.getenv("ANY_AGENT_MODEL_ID", "openai:local-router")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./travy.db")
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    NEXT_PUBLIC_BACKEND_URL: str = os.getenv("NEXT_PUBLIC_BACKEND_URL", "http://localhost:8080")
    
    GOOGLE_PLACES_API_KEY: str = os.getenv("GOOGLE_PLACES_API_KEY", "")
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", os.getenv("GOOGLE_PLACES_API_KEY", ""))
    FOURSQUARE_API_KEY: str = os.getenv("FOURSQUARE_API_KEY", "")
    MAPBOX_ACCESS_TOKEN: str = os.getenv("MAPBOX_ACCESS_TOKEN", "")
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    MAPS_PROVIDER: str = os.getenv("MAPS_PROVIDER", "google_maps" if os.getenv("GOOGLE_MAPS_API_KEY") else "local_haversine")
    PLACES_PROVIDER: str = os.getenv("PLACES_PROVIDER", "overpass")
    GEOCODER_PROVIDER: str = os.getenv("GEOCODER_PROVIDER", "nominatim")

    @property
    def weights(self) -> dict:
        weights_path = BASE_DIR / "config" / "weights.json"
        if not weights_path.exists():
            return {
                "budget_fit": 0.15,
                "distance_fit": 0.10,
                "time_fit": 0.10,
                "weather_fit": 0.10,
                "group_fit": 0.10,
                "mood_fit": 0.15,
                "opening_hours_fit": 0.10,
                "safety_fit": 0.10,
                "crowd_fit": 0.05,
                "fatigue_penalty": 0.05,
                "transport_fit": 0.05
            }
        try:
            with open(weights_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}


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
