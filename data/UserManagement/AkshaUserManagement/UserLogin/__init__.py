import logging
import json
from azure.data.tables import TableServiceClient, TableClient
import azure.functions as func

"""
RequestBody = {  
    "Username": "$USERNAME",
    "Password": "$PASSWORD" 
}

ResponseBody = {  
    "Client": "$Subscription" or "",
    "Email": "$Email" or "",
    "Message": "MESSAGE TEXT"
}
"""


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f'Python HTTP trigger function processed a request. {req.get_json()}')

    connection_string = "DefaultEndpointsProtocol=https;AccountName=aksha;AccountKey=WqSMmnaicDeMh7QwJPE3DiJ33bhqvtIeVK7vE4KWv2awShMYNjq6Hhp/TPeMVZ/fsQWAqxGaU1xX+AStwX8Qfw==;EndpointSuffix=core.windows.net"
    service = TableClient.from_connection_string(conn_str=connection_string, table_name="usersubscription")

    username = req.params.get('Username')
    password = req.params.get('Password')
    
    if not username:
        try: 
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            username = req_body.get('Username')
            password = req_body.get('Password')
    try:
        parameters = {"username":username}
        filter = "UserName eq @username" 
        got_entity = service.query_entities(query_filter=filter, parameters=parameters)
        got_entity = list(got_entity)
        if got_entity:
            record = dict(got_entity[0])
            print(record)
            if record["UserName"]:
                if record["UserName"]==username and record["Password"]==password:
                    results = json.dumps({"Email": str(record["RowKey"]), "Client": str(record["PartitionKey"]), "message": "Authentication Successfull!" })
                else:
                    results = json.dumps({"message": "Authentication Failed!"})
            else:
                results = json.dumps({"Email": " ", "Client": " ", "message": "Username or password incorrect, please enter the correct credentials"})
        else:
            results = json.dumps({"Email": " ", "Client": " ", "message":" User record not found, please enter correct username or contact support!"})
        
        return func.HttpResponse(results, mimetype="application/json",status_code=200)
    
    except Exception as e:
        logging.info(f"Error in verification module {e}")
        results = json.dumps({"Email": " ", "Client": " ","message": f"Error in verification module, please provide credentials eg:- username & password!"})
        return func.HttpResponse(results, mimetype="application/json",status_code=404)
