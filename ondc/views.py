from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime
import uuid, json, os, requests
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
import logging

from .models import Transaction, Message, FullOnSearch  # your Django models
from .cryptic_utils import create_authorisation_header  # assuming this is your custom utility
from .requestbodies import select_message

class ONDCSearchView(APIView):
    def post(self, request, *args, **kwargs):

        transaction_id = request.data.get('transaction_id')
        message_id = request.data.get('message_id')

        if not transaction_id or not message_id:
            transaction_id = str(uuid.uuid4())
            message_id = str(uuid.uuid4())
        
        timestamp = datetime.utcnow().isoformat(sep="T", timespec="milliseconds") + "Z"


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
            "response": response.json() if response.content else {}
        }, status=status.HTTP_200_OK)



logger = logging.getLogger(__name__)

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



        


    
# SIP Creation

class SIPCreationView(APIView):
         def post(self,request,*args,**kwargs):
             transaction_id = request.data.get('transaction_id')
             bpp_id=request.data.get('bpp_id')
             bpp_uri=request.data.get('bpp_uri')

             if not all([transaction_id,bpp_id,bpp_uri]):
                    return Response({"error":"Missing transaction_id ,bppid,bppuri"},status=status.HTTP_400_BAD_REQUEST)
             
             
             obj = get_object_or_404(
                        FullOnSearch,
                        payload__context__bpp_id=bpp_id,
                        payload__context__bpp_uri=bpp_uri,
                        transaction__transaction_id=transaction_id
                    )
             
             message_id=str(uuid.uuid4())
             timestamp = datetime.utcnow().isoformat(sep="T", timespec="milliseconds") + "Z"
             print(obj.payload)  # Or use logging


             payload={
  "context": {
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "*"
      }
    },
    "domain": "ONDC:FIS14",
    "timestamp": timestamp,
    "bap_id": "investment.staging.flashfund.in",
    "bap_uri": "https://investment.staging.flashfund.in/ondc",
    "transaction_id":transaction_id,
    "message_id":message_id,
    "version": "2.0.0",
    "ttl": "PT10M",
    "bpp_id": bpp_id,
    "bpp_uri": bpp_uri,
    "action": "select"
  },
  "message": {
    "order": {
      "provider": {
        "id": obj.payload["message"]["catalog"]["providers"][0]["id"]
      },
      "items": [
        {
          "id": obj.payload["message"]["order"]["items"][0]["id"],
          "quantity": {
            "selected": {
              "measure": {
                "value": "3000",
                "unit": "INR"
              }
            }
          }
        }
      ],
      "fulfillments": [
        {
          "id": obj.payload["message"]["order"]["fulfillments"][0]["id"],
          "type": obj.payload["message"]["order"]["fulfillments"][0]["type"],
          "customer": {
            "person": {
              "id":  obj.payload["message"]["order"]["fulfillments"][0]["customer"]["person"]["id"]
            }
          },
          "agent": {
            "person": {
              "id": obj.payload["message"]["order"]["fulfillments"][0]["agent"]["person"]["id"]
            },
            "organization": {
              "creds":  obj.payload["message"]["order"]["fulfillments"][0]["agent"]["organization"]["creds"]
            }
          },
          "stops": [
            {
              "time": {
                "schedule": {
                  "frequency": obj.payload["message"]["order"]["fulfillments"][0]["stops"][0]["time"]["schedule"]["frequency"]

                }
              }
            }
          ]
        }
      ],
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
             
             Message.objects.create(
                transaction=transaction_id,
                message_id=message_id,
                action="select",
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

             response = requests.post(f"{bpp_uri}/search", data=request_body_str, headers=headers)

             return Response({
                    "status_code": response.status_code,
                    "response": response.json() if response.content else {}
                }, status=status.HTTP_200_OK)


                

             
             






logger = logging.getLogger(__name__)

class OnSelectSIPView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            logger.info("Received on_select payload: %s", data)
            print("Received on_select payload:", json.dumps(data, indent=2))

            context = data.get("context", {})
            message_id = context.get("message_id")
            transaction_id = context.get("transaction_id")
            timestamp_str = context.get("timestamp")
            action = context.get("action")

            # Validate context fields
            if not all([message_id, transaction_id, timestamp_str, action]):
                return Response(
                    {"error": "Missing required fields in context"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if action != "on_select":
                return Response(
                    {"error": "Invalid action. Expected 'on_select'"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate timestamp
            timestamp = parse_datetime(timestamp_str)
            if not timestamp:
                return Response(
                    {"error": "Invalid timestamp format"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate transaction
            try:
                transaction = Transaction.objects.get(transaction_id=transaction_id)
            except Transaction.DoesNotExist:
                logger.warning("Transaction not found: %s", transaction_id)
                return Response(
                    {"error": "Transaction not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Validate message.order
            message = data.get("message", {})
            order = message.get("order", {})

            items = order.get("items", [])
            if not items:
                return Response(
                    {"error": "No items in order"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate investment amount
            first_item = items[0]
            selected_quantity = first_item.get("quantity", {}).get("selected", {})
            amount = selected_quantity.get("measure", {}).get("value")
            if not amount or float(amount) <= 0:
                return Response(
                    {"error": "Invalid investment amount"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate fulfillments
            fulfillments = order.get("fulfillments", [])
            if not fulfillments:
                return Response(
                    {"error": "No fulfillments provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate xinput.form.url
            xinput = order.get("xinput", {})
            form_url = xinput.get("form", {}).get("url")
            if not form_url:
                return Response(
                    {"error": "Missing account opening form URL in xinput.form.url"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # If all validations pass
            logger.info("on_select validation passed, sending ACK")
            return Response(
                {
                    "message": {
                        "ack": {
                            "status": "ACK"
                        }
                    }
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error("Failed to process on_select: %s", str(e), exc_info=True)
            return Response(
                {
                    "message": {
                        "ack": {
                            "status": "NACK",
                            "description": "Internal server error"
                        }
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
