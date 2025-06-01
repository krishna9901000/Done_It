from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd
import logging
import time

import threading
from jobspy_scraper import scrape_jobspy_jobs


from dotenv import load_dotenv
from pyngrok import ngrok
from twilio.rest import Client
import os
from pyngrok import conf

load_dotenv(".env")

# Your Twilio credentials (use env variables or .env for safety)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER_SID = os.getenv("TWILIO_PHONE_NUMBER_SID")  # e.g. 'PNxxxxxxxxxx'
conf.get_default().auth_token= os.getenv("NGROK_AUTH_TOKEN")

def start_ngrok_and_set_webhook():
    

    # Update webhook in Twilio
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.incoming_phone_numbers(TWILIO_PHONE_NUMBER_SID).update(
    sms_url=f"https://squirrel-relaxed-tahr.ngrok-free.app/",
    sms_method="POST")




app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whatsapp_bot")

registered_users = set()

def send_notifications():
    while True:
        try:
            
            df2 = pd.read_csv("jobs_jobspy.csv")
            if df2.empty:
                message = "🚫 No internships available right now."
            else:
                jobs = []
                
                for job in list(df2.itertuples(index=False))[:5]:
                                        jobs.append(
                            f"📌 *{job.title}*\n"
                            f"🏢 {job.company}\n"
                            f"📍 {job.location}\n"
                            f"🔗 {job.job_url}\n"
                        )
                final_message = "\n\n".join(jobs)

                for user in registered_users:
                    # Here, use Twilio API to send message to `user`
                    logger.info(f"Sending jobs to {user}")
                    print(f"To: {user}\n{final_message}")
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
        time.sleep(600)  # wait for 10 minutes

import threading

@app.on_event("startup")
async def load_jobs():
    scrape_jobspy_jobs()
    start_ngrok_and_set_webhook()
    thread = threading.Thread(target=send_notifications, daemon=True)
    thread.start()


@app.post("/")
async def whatsapp_reply(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()
    incoming_msg = form.get("Body", "").strip().lower()
    sender = form.get("From", "")

    logger.info(f"Received message from {sender}: {incoming_msg}")
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg == "register":
        if sender not in registered_users:
            registered_users.add(sender)
            msg.body("👋 Welcome! You’ve been registered. You’ll start receiving job updates every 10 minutes.")
        else:
            msg.body("✅ You are already registered.")
    elif incoming_msg == "get_notification":
        try:
            
            df2 = pd.read_csv("jobs_jobspy.csv")
            jobs = []
            for job in list(df2.itertuples(index=False))[:5]:
                jobs.append(
                            f"📌 *{job.title}*\n"
                            f"🏢 {job.company}\n"
                            f"📍 {job.location}\n"
                            f"🔗 {job.job_url}\n"
                        )
            final_message = "\n\n".join(jobs)
            msg.body(final_message)
        except Exception as e:
            logger.error(f"Error: {e}")
            msg.body("🚫 Error retrieving jobs.")
    else:
        msg.body("🤖 Hi! Send 'register' to get started or 'get_notification' to receive job updates now.")

    
    return Response(content=str(resp), media_type="application/xml")
