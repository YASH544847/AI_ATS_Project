from pdf_generator import create_pdf

result = {
    "Total Rounds": 4,
    "Difficulty": "Medium",
    "Round Flow": [
        "Aptitude",
        "Technical",
        "Coding",
        "HR"
    ],
    "Topics": None
}

questions = """
Round 1

1. What is Python?
2. What is SQL?

Round 2

1. Explain OOP.
2. Explain DBMS.
"""

create_pdf(
    "Google",
    "Data Analyst",
    "Fresher",
    result,
    questions
)

print("PDF Created Successfully")