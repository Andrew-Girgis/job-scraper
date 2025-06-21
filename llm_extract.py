# llm_extract.py  –  works with openai>=1.0
import os, json, asyncio
from openai import AsyncOpenAI, APITimeoutError
from dotenv import load_dotenv; load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a data-mining assistant. Extract up to 12 REQUIRED skills from
the job description. Output strict JSON, no comments or extra keys:

{
  "required_skills": [
    "skill 1",
    "skill 2",
    ...
  ]
}
Assume skills are single concepts (e.g., "Python", "A/B testing",
"SQL", "Snowflake"). Do not invent skills that aren't in the text.
"""

async def extract_required_skills(text: str) -> list[str] | None:
    try:
        response = await client.chat.completions.create(
            model="gpt-4.1-nano",
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.strip()},
                {"role": "user",   "content": text[:12_000]}
            ],
            timeout=30  # seconds
        )
        data = json.loads(response.choices[0].message.content)
        return data.get("required_skills")
    except (APITimeoutError, Exception) as e:
        print("⚠️ LLM extract failed:", e)
        return None
