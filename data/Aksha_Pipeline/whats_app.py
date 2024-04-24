import json
import requests

def send(link, phone_number):
    try:
        url = f"https://graph.facebook.com/v13.0/107494948909422/messages"
        headers = {
            "Authorization": f"Bearer EAAMuz7x1mk0BAFu7oJIwNaVrvFZCFHIvwAasLLnsRMVldanEZCoQqrb1ZB1RaUrBYyr0nLBpIlfl6xEIR4MZB1w7V3QfKm4VpWQOQIZASxA4JmZA43IJqX0ZAlZAI1iZAlrH3pZBXikXInPnzdTlwrMeF6E6MUz9L9nEXle8PkcFQlzfxWV2wIVnN8",
            'Content-Type': 'application/json'
        }

        data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "image",
        "image": {
            "link" : link,
            "caption":"Aksha Alert"
        }
        }
        rr = requests.post(
            url,
            headers=headers,
            data=json.dumps(data)
        )
        result = "Notification sent on registered whats app number successfully!"
    except Exception as e:
        result = f"Failed to send notification on whats app with error: {e}"

    return result