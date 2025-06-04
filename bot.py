
#====Module Imports ======#

from dotenv import load_dotenv
import logging
from jobspy_scraper import scrape_jobspy_jobs
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import Response
import os
import pandas as pd
from pymongo import MongoClient
from pyngrok import ngrok,conf
import re
import time
import threading
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import threading


#====Module Imports ======#




# === LOADING ENVIRONMENT =====#

load_dotenv(".env")

# Your Twilio credentials (use env variables or .env for safety)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER_SID = os.getenv("TWILIO_PHONE_NUMBER_SID")  # e.g. 'PNxxxxxxxxxx'
conf.get_default().auth_token= os.getenv("NGROK_AUTH_TOKEN")
twilio_from = os.getenv("TWILIO_PHONE_NUMBER")
app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whatsapp_bot")
registered_users = set()

# === LOADING ENVIRONMENT =====#






def send_jobs(msg):
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


def price_filter(incoming_msg,msg):
    price_ranges = {
            "₹5k": (0, 5000),
            "₹10k": (5000, 10000),
            "₹10k+": (10000, float("inf")),
        }
    low, high = price_ranges[incoming_msg]
         
    try:
        df = pd.read_csv("jobs_jobspy.csv")
        if "min_amount" not in df.columns:
            msg.body("⚠️ 'salary' column not found in job data.")
        else:
            filtered = df[(df['min_amount'] >= low) & (df['min_amount'] <= high)]
            if filtered.empty:
                msg.body("🚫 No jobs found in that price range.")
            else:
                jobs = []
                for job in list(filtered.itertuples(index=False))[:5]:
                    jobs.append(
                        f"📌 *{job.title}*\n"
                        f"🏢 {job.company}\n"
                        f"📍 {job.location}\n"
                        f"💰 ₹{job.min_amount}\n"
                        f"🔗 {job.job_url}\n"
                    )
                final_message = "\n\n".join(jobs)
                msg.body(final_message)


    except Exception as e:
        logger.error(f"Error filtering jobs: {e}")
        msg.body("🚫 Error filtering jobs.")

def extract_numeric_stipend(stipend_str):
    if pd.isna(stipend_str):
        return 0
    stipend_str = stipend_str.replace(",", "").lower()
    match = re.search(r'₹\s?(\d+)', stipend_str)
    if match:
        return int(match.group(1)),True
    return 0,False


def start_ngrok_and_set_webhook():
    

    # Update webhook in Twilio
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.incoming_phone_numbers(TWILIO_PHONE_NUMBER_SID).update(
    sms_url=f"https://squirrel-relaxed-tahr.ngrok-free.app/",
    sms_method="POST")

    return client




          
    
     
def send_notifications(client):
    while True:
        try:
            MongoDBClient = MongoClient(os.getenv("MONGODB_URI"))  # or your MongoDB URI
            db = MongoDBClient["test"]
            collection = db["users"]

            # Fetch all documents
            documents = list(collection.find())
        

            registered_users = [doc["phone"] for doc in documents if "phone" in doc]
            prefferedRoles = [list(doc["preferredRoles"]) for doc in documents if "preferredRoles" in doc]

            for i,user in enumerate(registered_users):

                Roles = prefferedRoles[i]
                for role in Roles:
                    scrape_jobspy_jobs(role)

                    df2 = pd.read_csv("jobs_jobspy.csv")
                    if df2.empty:
                        message = "🚫 No internships available right now."
                    else:
                        jobs = []
                        
                        for job in list(df2.itertuples(index=False)):
                                                jobs.append(
                                    f"📌 *{job.title}*\n"
                                    f"🏢 {job.company}\n"
                                    f"📍 {job.location}\n"
                                    f"🔗 {job.job_url}\n"
                                )
                        final_message = "\n\n".join(jobs)
                        resp = MessagingResponse()
                        
                        message = client.messages.create(
                            body=final_message,
                            from_=f"whatsapp:+14155238886",
                            to=f"whatsapp:{user}"
                        )
                                
                        logger.info(f"✅ Message sent to {user} | SID: {message.sid}")
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")
             
                    
        time.sleep(14400)  




@app.on_event("startup")
async def load_jobs():
    scrape_jobspy_jobs("SDE")
    client=start_ngrok_and_set_webhook()
    thread = threading.Thread(target=send_notifications(client), daemon=True)
    thread.start()



@app.post("/")
async def whatsapp_reply(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()
    incoming_msg = form.get("Body", "").strip().lower()
    sender = form.get("From", "")
    logger.info(f"Received message from {sender}: {incoming_msg}")
    resp = MessagingResponse()
    msg = resp.message()
    
    
    if incoming_msg == "get_jobs":
         send_jobs(msg)
        
    elif incoming_msg in ["₹5k", "₹10k", "₹10k+"]:
         price_filter(incoming_msg,msg)
        
    elif incoming_msg == "price filter":
        msg.body("Please choose a price range: ₹0–5k, ₹5k–10k, ₹10k+")
    
    elif incoming_msg =="get_user_data":
         pass
    
    else:
        msg.body("❓ Unknown command. Try:\n- register\n- get_notification\n- price filter")

    
    return Response(content=str(resp), media_type="application/xml")
