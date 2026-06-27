import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.otari_client import OtariClient
from app.main import app
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_otari_client_success():
    client = OtariClient()
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "travy-ok"
                }
            }
        ]
    }
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        res = await client.generate_completion(
            model="groq:gemma-3-27b-it",
            prompt="Reply with exactly: travy-ok"
        )
        assert res["otari_reachable"] is True
        assert res["response_preview"] == "travy-ok"
        assert res["model"] == "groq:gemma-3-27b-it"
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_otari_client_failure():
    client = OtariClient()
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = Exception("Connection timed out")
        with pytest.raises(Exception, match="Connection timed out"):
            await client.generate_completion(
                model="groq:gemma-3-27b-it",
                prompt="Reply with exactly: travy-ok"
            )
        mock_post.assert_called_once()

def test_api_ai_smoke_mock_success():
    test_client = TestClient(app)
    
    mock_result = {
        "backend": True,
        "otari_reachable": True,
        "model": "groq:gemma-3-27b-it",
        "latency_ms": 123,
        "response_preview": "travy-ok",
        "mode": "live"
    }
    
    with patch("app.services.otari_client.OtariClient.generate_completion", return_value=mock_result) as mock_gen:
        response = test_client.get("/api/ai/smoke")
        assert response.status_code == 200
        assert response.json() == mock_result
        mock_gen.assert_called_once()

def test_api_ai_smoke_mock_failure():
    test_client = TestClient(app)
    
    with patch("app.services.otari_client.OtariClient.generate_completion", side_effect=Exception("API Error")) as mock_gen:
        response = test_client.get("/api/ai/smoke")
        assert response.status_code == 200
        data = response.json()
        assert data["backend"] is True
        assert data["otari_reachable"] is False
        assert data["mode"] == "otari_unavailable"
        assert data["error_type"] == "Exception"
        assert data["safe_fallback_available"] is True
        mock_gen.assert_called_once()

def test_api_ai_models():
    test_client = TestClient(app)
    response = test_client.get("/api/ai/models")
    assert response.status_code == 200
    data = response.json()
    assert "local" in data
    assert "cheap" in data
    assert "balanced" in data
    assert "strong" in data
