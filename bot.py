from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
import logging
import pandas as pd


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whatsapp_bot")

app = FastAPI()

@app.post("/whatsapp")
async def whatsapp_reply(request: Request):
    form = await request.form()
    incoming_msg = form.get('Body', '').strip().lower()
    sender = form.get('From', '')

    logger.info(f"Received message from {sender}: {incoming_msg}")

    # Create Twilio XML response
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg == "get_notification":
        try:
            df1 = pd.read_csv('internships_internshala.csv')
            df2 = pd.read_csv("")
            if df1.empty:
                msg.body("🚫 No internships available right now.")
            else:
                messages = []
                for job in df1.itertuples(index=False):
                    messages.append(
                        f"📌 *{job.Title}*\n🏢 {job.Company}\n📍 {job.Location}\n💰 {job.Stipend}\n🔗 {job.Link}\n"
                    )
                final_message = "\n\n".join(messages[:5])  # Send only first 5 jobs
                msg.body(final_message)
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            msg.body("🚫 Error retrieving internships. Please try again later.")
    return Response(content=str(resp), media_type="application/xml")
