CONTEXT={
     "domain": "ONDC:FIS14",
        "timestamp": "2023-05-25T05:23:03.443Z",
        "bap_id": "api.buyerapp.com",
        "bap_uri": "https://api.buyerapp.com/ondc",
        "transaction_id": "a9aaecca-10b7-4d19-b640-b047a7c62196",
        "message_id": "bb579fb8-cb82-4824-be12-fcbc405b6608",
        "version": "2.0.0",
        "ttl": "PT10M",
        "action": "search"

}

select_message={
    "message":{
  "order": {
    "provider": {
      "id": "sellerapp_id"
    },
    "items": [
      {
        "id": "12391",
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
        "id": "ff_123",
        "type": "SIP",
        "customer": {
          "person": {
            "id": "pan:arrpp7771n"
          }
        },
        "agent": {
          "person": {
            "id": "euin:E52432"
          },
          "organization": {
            "creds": [
              {
                "id": "ARN-124567",
                "type": "ARN"
              },
              {
                "id": "ARN-123456",
                "type": "SUB_BROKER_ARN"
              }
            ]
          }
        },
        "stops": [
          {
            "time": {
              "schedule": {
                "frequency": "R6/2024-05-15/P1M"
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