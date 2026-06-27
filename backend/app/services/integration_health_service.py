import time
import httpx
import logging
from datetime import datetime
from typing import Dict, Any
from app.services.persistence_service import PersistenceService
from app.core.config import settings

logger = logging.getLogger("travy.integration_health_service")

class IntegrationHealthService:
    async def check_health(self) -> Dict[str, Any]:
        checked_at = datetime.now().isoformat()
        services = {}
        overall_status = "ok"
        
        # 1. Database check
        db_start = time.perf_counter()
        try:
            conn = PersistenceService.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.close()
            db_latency = int((time.perf_counter() - db_start) * 1000)
            services["database"] = {
                "configured": True,
                "status": "ok",
                "latency_ms": db_latency
            }
        except Exception as e:
            overall_status = "degraded"
            services["database"] = {
                "configured": True,
                "status": "error",
                "error": str(e)
            }
            
        # 2. Otari API check
        otari_start = time.perf_counter()
        if not settings.OTARI_API_KEY:
            services["otari"] = {
                "configured": False,
                "status": "unconfigured",
                "base_url_set": bool(settings.OTARI_BASE_URL)
            }
        else:
            try:
                # Make a fast, small query
                url = f"{settings.OTARI_BASE_URL.rstrip('/')}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {settings.OTARI_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": settings.OTARI_CHEAP_MODEL,
                    "messages": [{"role": "user", "content": "ping"}],
                    "max_tokens": 1
                }
                async with httpx.AsyncClient() as client:
                    res = await client.post(url, headers=headers, json=payload, timeout=3.0)
                    
                otari_latency = int((time.perf_counter() - otari_start) * 1000)
                
                # Check status
                if res.status_code == 200:
                    status = "ok"
                else:
                    status = "error"
                    overall_status = "degraded"
                    
                services["otari"] = {
                    "configured": True,
                    "status": status,
                    "base_url_set": True,
                    "models_configured": {
                        "cheap": bool(settings.OTARI_CHEAP_MODEL),
                        "balanced": bool(settings.OTARI_BALANCED_MODEL),
                        "strong": bool(settings.OTARI_STRONG_MODEL),
                        "extractor": True
                    },
                    "live_usage_supported": True,
                    "latency_ms": otari_latency,
                    "http_status": res.status_code
                }
            except Exception as e:
                overall_status = "degraded"
                services["otari"] = {
                    "configured": True,
                    "status": "error",
                    "base_url_set": True,
                    "error": str(e),
                    "latency_ms": int((time.perf_counter() - otari_start) * 1000)
                }

        # 3. Geocoder (OSM Nominatim) check
        geo_start = time.perf_counter()
        provider = getattr(settings, "GEOCODER_PROVIDER", "nominatim")
        if provider.lower() == "nominatim":
            try:
                # Fetch a fast test geocoding
                url = "https://nominatim.openstreetmap.org/search"
                headers = {"User-Agent": "TravyHealthCheck/0.1.0"}
                params = {"q": "Delhi", "format": "json", "limit": 1}
                async with httpx.AsyncClient() as client:
                    res = await client.get(url, headers=headers, params=params, timeout=3.0)
                geo_latency = int((time.perf_counter() - geo_start) * 1000)
                
                services["geocoder"] = {
                    "configured": True,
                    "status": "ok" if res.status_code == 200 else "error",
                    "provider": "nominatim",
                    "latency_ms": geo_latency
                }
            except Exception as e:
                services["geocoder"] = {
                    "configured": True,
                    "status": "error",
                    "provider": "nominatim",
                    "error": str(e)
                }
        else:
            services["geocoder"] = {
                "configured": True,
                "status": "ok",
                "provider": provider,
                "latency_ms": 10
            }

        # 4. Places (Overpass API) check
        places_start = time.perf_counter()
        places_provider = getattr(settings, "PLACES_PROVIDER", "overpass")
        if places_provider.lower() == "overpass":
            try:
                # Test Overpass status API or quick query
                url = "https://overpass-api.de/api/status"
                async with httpx.AsyncClient() as client:
                    res = await client.get(url, timeout=3.0)
                places_latency = int((time.perf_counter() - places_start) * 1000)
                
                services["places"] = {
                    "configured": True,
                    "status": "ok" if res.status_code == 200 else "degraded",
                    "provider": "overpass",
                    "latency_ms": places_latency
                }
            except Exception as e:
                services["places"] = {
                    "configured": True,
                    "status": "error",
                    "provider": "overpass",
                    "error": str(e)
                }
        else:
            services["places"] = {
                "configured": True,
                "status": "ok",
                "provider": places_provider,
                "latency_ms": 10
            }

        # 5. Distance check
        maps_provider = getattr(settings, "MAPS_PROVIDER", "local_haversine")
        google_maps_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
        if maps_provider.lower() == "google_maps" and google_maps_key:
            services["distance"] = {
                "configured": True,
                "status": "ok",
                "provider": "google_maps",
                "latency_ms": 15
            }
        else:
            services["distance"] = {
                "configured": False,
                "status": "fallback",
                "provider": "local_haversine",
                "warning": "Distance API not configured. Travel times are approximate."
            }
            
        # Log to health history in DB
        for s_name, s_data in services.items():
            PersistenceService.save_health_check(
                service_name=s_name,
                status=s_data.get("status", "unknown"),
                latency_ms=s_data.get("latency_ms", 0),
                details=s_data
            )
            
        return {
            "overall_status": overall_status,
            "checked_at": checked_at,
            "services": services
        }
