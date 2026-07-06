
from typing import Dict, Any, Optional, Union, List

def edit_cv_with_ai_prompt(
    full_cv_context: Dict[str, Any],
    job_analytics: Optional[Union[str, Dict[str, Any]]],
    sections: List[str] = None,
):
    """
    sections can contain any combination of:
    ["summary"]
    ["experience"]
    ["projects"]
    ["skills"]

    or

    ["summary", "experience", "projects", "skills"]
    """

    if sections is None:
        sections = ["summary", "experience", "projects", "skills"]

    cv_context = []
    instructions = []
    output_schema = []

    cv_context.append(f"Summary: {full_cv_context['summary']}")
    cv_context.append(f"Experience: {full_cv_context['experience']}")
    cv_context.append(f"Projects: {full_cv_context['projects']}")
    cv_context.append(f"Skills: {full_cv_context['skills']}")

    if "summary" in sections:
        

        instructions.append("""
SUMMARY:
Rewrite the candidate’s summary to emphasize only the most relevant and verifiable overlaps with the job description, based strictly on the provided Job Analysis and existing summary.

- Focus on alignment with the role; prioritize shared skills, experience, and domain relevance.
- Do not introduce any new claims, skills, or experiences not supported by the input.
- Keep the result concise, clear, and professional (2–4 sentences maximum).
- Ensure the tone remains natural and avoids exaggeration or overstatement.
""")

        output_schema.append(
            '"summary": "<rewritten summary>"'
        )

    if "experience" in sections:
        

        instructions.append("""
EXPERIENCE:
- Keep the exact same number of experience entries, companies, dates, and titles.
- Reorder the highlights so the most relevant achievements appear first.
- Refine wording for clarity and impact without changing factual content.
""")

        output_schema.append("""
"experience": [
    {
        "company": "<exact original company>",
        "position": "<exact original position>",
        "start_date": "<exact original start date>",
        "end_date": "<exact original end date>",
        "location": "<exact original location>",
        "highlights": [
            "<tailored bullet 1>",
            "<tailored bullet 2>"
        ]
    }
]
""")

    if "projects" in sections:
        

        instructions.append("""
PROJECTS:
- Keep the exact same projects.
- Refine descriptions to emphasize the tools, technologies, and outcomes most relevant to the target role.
""")

        output_schema.append("""
"projects": [
    {
        "name": "<exact original name>",
        "url": "<exact original URL or null>",
        "highlights": [
            "<tailored bullet 1>",
            "<tailored bullet 2>"
        ]
    }
]
""")

    if "skills" in sections:
        

        instructions.append("""
SKILLS:
- Extract only skills explicitly mentioned in the Job Analysis.
- Organize skills into ONLY 2–3 sections.
- Section labels must be a single word.
- Each skill must be 1–2 words maximum.
- Maximum total skills: 10–12.
""")

        output_schema.append("""
"skills": [
    {
        "label": "<section>",
        "details": [
            "<skill1>",
            "<skill2>"
        ]
    }
]
""")

    prompt = f"""
You are an expert CV optimization system specialized in AI research and industrial ML roles.

You will rewrite ONLY the requested CV sections.

STRICT GUARDRAILS:
1. NO HALLUCINATION.
2. NO EXAGGERATION.
3. FACTUAL INTEGRITY.
4. VOCABULARY ALIGNMENT.

### TARGET JOB ANALYSIS
<job_analysis>
{job_analytics}
</job_analysis>

### ORIGINAL CV CONTEXT
<cv_context>
{"\n".join(cv_context)}
</cv_context>

### REWRITE INSTRUCTIONS
{"".join(instructions)}

### OUTPUT FORMAT

Return ONLY valid JSON.

{{
{",".join(output_schema)}
}}
"""

    return prompt

def extract_job_insights_prompt(job_description: str):
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
    return prompt

def create_cover_letter_prompt(full_cv_context: Dict[str,Any], job_analytics: Optional[Union[str, Dict[str, Any]]]):
    work_experience = full_cv_context['experience']
    projects = full_cv_context['projects']
    education = full_cv_context['education']


    prompt = f"""
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
    return prompt
    

if __name__ == "__main__":
    print(edit_cv_with_ai_prompt(
        full_cv_context={
            "summary": "Summary",
            "experience": "Experience",
            "projects": "Projects",
            "skills": "Skills"
        },
        job_analytics="Job Analytics",
        sections=["summary"]
    ))

