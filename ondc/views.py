from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime
import uuid, json, os, requests
from datetime import datetime

from .models import Transaction, Message  # your Django models
from .cryptic_utils import create_authorisation_header  # assuming this is your custom utility

class ONDCSearchView(APIView):
    def post(self, request):
        # Generate IDs and timestamp
        transaction_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat(sep="T", timespec="seconds") + "Z"

        # Prepare payload
        payload = {
            "context": {
                "location": {
                    "country": {"code": "IND"},
                    "city": {"code": "*"}
                },
                "domain": "ONDC:FIS14",
                "timestamp": timestamp,
                "bap_id": "investment.staging.flashfund.in",
                "bap_uri": "https://investment.staging.flashfund.in/ondc",
                "transaction_id": transaction_id,
                "message_id": message_id,
                "version": "2.0.0",
                "ttl": "PT10M",
                "action": "search"
            },
            "message": {
                "intent": {
                    "category": {
                        "descriptor": {
                            "code": "MUTUAL_FUNDS"
                        }
                    },
                    "fulfillment": {
                        "agent": {
                            "organization": {
                                "creds": [
                                    {"id": "ARN-125784", "type": "ARN"}
                                ]
                            }
                        }
                    },
                    "tags": [
                        {
                            "display": False,
                            "descriptor": {
                                "name": "BAP Terms of Engagement",
                                "code": "BAP_TERMS"
                            },
                            "list": [
                                {
                                    "descriptor": {
                                        "name": "Static Terms (Transaction Level)",
                                        "code": "STATIC_TERMS"
                                    },
                                    "value": "https://buyerapp.com/legal/ondc:fis14/static_terms?v=0.1"
                                },
                                {
                                    "descriptor": {
                                        "name": "Offline Contract",
                                        "code": "OFFLINE_CONTRACT"
                                    },
                                    "value": "true"
                                }
                            ]
                        }
                    ]
                }
            }
        }

        # Store transaction and message
        transaction, _ = Transaction.objects.get_or_create(transaction_id=transaction_id)
        Message.objects.create(
            transaction=transaction,
            message_id=message_id,
            action="search",
            timestamp=parse_datetime(timestamp),
            payload=payload
        )

        # Send to gateway
        request_body_str = json.dumps(payload, separators=(',', ':'))
        auth_header = create_authorisation_header(request_body=request_body_str)

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header,
            "X-Gateway-Authorization": os.getenv("SIGNED_UNIQUE_REQ_ID", ""),
            "X-Gateway-Subscriber-Id": os.getenv("SUBSCRIBER_ID")
        }

        response = requests.post("https://staging.gateway.proteantech.in/search", data=request_body_str, headers=headers)

        return Response({
            "status_code": response.status_code,
            "response": response.json() if response.content else {},
            "sent_headers": headers,
            "sent_body": payload
        }, status=status.HTTP_200_OK)



