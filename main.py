import os
import io
from fastapi import FastAPI, UploadFile, File, Form  
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path


from utils import load_csv, summarize_expenses, format_summary_for_gpt, format_goal_prompt

# Load API key
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Fetch the key from the environment and initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
print("API Key Loaded:", bool(api_key))
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment!")

client = OpenAI(api_key=api_key)

# FastAPI app setup
app = FastAPI()

# Allow frontend apps (like Streamlit or React) to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_csv(file: UploadFile = File(...), goal: str = Form(...)):
    contents = await file.read()
    df = load_csv(io.BytesIO(contents))
    
    summary = summarize_expenses(df)
    prompt = format_summary_for_gpt(summary)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful personal finance assistant."},
            {"role": "user", "content": prompt}
        ] 
    )
    tips = response.choices[0].message.content

    # GPT Call 2 – Goal-specific insight
    prompt2 = format_goal_prompt(summary, goal)
    goal_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a financial advisor helping users achieve specific goals."},
            {"role": "user", "content": prompt2}
        ]
    )
    goal_advice = goal_response.choices[0].message.content.strip()

    return {
        "summary": summary,
        "tips": tips,
        "goal_advice": goal_advice
    }
