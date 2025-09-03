import instructor
import openai
from fastapi import HTTPException
from ..schemas import ATSCheckRequest, ATSCheckResponse

aclient = instructor.patch(openai.AsyncOpenAI())

def _create_ats_prompt(cv_text: str) -> str:
  """
  Creates the specialized prompt for the ATS Friendliness Checker.
  This prompt instructs the AI to act like an ATS system.
  """
  return f"""
# ROLE & GOAL
You are an advanced Applicant Tracking System (ATS) parser simulator. Your goal is to analyze a CV's text for its machine-readability and keyword optimization. You must identify any elements that could cause parsing errors or lower the candidate's ranking in an automated screening process.

# CONTEXT
- CV_TEXT: ```{cv_text}```

# DETAILED INSTRUCTIONS
Analyze the CV text based on the following ATS compatibility criteria:
1.  **Parsing Risks**: Identify elements that suggest complex formatting. Since you only see text, infer potential issues. For example, mention that if this text came from a two-column layout, a table, or included images/icons, it would likely fail.
2.  **Contact Information**: Verify that essential contact info (email, phone, LinkedIn) is present and appears in a standard, easily parsable format at the top.
3.  **Keywords & Skills**: Check if the skills section is clear and uses common industry keywords. Note if important skills are mentioned only in prose (harder to parse) instead of a dedicated skills list.
4.  **Structure & Headings**: Assess if the CV uses standard, conventional headings (e.g., "Work Experience", "Education", "Skills"). Non-standard headings can confuse a parser.
5.  **Action Verbs & Quantifiability**: Check if job descriptions start with strong action verbs and include quantifiable results (e.g., "Increased sales by 20%").

# MANDATORY OUTPUT FORMAT
Generate a single JSON object that strictly follows the required schema. All keys MUST be in snake_case. Populate all fields, including a list of specific issues found. If no issues are found in a category, confirm that it passed the check.

**HERE IS AN EXAMPLE of the required structure. Populate all fields with your analysis:**
```json
{{
  "ats_check": {{
    "ats_score": 85,
    "summary": "The CV is well-structured and uses standard headings, but could be improved by quantifying achievements and ensuring contact information is complete.",
    "issues": [
      {{
        "issue_type": "Parsing Risk",
        "description": "The text mentions a 'portfolio link in the header'. If the original document used a graphical header or a text box, an ATS might not read it correctly.",
        "suggestion": "Ensure all critical information, including links, is part of the main text body and not in headers, footers, or text boxes."
      }},
      {{
        "issue_type": "Keywords",
        "description": "Achievements under 'Software Engineer at Acme Corp' are descriptive but lack quantifiable metrics.",
        "suggestion": "Revise bullet points to include numbers and metrics, for example, change 'Developed new features' to 'Developed 3 new features, improving user engagement by 15%'."
      }}
    ]
  }}
}}
"""

async def run_ats_check(request: ATSCheckRequest) -> ATSCheckResponse:
  """
  Runs the ATS check by sending the request to the LLM and parsing the structured response.
  """
  prompt = _create_ats_prompt(request.cv_text)

  try:
    response = await aclient.chat.completions.create(
      model="gpt-4o-mini",
      messages=[{"role": "user", "content": prompt}],
      response_model=ATSCheckResponse,
      max_retries=2,
    )
    return response
  except Exception as e:
    # Add structured logging here  <-- IMPORTANT
    print(f"An error occurred during ATS check: {e}")
    raise HTTPException(
      status_code=500,
      detail="Failed to get a valid ATS analysis from the AI model."
    )
