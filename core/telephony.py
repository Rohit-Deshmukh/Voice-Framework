"""Telephony provider abstraction for the voice testing harness."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class TelephonyProvider(ABC):
    """Defines the interface any telephony provider must implement."""

    provider_name: str

    def __init__(self, provider_name: str) -> None:
        self.provider_name = provider_name

    @abstractmethod
    async def initiate_call(
        self,
        to_number: str,
        from_number: Optional[str],
        test_case_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Kick off an outbound test call and return the provider payload."""

    @abstractmethod
    async def hangup_call(self, call_id: str) -> Dict[str, Any]:
        """Forcefully terminate an in-flight call."""

    @abstractmethod
    async def parse_webhook_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize provider-specific webhook payloads into a common schema."""


class TwilioProvider(TelephonyProvider):
    """Concrete Twilio implementation using the Twilio REST API."""

    def __init__(self, account_sid: str, auth_token: str, default_from_number: str) -> None:
        super().__init__(provider_name="twilio")
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.default_from_number = default_from_number

    async def initiate_call(
        self,
        to_number: str,
        from_number: Optional[str],
        test_case_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        from_number = from_number or self.default_from_number
        payload = {
            "action": "initiate",
            "provider": self.provider_name,
            "to": to_number,
            "from": from_number,
            "test_case_id": test_case_id,
            "metadata": metadata or {},
        }
        try:
            from twilio.rest import Client  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "twilio is required for TwilioProvider. Install with `pip install twilio`."
            ) from exc
        client = Client(self.account_sid, self.auth_token)
        call = client.calls.create(
            to=to_number,
            from_=from_number,
            url=(metadata or {}).get("twiml_url"),
            status_callback=(metadata or {}).get("status_callback"),
        )
        payload.update({"provider_call_id": call.sid})
        return payload

    async def hangup_call(self, call_id: str) -> Dict[str, Any]:
        try:
            from twilio.rest import Client  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "twilio is required for TwilioProvider. Install with `pip install twilio`."
            ) from exc
        client = Client(self.account_sid, self.auth_token)
        call = client.calls(call_id).update(status="completed")
        return {"provider": self.provider_name, "provider_call_id": call.sid, "status": call.status}

    async def parse_webhook_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "call_sid": payload.get("CallSid"),
            "event_type": payload.get("CallStatus"),
            "timestamp": payload.get("Timestamp"),
            "raw": payload,
        }


class ZoomPhoneProvider(TelephonyProvider):
    """Placeholder for future Zoom Phone support."""

    def __init__(self) -> None:
        super().__init__(provider_name="zoom_phone")

    async def initiate_call(
        self,
        to_number: str,
        from_number: Optional[str],
        test_case_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:  # pragma: no cover
        raise NotImplementedError("ZoomPhoneProvider is not implemented yet")

    async def hangup_call(self, call_id: str) -> Dict[str, Any]:  # pragma: no cover
        raise NotImplementedError("ZoomPhoneProvider is not implemented yet")

    async def parse_webhook_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:  # pragma: no cover
        raise NotImplementedError("ZoomPhoneProvider is not implemented yet")


class SIPTrunkProvider(TelephonyProvider):
    """Placeholder for direct SIP trunk integrations."""

    def __init__(self) -> None:
        super().__init__(provider_name="sip_trunk")

    async def initiate_call(
        self,
        to_number: str,
        from_number: Optional[str],
        test_case_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:  # pragma: no cover
        raise NotImplementedError("SIPTrunkProvider is not implemented yet")

    async def hangup_call(self, call_id: str) -> Dict[str, Any]:  # pragma: no cover
        raise NotImplementedError("SIPTrunkProvider is not implemented yet")

    async def parse_webhook_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:  # pragma: no cover
        raise NotImplementedError("SIPTrunkProvider is not implemented yet")
