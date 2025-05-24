from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime
import uuid, json, os, requests
from threading import Thread
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
import logging
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ondc.models import Transaction,Message
from ondc.cryptic_utils import create_authorisation_header

from .models import OnIssue



class IGMIssue(APIView):
    def post(self,request,*args,**kwargs):
        transaction_id = request.data.get('transaction_id')
        bpp_id = request.data.get('bpp_id')
        bpp_uri = request.data.get('bpp_uri')

        
        message_id = str(uuid.uuid4())

        if not all([bpp_id,bpp_uri,transaction_id]):
            return Response({"errror":"Seller ID Required"})
        
        timestamp = datetime.utcnow().isoformat(sep="T", timespec="milliseconds") + "Z"

        payload={
                "context": {
                    "domain": "ONDC:FIS14",
                    "location": {
                    "country": {
                        "code": "IND"
                    },
                    "city": {
                        "code": "*"
                    }
                    },
                    "action": "issue",
                    "version": "2.0.0",
                    "bap_id": "investment.staging.flashfund.in",
                    "bap_uri": "https://investment.staging.flashfund.in/igm",
                    "bpp_id": bpp_id,
                    "bpp_uri": bpp_uri,
                    "transaction_id": transaction_id,
                    "message_id": message_id,
                    "timestamp": timestamp,
                    "ttl": "PT30S"
                },
                "message": {
                    "issue": {
                    "id": "1",
                    "category": "FULFILMENT",
                    "sub_category": "FLM01",
                    "complainant_info": {
                        "person": {
                        "name": "Sam Manuel"
                        },
                        "contact": {
                        "phone": "9879879870",
                        "email": "sam@yahoo.com"
                        }
                    },
                    "order_details": {
                        "id": "4597f703-e84f-431e-a96a-d147cfa142f9",
                        "state": "SANCTIONED",
                        "provider_id": "P1"
                    },
                    "description": {
                        "short_desc": "Delay in disbursement/not disbursed",
                        "Long_desc": "Loan not disbursed by the lender",
                        "additional_desc": {
                        "url": "https://buyerapp.com/additonal-details/desc.txt",
                        "content_type": "text/plain"
                        },
                        "images": [
                        "http://buyerapp.com/addtional-details/img1.png",
                        "http://buyerapp.com/addtional-details/img2.png"
                        ]
                    },
                    "source": {
                        "network_participant_id": "buyerapp.com/ondc",
                        "type": "CONSUMER"
                    },
                    "expected_response_time": {
                        "duration": "PT2H"
                    },
                    "expected_resolution_time": {
                        "duration": "P1D"
                    },
                    "status": "OPEN",
                    "issue_type": "ISSUE",
                    "issue_actions": {
                        "complainant_actions": [
                        {
                            "complainant_action": "OPEN",
                            "short_desc": "Complaint created",
                            "updated_at": "2023-01-15T10:00:00.469Z",
                            "updated_by": {
                            "org": {
                                "name": "buyerapp.com::ONDC:FIS12"
                            },
                            "contact": {
                                "phone": "9450394039",
                                "email": "buyerapp@interface.com"
                            }
                            }
                        }
                        ]
                    },
                    "created_at": timestamp,
                    "updated_at": timestamp
                    }
                }
                }
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

        response = requests.post(f"{bpp_uri}/issue", data=request_body_str, headers=headers)

        return Response({
            "status_code": response.status_code,
            "response": response.json() if response.content else {}
        }, status=status.HTTP_200_OK)


logger = logging.getLogger(__name__)

class OnIssueView(APIView):
    def post(self,request,*args,**kwargs):

       
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

            if action != "on_issue":
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


            OnIssue.objects.create(
                transaction=transaction,
                message_id=message_id,
                payload=data,
                timestamp=timestamp
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


