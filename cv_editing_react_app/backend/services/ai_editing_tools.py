
import json
from config.local_llm_settings import client, MODEL_NAME
from typing import List, Optional, Dict, Any, Union


def extract_job_insights(job_description: str):
    """
    Extract hiring signals from a Job Description.
    Returns:
        {
            "job_title": str,
            "company_name": str,
            "job_analysis_markdown": str
        }
    """

    prompt = f"""
You are an expert AI recruiter and job description analyst.

Analyze the following job description.

STRICT OUTPUT RULES:
- Output ONLY valid JSON.
- Do not include explanations, pleasantries, or markdown formatting outside the JSON.
- All outputs must be in English. If the job description is written in another language, internally translate it to English before performing the analysis.
- For factual categories ("gatekeepers" and "high_priority_missions"), do not hallucinate. If information is missing, use "Not Specified".
- For analytical categories ("the_essence"), infer the underlying reality of the role based on the provided description.
- Ensure the output is valid JSON.
- Escape all string values correctly.
- Use "\\n" for line breaks inside string values if needed.
- Preserve the exact JSON schema shown below.

JOB DESCRIPTION
---------------
{job_description}

Return JSON with EXACTLY the following structure:

{{
  "job_title": "<job title>",
  "company_name": "<company name or 'Not Specified'>",
  "analysis": {{
    "gatekeepers": {{
      "core_paradigms": [
        "<paradigm 1>",
        "<paradigm 2>"
      ],
      "programming_languages": [
        "<language 1>",
        "<language 2>"
      ],
      "infrastructure_and_tools": [
        "<tool 1>",
        "<tool 2>"
      ],
      "education_tier": "<education requirement>",
      "languages": [
        "<spoken language 1>"
      ]
    }},
    "the_essence": {{
      "ultimate_product_goal": "<1-2 sentences deducing the core business value of this role>",
      "technical_bottleneck": "<1-2 sentences inferring the hardest technical challenge this person will face>",
      "applied_vs_theoretical_divide": "<1-2 sentences analyzing how much of this role is shipping product versus research or architecture>"
    }},
    "high_priority_missions": {{
      "priority_1": "<top priority>",
      "priority_2": "<second priority>",
      "priority_3": "<third priority>"
    }}
  }}
}}
"""

    response = client.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        format="json",
        think=False,
        options={
            "temperature": 0.2,
            "top_p": 0.90,
            "repeat_penalty": 1.05,
        },
    )

    parsed = json.loads(response["message"]["content"])

    required_fields = [
        "job_title",
        "company_name",
        "analysis"
    ]

    for field in required_fields:
        if field not in parsed:
            raise ValueError(f"Missing field: {field}")

    return parsed


def edit_cv_with_ai(full_cv_context: Dict[str,Any], job_analytics: Optional[Union[str, Dict[str, Any]]]):

    work_experience = full_cv_context['experience']
    projects = full_cv_context['projects']
    skills = full_cv_context['skills']
    summary = full_cv_context['summary']

    job_analytics = job_analytics

    prompt = f"""
    You are an expert CV optimization system specialized in AI research and industrial ML roles.

    You will rewrite and tailor parts of a candidate's CV based ONLY on the provided CV context and the target Job Analysis.

    STRICT GUARDRAILS:
    1. NO HALLUCINATION: Do NOT invent companies, projects, tools, metrics, or achievements.
    2. NO EXAGGERATION: Do NOT inflate the candidate's impact or seniority. 
    3. FACTUAL INTEGRITY: If the candidate lacks a skill required by the JD, do NOT add it. 
    4. VOCABULARY ALIGNMENT: You MAY adopt the terminology and tone of the Job Analysis for existing matching skills (e.g., changing "made an API" to "developed a RESTful microservice" if the facts support it).

    ### TARGET JOB ANALYSIS
    <job_analysis>
    {job_analytics}
    </job_analysis>

    ### ORIGINAL CV CONTEXT (SOURCE OF TRUTH)
    <cv_context>
    Summary: {summary}
    Experience: {work_experience}
    Projects: {projects}
    Skills: {skills}
    </cv_context>

    ### REWRITE INSTRUCTIONS PER SECTION

    SUMMARY:
    - Rewrite to highlight the strongest overlaps between the candidate's history and the Job Analysis.
    - Keep to 2–4 concise, impactful sentences.

    EXPERIENCE:
    - Keep the exact same number of experience entries, companies, dates, and titles.
    - Reorder the `highlights` (bullet points) so the most relevant achievements to the target job appear first.
    - Refine the wording for clarity and impact, ensuring metrics and tools are highly visible.

    PROJECTS:
    - Keep the exact same projects.
    - Refine the descriptions to emphasize the tools, and outcomes most relevant to the target role.

    SKILLS:
    - Extract only skills explicitly mentioned in the Job Analysis. Do not infer or add new skills.
    - Organize skills into ONLY 2–3 sections.
    - Section labels MUST be a single word (e.g., Languages, Frameworks, Infrastructure, Tools, Cloud, Data).
    - Each skill item MUST be a short keyword or phrase of 1–2 words maximum (e.g., "Python", "FastAPI", "LangChain", "Docker", "CI/CD").
    - Do NOT use sentences or explanations inside skill items.
    - If a skill cannot be expressed in 1–2 words, decompose it into multiple atomic skills or discard it.
    - Keep related skills grouped logically.
    - Maximum total skills: 10–12 across all sections.

    ### OUTPUT FORMAT
    - Return ONLY valid JSON. No markdown formatting outside the JSON block.
    - Ensure all strings are properly escaped.
    - Every string inside a `highlights` array must be a clean, single sentence without Markdown bullet characters (-, *).

    {{
    "summary": "<rewritten summary>",
    "experience": [
        {{
        "company": "<exact original company>",
        "position": "<exact original position>",
        "start_date": "<exact original start date>",
        "end_date": "<exact original end date>",
        "location": "<exact original location>",
        "highlights": [
            "<tailored bullet point 1>",
            "<tailored bullet point 2>"
        ]
        }}
    ],
    "projects": [
        {{
        "name": "<exact original name>",
        "url": "<exact original URL, or null if none>",
        "highlights": [
            "<tailored bullet point 1>",
            "<tailored bullet point 2>"
        ]
        }}
    ],
    "skills": [
        {{
        "label": "<e.g., 'Languages' or 'ML Frameworks'>",
        "details": ["<skill 1>", "<skill 2>"]
        }}
    ]
    }}
    """

    response = client.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        format="json",
        think=False,
        options={
            "temperature": 0.3,
            "top_p": 0.90,
            "repeat_penalty": 1.05,
        },
    )

    content = response["message"]["content"]
    parsed = json.loads(content)

    assert "summary" in parsed
    assert "experience" in parsed
    assert "projects" in parsed

    assert parsed["summary"]
    assert len(parsed["experience"]) > 0
    assert len(parsed["projects"]) > 0

    return parsed


def clean_text(text: str):
    return text.encode("utf-8", "ignore").decode("utf-8")

def create_cover_letter(full_cv_context: Dict[str,Any], job_analytics: Optional[Union[str, Dict[str, Any]]]):


    work_experience = full_cv_context['experience']
    projects = full_cv_context['projects']
    education = full_cv_context['education']


    prompt = prompt = f"""
You are an expert professional cover letter writer specialized in Machine Learning and AI research roles.

You will generate a tailored cover letter based ONLY on the provided CV context and job description.

At the same time, you must also extract structured information from the job description.

STRICT RULES (VERY IMPORTANT):
- Do NOT invent any experience, projects, tools, companies, or achievements.
- Do NOT hallucinate or exaggerate impact.
- Do NOT include metadata such as:
  - titles (e.g., "Cover Letter")
  - candidate name headers
  - dates
  - labels like "Subject", "Application"
- Output MUST be valid JSON only.
- Cover letter must be in MARKDOWN format.
- Maximum cover letter length: 200 words strict limit.

EXTRACTION RULES: 
From the job description:
- Extract the **job title** as accurately as possible if can't find one then write ML Engineer.
- Extract the **company name** if explicitly mentioned.
- If the company name is not clearly stated, return "Unknown".
- If the job title is ambiguous, infer the most likely title from context without hallucination.

CONTENT RULES:
- You MAY rephrase CV content into a natural narrative.
- You MAY align wording with job description keywords ONLY when meaning is unchanged.
- You MAY prioritize relevant experiences from CV for the role.
- If information is missing, do NOT fabricate; keep statements general or omit them.
- Tone must be professional, natural, and human-like.
- You MAY use **bold markdown formatting** for key technical skills or achievements.

STRUCTURE REQUIREMENT:
1. Opening paragraph: motivation and role interest
2. Body paragraph(s): relevant experience and technical alignment
3. Closing paragraph: summary and professional sign-off

Return ONLY valid JSON in the following format:

{{
  "cover_letter": "Dear Sir/Madam,\\n...markdown formatted cover letter...",
  "job_title": "...extracted or inferred job title...",
  "company": "...extracted company name or 'Unknown'..."
}}

JOB ANALYTICS:
{job_analytics}

CV CONTEXT (ONLY SOURCE OF TRUTH):
Candidate Name: {full_cv_context['name']}
{education}
{work_experience}
{projects}
"""

    response = client.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        format="json",
        think=False,
        options={
            "temperature": 0.7,
            "top_p": 0.90,
            "repeat_penalty": 1.05,
        },
    )

    content = response["message"]["content"]
    parsed = json.loads(content)
    assert "cover_letter" in parsed
    assert "job_title" in parsed
    assert "company" in parsed
    assert (parsed["cover_letter"] is not None) and (parsed["cover_letter"] != "") and (parsed["job_title"] is not None) and (parsed["job_title"] != "") and (parsed["company"] is not None) and (parsed["company"] != "")

    return parsed
    

def generate_connection_message(profileText: str, wordLimit: int, promptText: str, cvText: Optional[Union[str, Dict[str, Any]]], temperature: float = 0.2):
    system_prompt = """You are helping me write casual, human LinkedIn messages.
                    You write like a real person — direct, specific, slightly informal.
                    Never use corporate buzzwords or templated phrasing."""
    prompt = f"""

            {promptText}

            Read their profile/post below and draft a short message I could actually send — the kind a real person writes, not a template.

            A few things to keep in mind:
            - Sound like me, not a recruiter or a bot. Casual but not sloppy.
            - Pick ONE specific thing from their profile or post and react to it naturally (a project, an idea they shared, a career move)
            - Don't summarize my whole CV — just drop one relevant detail that creates a natural "why I'm reaching out" moment
            - It's okay to be a little direct or even slightly self-deprecating — that reads as human
            - Avoid: "I came across your profile", "synergy", "leverage", "I'd love to connect", "reach out", or anything that sounds like a mail merge
            - Keep it under {wordLimit} words. Shorter is better.

            Their profile/post:
            {profileText}

            Write only the message. No subject line, no explanation, no bullet points.
            """
    
    response = client.chat(
            model=MODEL_NAME,
            messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
            think=False,
            options={
                "temperature": temperature,
                "top_p": 0.90,
                "repeat_penalty": 1.05,
            },
        )
    content = response["message"]["content"]

    assert (content is not None) and (content != "")

    return content
