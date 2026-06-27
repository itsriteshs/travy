from fastapi.responses import JSONResponse
from typing import Dict, Any

class ErrorResponseService:
    @staticmethod
    def format_error(status_code: int, error_type: str, message: str, details: Any = None) -> JSONResponse:
        content = {
            "success": False,
            "error": {
                "type": error_type,
                "message": message
            }
        }
        if details:
            content["error"]["details"] = details
            
        return JSONResponse(status_code=status_code, content=content)
