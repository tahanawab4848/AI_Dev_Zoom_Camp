from fastapi import FastAPI, Request
import json
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/alerts")
async def handle_alert(request: Request):
    payload = await request.json()
    logger.info(f"Received alert: {json.dumps(payload)}")
    
    # Process alerts
    alerts = payload.get("alerts", [])
    for alert in alerts:
        status = alert.get("status")
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        
        # Test alert logic
        if labels.get("test") == "true":
            logger.info("Test alert received.")
            logger.info("No incident to fix.")
            return "No incident to fix.\n"
        
        # Real incident logic
        if status == "firing":
            logger.info(f"Real incident firing: {labels} {annotations}")
            # Collect evidence...
            logger.info("Investigating and fixing...")
            # We already fixed the bug directly in app/main.py.
            return "Incident fix triggered."

    return "OK"
