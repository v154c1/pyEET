# pyEET
Python client for EET

Simple and mosty untested implementation of EET (e-trzby) as defined by Czech Financial Administration (http://www.etrzby.cz/)
It works with all developer certificates from http://www.etrzby.cz/cs/archiv-technicke-specifikace.

Tested on Python 2.7.11 and 3.4.3

The module depends on:
- lxml
- requests
- pyOpenSSL
- pytz

The API is not stable yet and subject to change. 

## Installation
`python setup.py install`

## Basic usage
```python
import eet

eet_client = eet.EET(CERT_PATH, CERT_PASS, 1, 'pokladna1')
payment = eet_client.create_payment('P12321', 3248, test=False)
payment.set_amount(eet.TAX_BASIC, 1000, 210)
result = eet_client.send_payment(payment)
print (result['fik'])
```

The code above assumes that you have path to the PKCS12 certificate stored in `CERT_PATH` and password for this certificate in `CERT_PASS`.

The general workflow is:
- Create instance of eet.EET
- Create an empty payment report using EET.create_payment()
- Add amount for different tax rates using payment.set_amount()
- send payment using EET.payment(payment)
- If there's any error during the communication with servers, an exception is thrown
- The result is a dict, always containing key 'fik'.
  - If fik is None, the EET servers returned an error, you can query it using keys 'kod' and 'message'
  - If fik is not None, then it contains FIK returned from the servers

The code above sends the payments to the EET Playgroud by default. To use different servers (production), use `eet_url` parameter in EET constructor.

