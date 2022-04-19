# mono_assessment

## Description

This task receives a list of transactions fetched from Mono's statement API and returns JSON response like the one below

```
{
  "status": "success",
  "data": {
    "group1": {
      "average_number_of_days_between_transactions": 20,
      "transactions": [
        {
          "narration": "-062768- -327662-BLACKBELL RESTAURANT LA  LANG",
          "amount": 500000,
          "type": "debit",
          "date": "2022-02-10T14:06:00.000Z"
        },
        {
          "narration": "USSD -044502- -327662-BLACKBELL RESTAURANT LA  LANG",
              "amount": 100000,
              "type": "debit",
              "date": "2022-03-01T14:06:00.000Z"
        }
      ]
    }
  }
}
```

## Prerequisites
* Python 3.6 and above

## How to use
* git clone [repo](https://github.com/hilariie/mono_assessment/)
* cd mono_assessment
* pip install -r requirements.txt
* python mono_api.py
* enter 127.0.0.1:5049/docs in browser
* paste list of transactions and execute
  * If you don't have list of transactions, go to mono.py, line 103 and copy.
* Download data


## License Type

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
