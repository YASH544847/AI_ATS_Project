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


def generate_questions(
    company,
    role,
    experience,
    difficulty,
    round_flow,
    topics
):
    """
    Generate interview questions using Groq LLM.
    """

    # Convert pandas Series to text
    if hasattr(topics, "index"):
        topics_text = ", ".join(topics.index.tolist())
    else:
        topics_text = str(topics)

    rounds_text = ", ".join(round_flow)

    prompt = f"""
You are a Senior Software Engineer and Technical Interviewer.

Candidate Details

Company: {company}

Role: {role}

Experience Level: {experience}

Predicted Interview Difficulty: {difficulty}

Interview Flow:
{rounds_text}

Important Topics:
{topics_text}

Generate:

1. 4 Technical Interview Questions

2. 4 HR Interview Questions

3. 4 Behavioral Interview Questions

4. Give preparation tips.

Return the response in proper Markdown format.
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