import httpx
import time
import uuid
import logging
from typing import Dict, Any, Optional
from app.services.persistence_service import PersistenceService

logger = logging.getLogger("travy.base_client")

class BaseClient:
    def __init__(self, provider_name: str, base_url: str):
        self.provider_name = provider_name
        self.base_url = base_url.rstrip("/")

    def _mask_auth_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        if not headers:
            return {}
        masked = {}
        for k, v in headers.items():
            if k.lower() in ["authorization", "api-key", "apikey", "x-api-key"]:
                masked[k] = "REDACTED"
            else:
                masked[k] = v
        return masked

    async def request(
        self,
        method: str,
        path: str,
        request_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Any] = None,
        timeout: float = 15.0,
        retries: int = 0
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        log_id = f"api_call_{uuid.uuid4().hex[:8]}"
        
        start_time = time.perf_counter()
        status_code = "UNKNOWN"
        error_msg = ""
        latency_ms = 0
        response_data = None
        
        # Safe HTTP call
        async with httpx.AsyncClient() as client:
            for attempt in range(retries + 1):
                try:
                    # Use explicit HTTP methods so that mocks (like mock_post) trigger correctly
                    if method.upper() == "POST":
                        response = await client.post(
                            url=url,
                            headers=headers,
                            params=params,
                            json=json_data,
                            timeout=timeout
                        )
                    elif method.upper() == "GET":
                        response = await client.get(
                            url=url,
                            headers=headers,
                            params=params,
                            timeout=timeout
                        )
                    else:
                        response = await client.request(
                            method=method,
                            url=url,
                            headers=headers,
                            params=params,
                            json=json_data,
                            timeout=timeout
                        )
                        
                    status_code = str(response.status_code)
                    latency_ms = int((time.perf_counter() - start_time) * 1000)
                    
                    # Raise for status if not OK
                    response.raise_for_status()
                    
                    try:
                        response_data = response.json()
                    except ValueError:
                        response_data = {"text": response.text}
                    break # Success!
                except Exception as e:
                    latency_ms = int((time.perf_counter() - start_time) * 1000)
                    status_code = "ERROR"
                    error_msg = str(e)
                    if attempt == retries:
                        logger.error(f"API Request to {url} failed after {retries + 1} attempts: {e}")
                    else:
                        time.sleep(0.5) # small pause before retry
                        
        # Save to DB log
        PersistenceService.save_api_call_log(
            log_id=log_id,
            request_id=request_id or "system",
            provider=self.provider_name,
            endpoint_name=path or "root",
            status=status_code,
            latency_ms=latency_ms,
            error_message=error_msg,
            cost_usd=0.0 # to be calculated/updated by the caller if it's an AI model call
        )
        
        if status_code == "ERROR":
            raise httpx.HTTPError(f"{self.provider_name} API call failed: {error_msg}")
            
        return {
            "data": response_data,
            "latency_ms": latency_ms,
            "status_code": status_code,
            "provider": self.provider_name
        }
