# fis/utils.py
import uuid
from datetime import datetime, timezone

def generate_context(transaction_id=None, action="search"):
    return {
        "domain": "ONDC:FIS14",
        "location": {
            "country": {"code": "IND"},
            "city": {"code": "std:487"}  # Replace * with a valid code
        },
        "bap_id": "investment.staging.flashfund.in",
        "bap_uri": "https://investment.staging.flashfund.in/ondc",
        "version": "2.0.0",
        "ttl": "PT10M",
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "transaction_id": transaction_id or str(uuid.uuid4()),
        "message_id": str(uuid.uuid4())
    }

def generate_search_payload(transaction_id=None):
    return {
        "context": generate_context(transaction_id, action="search"),
        "message": {
            "intent": {
                "category": {"descriptor": {"code": "MUTUAL_FUNDS"}},
                "fulfillment": {
                    "agent": {
                        "organization": {
                            "creds": [{"id": "ARN-125784", "type": "ARN"}]
                        }
                    }
                },
                "tags": [
                    {
                        "display": False,
                        "descriptor": {"name": "BAP Terms of Engagement", "code": "BAP_TERMS"},
                        "list": [
                            {
                                "descriptor": {"name": "Static Terms (Transaction Level)", "code": "STATIC_TERMS"},
                                "value": "https://buyerapp.com/legal/ondc:fis14/static_terms?v=0.1"
                            },
                            {
                                "descriptor": {"name": "Offline Contract", "code": "OFFLINE_CONTRACT"},
                                "value": "true"
                            }
                        ]
                    }
                ]
            }
        }
    }
