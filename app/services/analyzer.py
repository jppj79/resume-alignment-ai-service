import instructor
import openai
from fastapi import HTTPException
from ..schemas import AnalysisRequest, AnalysisResponse

aclient  = instructor.patch(openai.AsyncOpenAI())

def _create_analysis_prompt(cv_text: str, jd_text: str) -> str:
    """
    Creates the detailed, structured prompt for the LLM.
    This is a private helper function.
    """
    # Note: The quality of this prompt is critical for the quality of the output.
    # We are instructing the AI to act as a specific persona and to format
    # its output exactly like our Pydantic models.
    return f"""
# ROLE & GOAL
You are a world-class, senior IT recruitment expert with 15+ years of experience. Your task is to provide a critical, data-driven analysis comparing a candidate's CV against a job description (JD). Your output must be structured, actionable, and strictly adhere to the requested JSON format. Do not add any commentary or text outside of the final JSON object.

# CONTEXT
- CV_TEXT: ```{cv_text}```
- JOB_DESCRIPTION_TEXT: ```{jd_text}```

# DETAILED INSTRUCTIONS
Analyze the provided texts and generate a JSON response. The analysis must cover the following points:

1.  **Match Score Calculation**:
    - Evaluate the alignment across three key areas: technical skills, experience, and soft skills, each on a scale of 0-100.
    - Calculate a final, weighted 'overall_score'.
    - Provide a concise 'summary' justifying your scoring.

2.  **Strengths Identification**:
    - List the top, most relevant skills or experiences from the CV that directly match the core requirements of the JD.
    - For each strength, provide a short 'evidence' quote from the CV.

3.  **Skill Gap Detection**:
    - Identify critical, important, or desirable skills mentioned in the JD that are absent or underdeveloped in the CV. A desirable skill may be mentioned as familiarity and Additional knowledge.
    - For each gap, state its 'importance' and provide a 'reason' explaining its relevance to the role based on the JD.

4.  **Learning Path Suggestion**:
    - For the most significant skill gaps, propose a concrete 'recommendation' for improvement (e.g., a specific course, book, or type of project).

5.  **Executive Summary**:
    - Write a concise summary (max 150 words) for the candidate. It should summarize their overall fit, highlight their main selling points, and suggest the most critical area for improvement to become an ideal candidate.

6.  **Learning Potential Assessment**:
    - Based on the candidate's career progression, diversity of technologies used (e.g., working with multiple languages, clouds, or frameworks), and evidence of continuous learning (like certifications or personal projects), assess their potential to learn the missing skills.
    - Provide a 'rating' of High, Medium, or Low.
    - Justify this rating in a 'summary'.
    - List the specific 'evidence' from the CV that supports your conclusion.

# MANDATORY OUTPUT FORMAT
Generate a single JSON object that strictly follows the required schema. Do not include markdown formatting like ```json in your response.
**CRITICAL: All keys in the JSON object MUST be in snake_case (e.g., 'overall_score', 'technical_skills', 'skill_gaps'). Do not use spaces, dashes, or capitalization in the keys. The output must strictly follow the required schema.**
The final JSON object MUST be complete and contain all the sections shown in the example structure below.

**HERE IS AN EXAMPLE of the required structure. Populate all fields with your analysis:**
```json
{{
  "analysis": {{
    "match_score": {{
      "overall_score": 0,
      "breakdown": {{
        "technical_skills": 0,
        "experience": 0,
        "soft_skills": 0
      }},
      "summary": "Your summary of the score goes here."
    }},
    "strengths": [
      {{
        "skill": "A key skill from the CV that matches the JD.",
        "evidence": "A brief quote from the CV as evidence."
      }}
    ],
    "skill_gaps": [
      {{
        "skill": "A skill required by the JD but missing from the CV.",
        "importance": "Critical",
        "reason": "Why this skill is important for the role."
      }}
    ],
    "learning_path": [
      {{
        "skill_to_develop": "The skill from the gap.",
        "recommendation": "A concrete learning recommendation."
      }}
    ],
    "executive_summary": "Your final executive summary for the candidate.",
    "learning_potential": {{
      "rating": "High",
      "summary": "The candidate has a strong track record of adapting to new technologies and frameworks, suggesting they can learn the missing skills quickly.",
      "evidence": [
        "Successfully migrated a legacy system from Java to Go.",
        "Holds certifications in both AWS and GCP, showing adaptability across cloud platforms."
      ]
    }}
  }}
}}
"""

async def run_analysis(request: AnalysisRequest) -> AnalysisResponse:
  """
  Runs the analysis by sending the request to the LLM and parsing
  the structured response.
  """
  prompt = _create_analysis_prompt(request.cv_text, request.jd_text)
  
  try:
    response = await aclient.chat.completions.create(
      model="gpt-4o-mini",
      messages=[{"role": "user", "content": prompt}],
      response_model=AnalysisResponse,
      max_retries=2,
    )
    return response
  except Exception as e:
    # Add structured logging here  <-- IMPORTANT
    print(f"An error occurred during LLM analysis: {e}")
    # Raise an HTTPException to be caught by FastAPI's error handling
    raise HTTPException(
      status_code=500,
      detail="Failed to get a valid analysis from the AI model."
    )