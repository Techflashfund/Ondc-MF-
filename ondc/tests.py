#     def post(self,request,*args,**kwargs):
#         transaction_id=request.data.get('transaction_id')
#         bpp_id = request.data.get('bpp_id')
#         bpp_uri = request.data.get('bpp_uri')

#         if not all([transaction_id, bpp_id, bpp_uri]):
#             return Response({"error": "Missing transaction_id, bpp_id, or bpp_uri"}, 
#                           status=status.HTTP_400_BAD_REQUEST)
        
#         obj=get_object_or_404(SelectSIP,payload__context__bpp_id=bpp_id,payload__context__bpp_uri=bpp_uri,transaction__transaction_id=transaction_id)
#         message_id = str(uuid.uuid4())
#         timestamp = datetime.utcnow().isoformat(sep="T", timespec="milliseconds") + "Z"

#         try:
#             provider=obj.payload['message']['order']['provider']
#             item=obj.payload['message']['order']['items']
#             fulfillments=obj.payload['message']['order']['fulfillments']
#             xinput=obj.payload["message"]["order"]["xinput"]
#             url = obj.payload["message"]["order"]["xinput"]["form"]["url"]
#         except (KeyError, TypeError):
#             return Response(
#                 {"error": "Form URL not found in payload"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         payload={
#   "context": {
#     "location": {
#       "country": {
#         "code": "IND"
#       },
#       "city": {
#         "code": "*"
#       }
#     },
#     "domain": "ONDC:FIS14",
#     "timestamp": timestamp,
#     "bap_id": "investment.staging.flashfund.in",
#     "bap_uri": "https://investment.staging.flashfund.in/ondc",
#     "transaction_id": transaction_id,
#     "message_id": message_id,
#     "version": "2.0.0",
#     "ttl": "PT10M",
#     "bpp_id": bpp_id,
#     "bpp_uri":bpp_uri,
#     "action": "select"
#   },
#   "message": {
#     "order": {
#       "provider": {
#         "id": provider['id']
#       },
#       "items": [
#         {
#           "id": item[0]['id'],
#           "quantity": {
#             "selected": {
#               "measure": {
#                 "value": "3000",
#                 "unit": "INR"
#               }
#             }
#           },
#           "fulfillment_ids": [
#             item[0]['fulfillment_ids']
#           ]
#         }
#       ],
#       "fulfillments": [
#         {
#           "id": fulfillments[0]['id'],
#           "type": fulfillments[0]['type'],
#           "customer": {
#             "person": {
#               "id": "pan:arrpp7771n"
#             }
#           },
#           "agent": {
#             "person": {
#               "id": "euin:E52432"
#             },
#             "organization": {
#               "creds": [
#                 {
#                   "id": "ARN-124567",
#                   "type": "ARN"
#                 },
#                 {
#                   "id": "ARN-123456",
#                   "type": "SUB_BROKER_ARN"
#                 }
#               ]
#             }
#           },
#           "stops": [
#             {
#               "time": {
#                 "schedule": {
#                   "frequency": fulfillments[0]["tags"][0]["list"][0]["value"]
#                 }
#               }
#             }
#           ]
#         }
#       ],
#       "xinput": {
#         "form": {
#           "id": xinput['form']['id']
#         },
#         "form_response": {
#           "submission_id": "6547-7456-7235-4386"
#         }
#       },
#       "tags": [
#         {
#           "display": False,
#           "descriptor": {
#             "name": "BAP Terms of Engagement",
#             "code": "BAP_TERMS"
#           },
#           "list": [
#             {
#               "descriptor": {
#                 "name": "Static Terms (Transaction Level)",
#                 "code": "STATIC_TERMS"
#               },
#               "value": "https://buyerapp.com/legal/ondc:fis14/static_terms?v=0.1"
#             },
#             {
#               "descriptor": {
#                 "name": "Offline Contract",
#                 "code": "OFFLINE_CONTRACT"
#               },
#               "value": "true"
#             }
#           ]
#         }
#       ]
#     }
#   }
# }
        
#         user_kyc_data = {
#             "pan": "ABCDE1234F",
#             "dob": "1990-01-01",
#             "email": "user@example.com",
#             "name": "Ravi Kumar",
#             "gender":"Male",
#             "marital_status":"Married",
#             "occupation":"Salaried",
#             "source_of_wealth":"Business",
#             "income_range":"1L to 5L",
#             "cob":"India",
#             "pob":"Kochi"
#         }
#         try:
#             res = requests.post(url, data=user_kyc_data)
#             if res.status_code == 200:
#                 resp_json = res.json()
#                 submission_id=resp_json['submission_id']
#                 SubmissionID.objects.create(
#                     trnsaction=transaction_id,
#                     submission_id=submission_id
#                 )
#                 return Response(
#                 {"message": "Form uploaded successfully"},
#                 status=status.HTTP_200_OK
#             )
#             else:
#                 return Response(
#                     {"error": f"Form upload failed with status {res.status_code}"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#         except requests.exceptions.RequestException as e:
#             return Response(
#                 {"error": f"Form upload failed: {str(e)}"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         except Exception as e:
#             return Response(
#                 {"error": f"Unexpected error: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )




        