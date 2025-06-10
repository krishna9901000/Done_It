from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk

import os
import requests
import openai
from tqdm import tqdm
import fitz  # PyMuPDF
import pandas as pd
from groq import Groq


GROQ_API_KEY=os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-8b-8192"
from pymongo import MongoClient
from datetime import datetime


# Connect to MongoDB (adjust the URI as needed)
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["resume_db"]
resume_collection = db["resumes"]



def store_resume_in_mongodb(phone_number, resume_text):
    resume_collection.update_one(
        {"phone_number": phone_number},
        {
            "$set": {
                "resume_text": resume_text,
                "timestamp": datetime.now()
            }
        },
        upsert=True  # Insert if not found
    )

def extract_text_from_pdf(url: str,sender):
    response = requests.get(
        url,
        auth=(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    )
    

    if response.status_code != 200:
        raise Exception("Failed to download file from Twilio. Status code: " + str(response.status_code))
    
    with open("resume.pdf", "wb") as f:
        f.write(response.content)
    
    doc = fitz.open("resume.pdf")  # no need for "r" mode
    text = ""
    for page in doc:
        text += page.get_text()
    
    try:
        store_resume_in_mongodb(resume_text=text,phone_number=sender)
    except:
        print("Error saving resume in the database")
    finally:
        return text

nltk.download("punkt")

def extract_keywords(text):
    text = str(text).lower()
    words = nltk.word_tokenize(text)
    keywords = [w for w in words if w.isalpha()]
    return list(set(keywords))

# Function to generate JD using OpenAI
def generate_description(title):
    prompt = f"Write a detailed job description for the job title: '{title}'. Include roles, responsibilities, and required qualifications."
        
        

    client = Groq()
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
         {
        "role": "system",
        "content": "Your role is as a hr is to create a job description for the job title"
        },
        {
            "role": "user",
            "content": prompt
        }
        ],
        temperature=0.7,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    response=""
    for chunk in completion:
        response+=(chunk.choices[0].delta.content or "") 
    
    return response


def fillnulls(job_df):

    # Fill missing descriptions with AI-generated content
    descriptions = []
    for idx, row in tqdm(job_df.iterrows(), total=len(job_df)):
        title = row["title"] if pd.notnull(row["title"]) else ""
        desc = row["description"] if pd.notnull(row["description"]) and row["description"].strip() else ""
        
        if not desc and title.strip():
            desc = generate_description(title)
        
        descriptions.append(desc)
    
    # Combine title and (original or generated) description
    job_descriptions = (job_df["title"].fillna("").astype(str) + " " + pd.Series(descriptions).fillna("").astype(str)).str.lower().tolist()

    return job_descriptions




def score_resume(resume_text, job_df):
    resume_keywords = extract_keywords(resume_text)
    
    # For simplicity: join job descriptions
    
    job_descriptions = fillnulls(job_df=job_df)
    documents = [" ".join(resume_keywords)] + job_descriptions

    vectorizer = CountVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()

    cosine_sim = cosine_similarity([vectors[0]], vectors[1:])[0]
    best_idx = cosine_sim.argmax()
    best_score = cosine_sim[best_idx] * 100

    print(best_score)
    return best_score, job_df.iloc[best_idx], resume_keywords



def fetch_resume(phone_number: str) -> str:
    """
    Fetch resume details for a phone number.
    Returns formatted text or "not uploaded" message.
    """
    resume = resume_collection.find_one(
        {"phone_number": phone_number},
        sort=[("timestamp", -1)]  # Get latest resume
    )
    
    if resume:
        preview = resume['resume_text'][:100] + "..." if len(resume['resume_text']) > 100 else resume['resume_text']
        return (
            f"📄 **Resume Details**\n"
            f"▸ Phone: {resume['phone_number']}\n"
            f"▸ Last Updated: {resume['timestamp'].strftime('%Y-%m-%d %H:%M')}\n"
            f"▸ Preview: {preview}"
        )
    else:
        return "⚠️ No resume uploaded for this number."
