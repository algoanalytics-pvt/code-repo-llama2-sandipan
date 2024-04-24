import logging
import json
from azure.data.tables import TableServiceClient, TableClient
import azure.functions as func

"""
RequestBody = {  
    "Username": "$USERNAME",
    "Current_Email": "$CURRENT_EMAIL",
    "New_Email": "$NEW_EMAIL" 
}
"""


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    connection_string = "DefaultEndpointsProtocol=https;AccountName=aksha;AccountKey=WqSMmnaicDeMh7QwJPE3DiJ33bhqvtIeVK7vE4KWv2awShMYNjq6Hhp/TPeMVZ/fsQWAqxGaU1xX+AStwX8Qfw==;EndpointSuffix=core.windows.net"
    service = TableClient.from_connection_string(conn_str=connection_string, table_name="usersubscription")

    username = req.params.get('Username')
    current_Email = req.params.get('Current_Email')
    new_Email = req.params.get('New_Email')
    
    if not username:
        try: 
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            username = req_body.get('Username')
            current_Email = req_body.get('Current_Email')
            new_Email = req_body.get('New_Email')
    
    try:
        parameters = {"username":username}
        filter = "UserName eq @username" 
        got_entity = service.query_entities(query_filter=filter, parameters=parameters)
        got_entity = list(got_entity)
        if got_entity:
            record = dict(got_entity[0])
            print(record)
            logging.info(f'upper line. {username} ,{record}')
            if record["UserName"]==username and record["RowKey"]==current_Email:
                
                record["RowKey"] = new_Email
                logging.info(f'Python HTTP trigger function processed a request. {username}')
                service.update_entity(record)
                results = json.dumps({"message": "Email updated Successfully!"})
                return func.HttpResponse(results, mimetype="application/json",status_code=200)
            else:
                results = json.dumps({"message": "Current Email incorrect..."})
                return func.HttpResponse(results, mimetype="application/json",status_code=200)
    except Exception as e:
        logging.info(f"Error in verification module {e}")
        results = json.dumps({"message": f"Error in Email updation {e}"})
        return func.HttpResponse(results, mimetype="application/json",status_code=404)
