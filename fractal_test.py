#Loading environment variables

import requests
import json
from ast import literal_eval
import pandas as pd

#Set API Key from App created
api_key = "qELMDLtbGG8xfrtxNbQNI3zltK2lnUzk4fgJTLsx"

#Load JSON environment variable file
with open('fractalpostmanenv.json') as file:
    data = json.load(file)

env_variables = data['values']

#Set environment variables
for auth_var in env_variables:
    for a in auth_var.items():
        if (a[0] == 'key' and a[1] == 'x-partner-id'):
            partner_id = auth_var['value']
        
        if (a[0] == 'key' and a[1] == 'x-api-key'):
            auth_var['value'] = api_key
            
        if (a[0] == 'key' and a[1] == 'bankId'):
             bankId = auth_var['value']
            
        if (a[0] == 'key' and a[1] == 'companyId'):
             companyId = auth_var['value']

        if (a[0] == 'key' and a[1] == 'accountId'):
            accountId = auth_var['value']

# GET access token function
def fetch_access_token(api_key, partner_id):

    AUTH_ENDPOINT = "https://7gq3bccyoa.execute-api.eu-west-1.amazonaws.com/v1/token"
    auth_headers = {
        
        'Accept': "application/json",
        'Content-Type': "application/json",
        'x-api-key': api_key,
        'x-partner-id': partner_id

        }

    auth_response = requests.post(url = AUTH_ENDPOINT, headers=auth_headers)

    if auth_response.status_code == 201:

        auth_response_text = auth_response.text
        auth_response_dict = literal_eval(auth_response_text)
        access_token = "Bearer " + auth_response_dict["access_token"]
        return (auth_response.status_code, access_token)

    else:
        return (auth_response.status_code, auth_response.text)   

#Retrieve bank transactions function
def get_bank_trans(api_key, partner_id, bankId, companyId, token, acc_id):

    BANK_TRANS_URL = "https://r7p2rhg4ji.execute-api.eu-west-1.amazonaws.com/v1/banking/{}/accounts/{}/transactions".format(bankId, acc_id)

    querystring_bank_trans = {"companyId":companyId}

    headers_bank_trans = {
        'Accept': "application/json",
        'Content-Type': "application/json",
        'x-api-key': api_key,
        'x-partner-id': partner_id,
        'Authorization': token

        }

    response_bank_trans = requests.request("GET", BANK_TRANS_URL, headers=headers_bank_trans, params=querystring_bank_trans)

    if response_bank_trans.status_code == 200:

        bank_trans_data = response_bank_trans.json()
        bank_trans_results = pd.DataFrame(bank_trans_data['results'])

        bank_trans_results_df = pd.concat([bank_trans_results.drop(['merchant'], axis=1), bank_trans_results.merchant.apply(pd.Series)], axis=1)
        bank_trans_results_df = bank_trans_results_df.rename(columns={'name':'Merchant Name'})
        return (response_bank_trans.status_code, bank_trans_results_df)

    else:
        return (response_bank_trans.status_code, response_bank_trans.text)






#Function call to fetch JWT authorization token
auth_code, token = fetch_access_token(api_key, partner_id)

if auth_code == 201:

    #Function call to retreive banking transactions
    bank_trans_code, bank_trans_message = get_bank_trans(api_key, partner_id, bankId, companyId, token, accountId)

    if bank_trans_code == 200:

        #Save transactions deatils in current directory
        bank_trans_message.to_html('bank_trans.html')
        bank_trans_message.to_csv('bank_trans.csv')
        print ("Following files have been saved in current directory:  bank_trans.csv AND bank_trans.html")
    
    else:

        print ("Banking Transaction Token Response Code:   ", bank_trans_code,'\n')
        print ("Check the request call to retreive transactions.....Banking Transaction Response Message:   ", bank_trans_message)

else:
    print ("JWT Authorizaion Token Response Code:   ", auth_code,'\n')
    print ("Check the request call for authorization token.....JWT Authorization Token Response Message:  ", token)
