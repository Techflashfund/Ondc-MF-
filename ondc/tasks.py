import uuid
import json
import requests
from datetime import datetime
import os
import logging
from django.utils.dateparse import parse_datetime
from .cryptic_utils import create_authorisation_header
from .models import Message

logger = logging.getLogger(__name__)


class SIPFlowManager:
    def __init__(self, transaction, provider, select_payload, bpp_uri):
        self.transaction = transaction
        self.provider = provider
        self.select_payload = select_payload
        self.bpp_uri = bpp_uri

    def start(self):
        try:
            init_resp = self._init()
            if init_resp.status_code != 200:
                logger.error("INIT failed")
                return

            confirm_resp = self._confirm()
            if confirm_resp.status_code != 200:
                logger.error("CONFIRM failed")
                return

            status_resp = self._status()
            if status_resp.status_code != 200:
                logger.error("STATUS failed")
                return

        except Exception as e:
            logger.error(f"Error in SIP flow: {e}", exc_info=True)

    def _build_context(self, action):
        return {
            "domain": "ONDC:FIS14",
            "country": {"code": "IND"},
            "city": {"code": "*"},
            "action": action,
            "core_version": "2.0.0",
            "bap_id": "investment.staging.flashfund.in",
            "bap_uri": "https://investment.staging.flashfund.in/ondc",
            "bpp_id": self.select_payload["context"]["bpp_id"],
            "bpp_uri": self.select_payload["context"]["bpp_uri"],
            "transaction_id": self.select_payload["context"]["transaction_id"],
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            "ttl": "PT10M"
        }

    def _post_to_bpp(self, endpoint, action, message_data):
        context = self._build_context(action)
        payload = {
            "context": context,
            "message": message_data
        }

        Message.objects.create(
            transaction=self.transaction,
            message_id=context["message_id"],
            action=action,
            timestamp=parse_datetime(context["timestamp"]),
            payload=payload
        )

        body_str = json.dumps(payload, separators=(',', ':'))
        auth_header = create_authorisation_header(body_str)

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header,
            "X-Gateway-Authorization": os.getenv("SIGNED_UNIQUE_REQ_ID", ""),
            "X-Gateway-Subscriber-Id": os.getenv("SUBSCRIBER_ID")
        }

        full_url = f"{self.bpp_uri}/{endpoint}"
        response = requests.post(full_url, headers=headers, data=body_str)
        logger.info(f"{action.upper()} response: {response.status_code}, {response.text}")
        return response

    def _init(self):
        # Use same message.order as /select
        order = self.select_payload["message"]["order"]
        return self._post_to_bpp("init", "init", {"order": order})

    def _confirm(self):
        # Reuse same order structure
        order = self.select_payload["message"]["order"]
        return self._post_to_bpp("confirm", "confirm", {"order": order})

    def _status(self):
        order_id = str(uuid.uuid4())  # You can use actual order_id if available
        return self._post_to_bpp("status", "status", {"order_id": order_id})
