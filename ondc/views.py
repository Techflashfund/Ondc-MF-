from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime
import uuid, json, os, requests
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
import logging

from .models import Transaction, Message, FullOnSearch  # your Django models
from .cryptic_utils import create_authorisation_header  # assuming this is your custom utility

class ONDCSearchView(APIView):
    def post(self, request, *args, **kwargs):

        transaction_id = request.data.get('transaction_id')
        message_id = request.data.get('message_id')

        if not transaction_id or not message_id:
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



logger = logging.getLogger(__name__)

# class OnSearchView(APIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             data = request.data  
#             logger.info(" Received on_search callback:\n%s", json.dumps(data, indent=2))
#             print(" Received on_search callback:\n", json.dumps(data, indent=2))
#         except Exception as e:
#             logger.error(" Failed to log on_search data: %s", str(e))
#             return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

#         return Response({"message": "on_search received"}, status=status.HTTP_200_OK)
    
class OnSearchView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data  
            logger.info("Received on_search callback:\n%s", json.dumps(data, indent=2))
            print("Received on_search callback:\n", json.dumps(data, indent=2))

            context = data.get("context", {})
            message_id = context.get("message_id")
            transaction_id = context.get("transaction_id")
            timestamp_str = context.get("timestamp")

            # Validate required fields
            if not all([message_id, transaction_id, timestamp_str]):
                return Response({"error": "Missing required fields in context"}, status=status.HTTP_400_BAD_REQUEST)

            # Parse timestamp
            timestamp = parse_datetime(timestamp_str)
            if not timestamp:
                return Response({"error": "Invalid timestamp format"}, status=status.HTTP_400_BAD_REQUEST)

            # Get related transaction
            try:
                transaction = Transaction.objects.get(transaction_id=transaction_id)
            except Transaction.DoesNotExist:
                return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

            # Save to database
            FullOnSearch.objects.create(
                transaction=transaction,
                message_id=message_id,
                payload=data,
                timestamp=timestamp
            )

        except Exception as e:
            logger.error("Failed to process on_search data: %s", str(e))
            return Response({"error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "on_search received"}, status=status.HTTP_200_OK)


class OnSearchDataView(APIView):
    def post(self, request, *args, **kwargs):
        transaction_id = request.data.get("transaction_id")
        
        if not transaction_id:
            return Response({"error": "Missing transaction_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            search_entries = FullOnSearch.objects.filter(transaction=transaction)

            response_data = []
            for entry in search_entries:
                response_data.append({
                    "message_id": entry.message_id,
                    "timestamp": entry.timestamp,
                    "payload": entry.payload
                })

            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Failed to fetch FullOnSearch data: %s", str(e))
            return Response({"error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ONDCIncrementSearchView(APIView):
    def post(self, request, *args, **kwargs):
        transaction_id = request.data.get('transaction_id')
        message_id = request.data.get('message_id')

        if not transaction_id:
            return Response({"error": "transaction_id and message_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        if not message_id:
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
                # Add your specific message content here
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
        