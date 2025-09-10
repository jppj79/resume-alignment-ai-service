from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# --- Analysis Models ---
class AnalysisRequest(BaseModel):
    """
    Defines the input structure for the analysis endpoint.
    """
    cv_text: str = Field(..., description="The full text content of the user's curriculum vitae.")
    jd_text: str = Field(..., description="The full text content of the job description.")

class LearningPotential(BaseModel):
    """
    Assesses the candidate's potential to learn new skills based on their experience.
    """
    rating: Literal['High', 'Medium', 'Low'] = Field(..., description="Assessment of the candidate's ability to learn new technologies quickly.")
    summary: str = Field(..., description="Justification for the rating based on CV evidence.")
    evidence: List[str] = Field(..., description="Specific examples from the CV that support the learnability assessment (e.g., diverse tech stack, career progression).")

class ScoreBreakdown(BaseModel):
    """
    Provides a detailed breakdown of the match score across different categories.
    """
    technical_skills: int = Field(..., ge=0, le=100, description="Score for matching required technologies, frameworks, and tools.")
    experience: int = Field(..., ge=0, le=100, description="Score for alignment in years of experience and role responsibilities.")
    soft_skills: int = Field(..., ge=0, le=100, description="Score for matching soft skills like communication, leadership, etc.")

class MatchScore(BaseModel):
    """
    Contains the overall match score and its detailed breakdown.
    """
    overall_score: int = Field(..., ge=0, le=100, description="The final, weighted match score from 0 to 100.")
    breakdown: ScoreBreakdown
    summary: str = Field(..., description="A concise summary justifying the overall score.")

class Strength(BaseModel):
    """
    Represents a key skill or experience from the CV that matches the job description.
    """
    skill: str = Field(..., description="A specific skill or experience, e.g., 'REST API Development with NestJS'.")
    evidence: str = Field(..., description="Brief quote or reference from the CV that proves this skill.")

class SkillGap(BaseModel):
    """
    Identifies a key skill required by the job description that is missing or underdeveloped in the CV.
    """
    skill: str = Field(..., description="The missing skill, e.g., 'Kubernetes'.")
    importance: Literal['Critical', 'Important', 'Desirable'] = Field(..., description="The importance of the skill for the role.")
    reason: str = Field(..., description="Explanation of why this skill is important according to the job description.")

class LearningStep(BaseModel):
    """
    Provides an actionable recommendation for closing a skill gap.
    """
    skill_to_develop: str = Field(..., description="The skill that the user should focus on learning.")
    recommendation: str = Field(..., description="A concrete, actionable recommendation for a course, book, or project.")

class AnalysisResult(BaseModel):
    """
    The main structure containing the full analysis result.
    """
    match_score: MatchScore
    strengths: List[Strength]
    skill_gaps: List[SkillGap]
    learning_path: list[LearningStep] | None = None
    executive_summary: str = Field(..., max_length=1000, description="A summary for the candidate about their fit for the role.")
    learning_potential: LearningPotential | None = None

class AnalysisResponse(BaseModel):
    """
    The final top-level response object returned by the API.
    """
    analysis: AnalysisResult

# --- ATS checker models ---
class ATSCheckRequest(BaseModel):
    """
    Defines the input for the ATS checker endpoint. It only needs the CV text.
    """
    cv_text: str = Field(..., description="The full text content of the user's curriculum vitae.")

class ATSIssue(BaseModel):
    """
    Represents a single issue found during the ATS scan, with a clear category.
    """
    issue_type: Literal['Formatting', 'Keywords', 'Parsing Risk', 'Contact Info', 'Structure'] = Field(..., description="The category of the issue found.")
    description: str = Field(..., description="A clear explanation of the potential problem.")
    suggestion: str = Field(..., description="An actionable suggestion on how to fix the issue.")

class ATSResult(BaseModel):
    """
    Contains the full results of the ATS-friendliness check, including a score and a list of issues.
    """
    ats_score: int = Field(..., ge=0, le=100, description="An overall score from 0-100 indicating ATS compatibility.")
    summary: str = Field(..., description="A general summary of the CV's performance against ATS standards.")
    issues: List[ATSIssue] = Field(..., description="A list of specific issues found that could harm ATS parsing.")

class ATSCheckResponse(BaseModel):
    """
    The final top-level response object for the ATS check API endpoint.
    """
    ats_check: ATSResult

# --- JD analyzer models ---
class JDAnalysisRequest(BaseModel):
    """Request model for JD-only analysis."""
    jd_text: str

class IdentifiedProfile(BaseModel):
    """Represents a single professional profile identified within a JD."""
    profile_title: str = Field(..., description="The title of the identified professional profile, e.g., 'Data Scientist'.")
    key_responsibilities: List[str] = Field(..., description="Specific responsibilities for this profile mentioned in the JD.")
    #required_skills: List[str] = Field(..., description="Specific skills for this profile mentioned in the JD.")
    core_requirements: List[str] = Field(..., description="Mandatory skills explicitly required for the role.")
    desirable_skills: List[str] = Field(..., description="Skills listed as 'nice to have', 'preferred', or 'bonus points'.")

class HiringRealism(BaseModel):
    """Assessment of how realistic it is to hire for this role."""
    rating: str = Field(..., description="The likelihood of finding a suitable candidate (e.g., 'High', 'Medium', 'Low').")
    justification: str = Field(..., description="The reasoning behind the rating, based on market reality.")

class JDAnalysis(BaseModel):
    """The core analysis of the job description."""
    is_hybrid_role: bool = Field(..., description="True if the JD combines multiple distinct roles.")
    primary_focus: str = Field(..., description="The main functional area of the job.")
    identified_profiles: List[IdentifiedProfile] = Field(..., description="A list of distinct profiles found in the JD.")
    conflict_summary: str = Field(..., description="An explanation of why the combination of profiles is challenging.")
    hiring_realism: HiringRealism = Field(..., description="An assessment of the hiring difficulty.")
    recommendations: List[str] = Field(..., description="Actionable suggestions for the hiring manager.")

class JDAnalysisResponse(BaseModel):
    """The final Pydantic model for the JD analysis API response."""
    jd_analysis: JDAnalysis
    