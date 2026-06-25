from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Read API Key
api_key = os.getenv("GROQ_API_KEY")

# Check if API key exists
if not api_key:
    raise ValueError(
        "❌ GROQ_API_KEY not found. Please create a .env file and add:\n"
        "GROQ_API_KEY=your_groq_api_key"
    )

# Create Groq client
client = Groq(api_key=api_key)


def generate_questions(prompt):
    """
    Generate interview questions using Groq LLM.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=2500,
    )

    return response.choices[0].message.content