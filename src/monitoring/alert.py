# src/alert.py
from prefect.blocks.notifications import MicrosoftTeamsWebhook
# src/alert.py
import requests
import json

TEAMS_WEBHOOK_URL = "https://gizasystems.webhook.office.com/webhookb2/7951b4ae-e952-4381-9659-dd46de80598d@526b8ab1-b977-4460-8087-39fd2ef8859e/IncomingWebhook/cb641efc14544a8fb4962a4e23d9273b/dee9b87e-980b-4f73-ba92-90860aafaa97/V2k4Nj0PiuMf-FMfdtoCbDjcr6vXG1phCkqwoS5CwaUsA1"

def send_teams_alert(message: str):
    """
    Sends a message to Microsoft Teams using a direct webhook call.
    """
    payload = {
        "text": message
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(TEAMS_WEBHOOK_URL, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        raise ValueError(f"Failed to send Teams alert: {response.status_code}, {response.text}")
