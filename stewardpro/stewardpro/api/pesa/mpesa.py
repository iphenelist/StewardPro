# vodacom M-PESA
from pypesa.vodacom import MPESA

api_key = '<your-api-key>'
public_key = '<open-api-public-key>'

m_pesa = MPESA(api_key=api_key, public_key=public_key)

# Customer to Business payment
parameters = {
    'input_Amount': '1000', # amount to be charged
    'input_Country': 'TZN',
    'input_Currency': 'TZS',
    'input_CustomerMSISDN': '000000000001',
    'input_ServiceProviderCode': '000000',
    'input_ThirdPartyConversationID': 'c9e794e10c63479992a8b08703abeea36',
    'input_TransactionReference': 'T23434ZE3',
    'input_PurchasedItemsDesc': 'Shoes',
}

response = m_pesa.customer2business(parameters)