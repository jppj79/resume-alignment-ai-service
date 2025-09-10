import instructor
import openai
from fastapi import HTTPException
from ..schemas import JDAnalysisRequest, JDAnalysisResponse

aclient  = instructor.patch(openai.AsyncOpenAI())

def _create_jd_analysis_prompt(jd_text: str) -> str:
    """
    Creates the detailed, structured prompt for the LLM to analyze a job description.
    This prompt is designed to identify "unicorn" roles that combine multiple profiles.
    """
    return f"""
# ROLE & GOAL
You are a world-class, senior Recruitment Strategist and HR Analyst with over 20 years of experience. Your expertise is in organizational design and analyzing job market trends. Your task is to critically analyze a single job description (JD) to determine if it is asking for a "unicorn" candidate—an individual expected to fill multiple, distinct professional roles. Your output must be a structured JSON object, providing actionable insights for hiring managers. Do not add any commentary or text outside of the final JSON object.

# CONTEXT
- JOB_DESCRIPTION_TEXT: ```{jd_text}```

# DETAILED INSTRUCTIONS
Analyze the provided job description and generate a JSON response. The analysis must cover the following points:

1.  **Overall Assessment**:
    -   First, determine if the JD describes a single, cohesive role or if it's a hybrid role blending multiple distinct profiles. Set 'is_hybrid_role' to true or false.
    -   Identify the 'primary_focus' of the position, even if it's a hybrid role (e.g., "Backend Development with DevOps responsibilities").

2.  **Profile Deconstruction**:
    -   Identify and list each distinct professional profile found within the JD (e.g., "Data Scientist", "DevOps Engineer", "Frontend Developer").
    -   For each 'identified_profile', extract and list its specific 'key_responsibilities'.
    -   Critical Skill Differentiation: Carefully differentiate between mandatory skills (**core_requirements**) and "nice to have" or "desirable" skills (**desirable_skills**). Place skills mentioned as "plus", "bonus", or "preferred" in the 'desirable_skills' list. This instruction now fully governs skill extraction.

3.  **Conflict & Overlap Summary**:
    -   Write a concise 'conflict_summary' explaining *why* the combination of profiles is challenging. Highlight the core tensions or the rarity of the combined skill set. For example, explain how the mindset of a creative UI/UX designer differs from a systems-focused DevOps engineer.

4.  **Hiring Realism Assessment**:
    -   Assess the probability of finding a single candidate who genuinely possesses all 'core_requirements' at a high level.
    -   Factor in "Nice to Haves": Explicitly consider the volume and diversity of the 'desirable_skills'. A large or unrelated list of desirable skills significantly decreases the hiring realism.
    -   Provide a 'rating' (**High**, **Medium**, **Low**) and justify it based on both core requirements and the weight of desirable skills.

5.  **Actionable Recommendations**:
    -   Provide a list of concrete, actionable 'recommendations' for the hiring manager. These could include suggestions like splitting the role into two separate positions, refining the job description to focus on core needs, or adjusting seniority and compensation expectations.

# MANDATORY OUTPUT FORMAT
Generate a single JSON object that strictly follows the required schema. Do not include markdown formatting like ```json in your response.
**CRITICAL: All keys in the JSON object MUST be in snake_case (e.g., 'is_hybrid_role', 'primary_focus', 'identified_profiles'). The output must strictly follow the required schema.**
The final JSON object MUST be complete and contain all the sections shown in the example structure below.

**HERE IS AN EXAMPLE of the required structure. Populate all fields with your analysis:**
```json
{{
  "jd_analysis": {{
    "is_hybrid_role": true,
    "primary_focus": "Senior Backend Developer with Data Science expectations",
    "identified_profiles": [
      {{
        "profile_title": "Backend Developer",
        "key_responsibilities": [
          "Develop and maintain microservices.",
          "Optimize application performance and database queries.",
          "Write clean, testable code and perform code reviews."
        ],
        "core_requirements": [
          "Python",
          "FastAPI/Django",
          "PostgreSQL",
          "Docker"
        ],
        "desirable_skills": [
          "Kubernetes experience",
          "Frontend knowledge (React)"
        ]
      }},
      {{
        "profile_title": "Data Scientist (implied by desirable skills)",
        "key_responsibilities": [
          "Analyze user data to generate insights.",
          "Develop predictive models (as suggested by 'nice to have')."
        ],
        "core_requirements": [
          "SQL complex queries"
        ],
        "desirable_skills": [
          "Pandas",
          "Scikit-learn",
          "Experience with ML pipelines"
        ]
      }}
    ],
    "conflict_summary": "The core role is clearly a Backend Developer. However, the desirable skills introduce elements of Data Science and advanced DevOps. The skills listed under 'nice to have' are not trivial; they represent a separate career track. This suggests the company wants a developer who can also function as a part-time data scientist.",
    "hiring_realism": {{
      "rating": "Low",
      "justification": "Finding a senior developer with deep backend expertise is feasible. However, adding expectations for machine learning (Pandas, Scikit-learn) and Kubernetes significantly narrows the pool. Candidates with this combined skill set are rare and highly sought after, likely exceeding standard developer compensation bands."
    }},
    "recommendations": [
      "Focus the role entirely on Backend Development by removing the data science 'nice to haves' to attract a larger pool of qualified developers.",
      "If data science capabilities are critical, consider creating a separate, part-time Data Analyst role or allocate budget for a specialized contractor.",
      "Move 'Kubernetes experience' from desirable to core if infrastructure management is essential, or remove it if a separate DevOps team handles deployment."
    ]
  }}
}}
"""

async def run_jd_analysis(request: JDAnalysisRequest) -> JDAnalysisResponse:
    """
    Runs the analysis on a single JD to identify combined roles.
    """
    prompt = _create_jd_analysis_prompt(request.jd_text)
    
    try:
        response = await aclient.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_model=JDAnalysisResponse,
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