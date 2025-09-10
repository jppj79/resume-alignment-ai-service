![Python](https://img.shields.io/badge/python-3.13+-blue.svg)

# Resume Align AI 🤖

An AI-powered career coach, built in Python, designed to demystify the job application process by providing a deep, actionable analysis of your resume against a job description.

---

### About The Project

This project started with a simple question every job seeker asks: **"Am I the right candidate for this role?"**

This project was created with a focus on **simplicity and transparency**. While many powerful platforms and complex open-source projects exist, the goal here wasn't to replicate all their features. Instead, this tool is **intentionally streamlined** to be easy to set up and run, allowing anyone to explore the **core mechanics** of how Large Language Models (LLMs) can be applied to resume analysis. Given its academic purpose and origin as a personal job-seeking tool, the prompt engineering is **specifically fine-tuned for software engineering roles, including Full-stack Developer, DevOps and related developer positions.**

It's about more than just tweaking a resume for a single application; it’s about creating a feedback loop for continuous professional improvement.

### Features ✨

* 📊 **Detailed Match Score:** Instantly see where you stand with a comprehensive score.
* 🌱 **Actionable Skill Gaps:** Know exactly what skills to work on to become a better fit.
* 🚀 **Learning Potential Rating:** Highlights your ability to adapt and grow into the role, even if you don't meet 100% of the requirements.
* 🤖 **ATS-Compatibility Check:** Get concrete tips to ensure your resume gets past the bots and is seen by a human.
* 🦄 **Job Description Analysis:** Get a deep dive into the job requirements, identifying key responsibilities and core/desirable requirements.

### Tech Stack & Core Mechanics 🛠️

The "secret sauce" of this application is a combination of a modern tech stack and strategic implementation:

* **Backend:** Python
* **AI Engine:** OpenAI API (specifically `gpt-4o-mini` for its balance of cost and capability).
* **Core Logic:** Strategic Prompt Engineering to guide the AI's reasoning for a deep, relevant analysis.
* **Data Integrity:** Strict data schemas enforced by Pydantic to ensure clean, predictable JSON output every time.

---

## Prerequisites 🛠️

- Python 3.13+ 🐍
- [OpenAI API key](https://platform.openai.com/api-keys) 🔑

## Installation ⚙️

1.  Clone the repository:

    ```bash
    $ git clone https://github.com/jppj79/resume-alignment-ai-service.git
    $ cd resume-alignment-ai-service
    ```

2.  Create a virtual environment:

    ```bash
    $ python -m venv venv
    ```

3. Activate the virtual environment

    ```bash
    $ .\.venv\Scripts\activate
    ```

4.  Install dependencies:

    ```bash
    $ pip install -r requirements.txt
    ```

5. Create a .env file in project root with your [OpenAI API key](https://platform.openai.com/api-keys):

    ```
    OPENAI_API_KEY="your_openai_api_key_here"
    ```

6. Run the server:

    ```bash
    $ uvicorn app.main:app --reload
    ```

The application will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## API Endpoints 🧰

You can use a tool like [Postman](https://www.postman.com/) to test the endpoints.

![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)

### Health Check ⚙️

-   **URL:** `/`
-   **Method:** `GET`
-   **Description:** Health check endpoint to ensure the service is running.
-   **Success Response:**
    -   **Code:** 200
    -   **Content:** `{"status": "ok", "service": "alignment-service"}`

### Analyze CV and Job Description ⚙️

-   **URL:** `/analyze`
-   **Method:** `POST`
-   **Description:** Accepts CV and Job Description text and returns a detailed, AI-powered analysis of the match.

#### Payload Example for `/analyze`

```json
{
    "cv_text": "Full text of the CV here...",
    "jd_text": "Full text of the job description here..."
}
```

#### Response Example
```json
{
    "analysis": {
        "match_score": {
            "overall_score": 85,
            "breakdown": {
                "technical_skills": 90,
                "experience": 85,
                "soft_skills": 80
            },
            "summary": "Pablo's extensive experience and technical proficiency in Python, microservices architecture, and cloud platforms align well with the role specifications. However, the absence of Django experience and AWS familiarity slightly lowers the match score."
        },
        "strengths": [
            {
                "skill": "Python expertise with microservices architecture",
                "evidence": "Engineered a resilient microservices architecture using Python, NestJS, and Apache Kafka."
            }
        ],
        "skill_gaps": [
            {
                "skill": "Django framework experience",
                "importance": "Important",
                "reason": "Django is required for designing and maintaining backend applications, a core responsibility in the role."
            }
        ],
        "learning_path": [
            {
                "skill_to_develop": "Django framework",
                "recommendation": "Enroll in 'Django for Beginners: Build Websites with Python & Django' by William S. Vincent."
            }
        ],
        "executive_summary": "Pablo Perez possesses robust skills as a Principal Software Engineer with significant experience in Python...",
        "learning_potential": {
            "rating": "High",
            "summary": "The candidate showcases a strong ability to learn new technologies quickly, having adapted to various roles and responsibilities over his 20-year career.",
            "evidence": [
                "Led the architecture and development of critical AI-powered systems."
            ]
        }
    }
}
```
### Analyze Job Description ⚙️

-   **URL:** `/analyze-jd-profile`
-   **Method:** `POST`
-   **Description:** Accepts Job Description text and returns a detailed, AI-powered analysis of role complexity.

#### Payload Example for `/analyze-jd-profile`

```json
{
    "jd_text": "Full text of the job description here..."
}
```

#### Response Example
```json
{
    "jd_analysis": {
        "is_hybrid_role": true,
        "primary_focus": "Cloud Operations and Incident Management with DevOps responsibilities",
        "identified_profiles": [
            {
                "profile_title": "Cloud Operations Engineer",
                "key_responsibilities": [
                    "Perform daily operational tasks such as log analysis, system health checks, and user support",
                    "Implement and document new processes on operational playbooks",
                    "Monitor system health using custom health check tools and incident management platforms",
                    "Foster a culture of continuous improvement and operational excellence",
                    "Perform tenant deployment with tailor-built architecture"
                ],
                "core_requirements": [
                    "Azure certifications (AZ-900, AZ-104, AZ-303, AZ-304)",
                    "Proficiency in containerization and orchestration (Docker, Kubernetes)",
                    "Understanding of networking, VNET, Load Balancer, Firewall, VPN",
                    "Experience with Active Directory and authentication services (MFA, TOTP)",
                    "Strong analytical and problem-solving skills"
                ],
                "desirable_skills": [
                    "Experience with GCP cloud infrastructure",
                    "Knowledge/experience in cloud databases (Cassandra, Mongodb, PostgreSQL)",
                    "Familiarity with ITIL processes and service management best practices",
                    "Experience with CI/CD pipelines",
                    "Experience with Remote access solutions",
                    "Proficiency in monitoring tools (Azure/GCP monitoring, BigQuery)"
                ]
            },
            {
                "profile_title": "Incident Manager",
                "key_responsibilities": [
                    "Proactively identify, diagnose, and troubleshoot complex issues",
                    "Lead the resolution of major incidents",
                    "Serve as a key escalation point for support teams",
                    "Translate technical issues into summaries for non-technical stakeholders"
                ],
                "core_requirements": [
                    "Ability to manage incidents effectively",
                    "Knowledge of service management best practices",
                    "Excellent communication skills"
                ],
                "desirable_skills": [
                    "Experience with ServiceNow",
                    "Understanding of change management processes"
                ]
            }
        ],
        "conflict_summary": "The role combines Cloud Operations and Incident Management with overlapping responsibilities, which require distinct skill sets and mindsets. While both profiles require technical expertise, the nature of incident management focuses more on communication and process efficiency, while cloud operations demand in-depth technical knowledge of the cloud environment, automation, and orchestration. Expecting one individual to excel in both areas is unrealistic given the depth and breadth of required skills.",
        "hiring_realism": {
            "rating": "Low",
            "justification": "While it is feasible to find candidates with strong Cloud Operations skills, the addition of incident management responsibilities complicates the search. Candidates who are experienced in both fields are rare, and the extensive list of desirable skills further narrows the pool, leading to low hiring realism."
        },
        "recommendations": [
            "Consider splitting the role into two separate positions: one focused on Cloud Operations and the other on Incident Management to attract more specialized candidates.",
            "Refine the job description to target core responsibilities and remove less critical desirable skills to widen the candidate pool.",
            "Adjust compensation and seniority expectations to align with the expected skill set and market reality."
        ]
    }
}
```

### Check ATS Friendliness ⚙️

-   **URL:** `/check-ats`
-   **Method:** `POST`
-   **Description:** Accepts CV text and returns an analysis of its ATS friendliness.

#### Payload Example for `/check-ats`

```json
{
    "cv_text": "Full text of the CV here..."
}
```

#### Response Example
```json
{
    "ats_check": {
        "ats_score": 70,
        "summary": "The CV is detailed and contains relevant information, but has several issues related to structure, contact info, and keyword optimization.",
        "issues": [
            {
                "issue_type": "Contact Info",
                "description": "There is no visible contact information in the CV text, such as email, phone number, or LinkedIn profile.",
                "suggestion": "Include clear, standard contact information at the top of the CV to ensure it is easily accessible for ATS parsing."
            },
            {
                "issue_type": "Keywords",
                "description": "The CV lacks a specific skills section. While there are several relevant keywords embedded in the descriptions, key skills are not explicitly listed, making them harder for ATS to identify.",
                "suggestion": "Add a dedicated skills section listing relevant keywords and technologies for better visibility in ATS scans."
            },
            {
                "issue_type": "Formatting",
                "description": "While the CV provides a detailed account of experience and achievements, the dense block of text might be hard to read for both ATS and human recruiters, as it could be viewed as overwhelming.",
                "suggestion": "Break down long paragraphs into bullet points for clearer readability and easier parsing."
            }
        ]
    }
}
```
