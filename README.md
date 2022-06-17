# PaymentReportAPI
### Generate report request endpoint:
```
Request (content_type: application/json)
POST /report
```
The API takes payment data JSON with various attributes, converts them into a unified report, and then returns them to the user as JSON.
The API also integrates with the https://api.nbp.pl/ to convert payment data in foreign currency to PLN.
#### Example request body:
```
{
        "pay_by_link": [
            {
                "created_at": "2022-05-13T19:12:02.370518+02:00",
                "currency": "EUR",
                "amount": 40000,
                "description": "Car",
                "bank": "idea_bank"
            },

            {
                "created_at": "2022-01-02T11:58:02.370518+07:00",
                "currency": "USD",
                "amount": 9999,
                "description": "Clothing store",
                "bank": "mbank"
            }
        ],
        "dp": [
            {
                "created_at": "2022-03-21T11:32:11.370518+03:00",
                "currency": "PLN",
                "amount": 31700,
                "description": "Restaurant",
                "iban": "PLNOA123435467887653"
            },
            {
                "created_at": "2022-04-21T21:34:11.370518+01:00",
                "currency": "USD",
                "amount": 2200,
                "description": "Toy Store",
                "iban": "GERSXOA86756435435465468"
            }
        ],
        "card": [
            {
                "created_at": "2022-05-21T19:20:02.370518+02:00",
                "currency": "EUR",
                "amount": 2000,
                "description": "Restaurant",
                "cardholder_name": "Jan",
                "cardholder_surname": "Kowalski",
                "card_number": "1234567890000"
            },

            {
                "created_at": "2021-11-21T11:02:02.370518+04:00",
                "currency": "GBP",
                "amount": 200,
                "description": "Ice cream shop",
                "cardholder_name": "Steven",
                "cardholder_surname": "Gerrard",
                "card_number": "11112222333344445555"
            }
        ]
    }
```
#### The response for the example request generated by the API:
```
[
    {
        "date": "2021-11-21T07:02:02.370518Z",
        "type": "card",
        "payment_mean": "Steven Gerrard 1111************5555",
        "description": "Ice cream shop",
        "amount": 200,
        "currency": "GBP",
        "amount_in_pln": 1074
    },
    {
        "date": "2022-01-02T04:58:02.370518Z",
        "type": "pay_by_link",
        "payment_mean": "mbank",
        "description": "Clothing store",
        "amount": 9999,
        "currency": "USD",
        "amount_in_pln": 44450
    },
    {
        "date": "2022-03-21T08:32:11.370518Z",
        "type": "dp",
        "payment_mean": "PLNOA123435467887653",
        "description": "Restaurant",
        "amount": 31700,
        "currency": "PLN",
        "amount_in_pln": 31700
    },
    {
        "date": "2022-04-21T20:34:11.370518Z",
        "type": "dp",
        "payment_mean": "GERSXOA86756435435465468",
        "description": "Toy Store",
        "amount": 2200,
        "currency": "USD",
        "amount_in_pln": 9780
    },
    {
        "date": "2022-05-13T17:12:02.370518Z",
        "type": "pay_by_link",
        "payment_mean": "idea_bank",
        "description": "Car",
        "amount": 40000,
        "currency": "EUR",
        "amount_in_pln": 186568
    },
    {
        "date": "2022-05-21T17:20:02.370518Z",
        "type": "card",
        "payment_mean": "Jan Kowalski 1234*****0000",
        "description": "Restaurant",
        "amount": 2000,
        "currency": "EUR",
        "amount_in_pln": 9328
    }
]
```

### The API also provides an additional endpoint that allows users to save the generated report on the server, as well as query the server for a previously saved report.
#### Generate and save report endpoint:
```
Request (content_type: application/json)
POST /customer-report/[customer-id]
```
##### Retrieve saved report:
```
GET /customer-report/[customer-id]
```
