import logging
import azure.functions as func
import requests  
import json
import os

def main(req: func.HttpRequest) -> func.HttpResponse:


    logging.info('Python HTTP trigger function processed a request.')
  
   
    CLIENT_SECRET = os.environ["CLIENT_CRED"]  
    CLIENT_ID = os.environ["CLIENT_ID"]
    AUTHORITY = os.environ["AUTHORITY"]  

    config = {
    "authority": AUTHORITY,
    "client_id": CLIENT_ID,    
    "client_secret": CLIENT_SECRET
}
        
    from msal import ConfidentialClientApplication
    app = ConfidentialClientApplication(config["client_id"] ,
    authority=config["authority"],
    client_credential=config["client_secret"] )
     
    result = app.acquire_token_for_client(scopes=["https://YOURD365ORG.crm6.dynamics.com/.default"])

    logging.info(result)
   
    bearer_token = extract_token(result)     

    logging.info(bearer_token)

    crmrequestheaders = {
        'Authorization': bearer_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=utf-8'        
    }

                      

    firstname = req.params.get('firstname')
    if not firstname:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            firstname = req_body.get('firstname')

    logging.info(firstname)

    lastname = req.params.get('lastname')
    if not lastname:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            lastname = req_body.get('lastname')    

    logging.info(lastname)           

    if firstname and lastname:
        logging.info('lastname')      
        contactsdata={ "firstname": firstname , "lastname": lastname }
        try:
            crmres = requests.post('https://YOURD365ORG.api.crm6.dynamics.com//api/data/v9.2/contacts', 
                       headers=crmrequestheaders, 
                       data=json.dumps(contactsdata))
            return func.HttpResponse(f"Success: {crmres}")  
        except Exception as e:
            return func.HttpResponse(f"Error, {e}")              
    else:
        return func.HttpResponse(
             "This HTTP triggered function expects two parameters: firstname and lastname.",
             status_code=200
        )

def extract_token(result):
    token_dump = json.dumps(result)
    token_json=json.loads(token_dump)
    msal_token = token_json["access_token"]
    bearer_token = "{} {}".format("Bearer", msal_token)     
    return bearer_token
