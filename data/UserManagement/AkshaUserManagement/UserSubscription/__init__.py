import logging
import json
from azure.data.tables import TableServiceClient, TableClient
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    connection_string = "DefaultEndpointsProtocol=https;AccountName=aksha;AccountKey=WqSMmnaicDeMh7QwJPE3DiJ33bhqvtIeVK7vE4KWv2awShMYNjq6Hhp/TPeMVZ/fsQWAqxGaU1xX+AStwX8Qfw==;EndpointSuffix=core.windows.net"
    service = TableClient.from_connection_string(conn_str=connection_string, table_name="usersubscription")
    
    subscription = req.params.get('subscription')
    email = req.params.get('email')
    mac_id= req.params.get('mac')

    if not email:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            email = req_body.get('email')
            subscription = req_body.get('subscription')
            mac_id = req_body.get('mac')
    try:
        got_entity = service.get_entity(partition_key=str(subscription), row_key=str(email))
        
        record = dict(got_entity)
        
        
        if record['Status']:
            if record['MAC_Address'] == mac_id:
                results = json.dumps({"Service":"Running", "ServiceValidity":str(record['ServiceValidity'])})
            else:
                results = json.dumps({"Service":"Expired", "ServiceValidity":str(record['ServiceValidity'])})    
        elif not record['Status']:
            results = json.dumps({"Service":"Expired", "ServiceValidity":str(record['ServiceValidity'])})
           
    except Exception as e:
        results = json.dumps({"Service":"Invalid", "ServiceValidity":"NA"})   
    return func.HttpResponse(results, mimetype="application/json",status_code=200)


