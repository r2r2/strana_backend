import os
import requests


def send_email_to_agent(agent_id, event_id, agent_status):
    SITE_HOST = os.getenv("LK_SITE_HOST")
    EXPORT_CABINET_KEY = os.getenv("EXPORT_CABINET_KEY", default="default_key")

    cabinet_event_webhook_link = f"https://{SITE_HOST}/api/events/send_email_to_agent_from_admin"
    payload = {'data': EXPORT_CABINET_KEY}
    data = {"agent_id": agent_id, "event_id": event_id, "agent_status": agent_status}

    requests.post(cabinet_event_webhook_link, params=payload, json=data)
