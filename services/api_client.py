"""HTTP client helpers for interacting with the FastAPI service."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx


class VoiceFrameworkClient:
    """Lightweight wrapper around the Voice Framework API."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 15.0,
        api_key: Optional[str] = None,
        api_key_header_name: str = "x-api-key",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_key = api_key
        self.api_key_header_name = api_key_header_name

    def _auth_headers(self) -> Dict[str, str]:
        if not self.api_key:
            return {}
        return {self.api_key_header_name: self.api_key}

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        url = f"{self.base_url}{path}"
        headers = {**self._auth_headers(), **kwargs.pop("headers", {})}
        response = httpx.request(method, url, timeout=self.timeout, headers=headers, **kwargs)
        response.raise_for_status()
        return response

    def list_test_cases(self) -> List[Dict[str, Any]]:
        response = self._request("GET", "/testcases")
        return response.json()

    def list_test_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        response = self._request("GET", "/testruns", params={"limit": limit})
        return response.json()

    def get_test_run(self, run_id: str) -> Dict[str, Any]:
        response = self._request("GET", f"/testruns/{run_id}")
        return response.json()

    def run_test_case(
        self,
        *,
        test_id: str,
        provider: str = "twilio",
        mode: str = "simulation",
        to_number: Optional[str] = None,
        from_number: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "test_id": test_id,
            "provider": provider,
            "mode": mode,
            "metadata": metadata or {},
        }
        if to_number:
            payload["to_number"] = to_number
        if from_number:
            payload["from_number"] = from_number
        response = self._request("POST", "/test/run", json=payload)
        return response.json()
*** End Patch