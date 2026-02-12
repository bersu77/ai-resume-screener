import json
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

SCREENING_PROMPT = """You are an expert AI resume screener. Analyze the following resume against the provided job description.

Return a JSON response with exactly these fields:
- "score": integer from 0 to 100 representing how well the candidate matches the job
- "summary": a 2-3 sentence overall assessment
- "strengths": list of 3-5 key strengths relevant to the job
- "weaknesses": list of 1-3 gaps or missing qualifications
- "recommendation": one of "Strong Match", "Good Match", "Partial Match", or "Weak Match"

Be fair, objective, and base your analysis only on the information provided.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Respond with valid JSON only."""


def screen_resume(resume_text, job_description):
    prompt = SCREENING_PROMPT.format(
        resume_text=resume_text,
        job_description=job_description,
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return result
