
import json
from typing import List, Optional, Dict, Any, Union

from services.llm import LLM_With_Tracking
from services.prompt_factory import edit_cv_with_ai_prompt, extract_job_insights_prompt, create_cover_letter_prompt
from schema.job_analysis_schema import JobInsights


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


    llm_with_tracking = LLM_With_Tracking(temperature=0.2, task_name="job_analysis")

    prompt = extract_job_insights_prompt(job_description,pydantic_model=JobInsights)
    messages = [("human", prompt)]
    output =llm_with_tracking.invoke_with_tracking(messages,pydantic_model=JobInsights)

 

    if output["error"]:
        raise Exception(output["error"])
    
    job_insights = output["structured_output"]
    parsed = job_insights.model_dump()
    return parsed


def edit_cv_with_ai(full_cv_context: Dict[str,Any], 
                    job_analytics: Optional[Union[str, Dict[str, Any]]],
                    sections: List[str] = None,):

    """
    sections can contain any combination of:
    ["summary"]
    ["experience"]
    ["projects"]
    ["skills"]

    or

    ["summary", "experience", "projects", "skills"]
    """

    prompt = edit_cv_with_ai_prompt(full_cv_context, job_analytics, sections)


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

    if "summary" in sections:
        assert "summary" in parsed
        assert parsed["summary"]

    if "experience" in sections:
        assert "experience" in parsed
        assert isinstance(parsed["experience"], list)
        assert len(parsed["experience"]) > 0

    if "projects" in sections:
        assert "projects" in parsed
        assert isinstance(parsed["projects"], list)
        assert len(parsed["projects"]) > 0

    if "skills" in sections:
        assert "skills" in parsed
        assert isinstance(parsed["skills"], list)
        assert len(parsed["skills"]) > 0

    return parsed


def create_cover_letter(full_cv_context: Dict[str,Any], job_analytics: Optional[Union[str, Dict[str, Any]]]):


    work_experience = full_cv_context['experience']
    projects = full_cv_context['projects']
    education = full_cv_context['education']


    prompt = create_cover_letter_prompt(full_cv_context, job_analytics)

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
