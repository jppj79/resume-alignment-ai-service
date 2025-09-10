from .core import config
from fastapi import FastAPI, HTTPException
from .schemas import AnalysisRequest, AnalysisResponse, ATSCheckRequest, ATSCheckResponse, JDAnalysisRequest, JDAnalysisResponse
from .services.analyzer import run_analysis
from .services.jd_analyzer import run_jd_analysis
from .services.ats_checker import run_ats_check

# Initialize the FastAPI app
app = FastAPI(
    title="ResumeAlign AI - Alignment Service",
    description="A microservice to analyze CVs against job descriptions.",
    version="0.2.0"
)

@app.get("/", tags=["Health Check"])
async def read_root():
    """
    Health check endpoint to ensure the service is running.
    """
    return {"status": "ok", "service": "alignment-service"}

@app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_cv_jd(request: AnalysisRequest):
    """
    Accepts CV and JD text and returns a detailed, AI-powered analysis of the match.
    """
    # The endpoint now calls our service logic and handles potential errors
    try:
        analysis_result = await run_analysis(request)
        return analysis_result
    except HTTPException as e:
        # Re-raise HTTPExceptions from the service layer
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected internal error occurred: {str(e)}")
    
@app.post("/analyze-jd-profile", response_model=JDAnalysisResponse, tags=["Analysis"])
async def analyze_jd_profile(request: JDAnalysisRequest):
    """
    Analyzes a single Job Description (JD) for role complexity.

    This endpoint examines a JD to determine if it describes a single cohesive
    role or if it combines multiple distinct professional profiles (a "unicorn" role).
    It returns a deconstruction of the required profiles, an assessment of hiring
    realism, and actionable recommendations.
    """
    try:
        analysis_result = await run_jd_analysis(request)
        return analysis_result
    except HTTPException as e:
        # Re-raise controlled HTTP exceptions from the service layer
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail="An unexpected internal error occurred.")
    
@app.post("/check-ats", response_model=ATSCheckResponse, tags=["ATS Checker"])
async def check_ats_friendliness(request: ATSCheckRequest):
    """
    Accepts CV text and returns an analysis of its ATS friendliness.
    """
    try:
        ats_result = await run_ats_check(request)
        return ats_result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected internal error occurred: {str(e)}")
