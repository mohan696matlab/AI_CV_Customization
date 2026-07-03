import re
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session
try:
    from .db_schema import Base, Job  # Relative import when called as a module
except ImportError:
    from db_schema import Base, Job   # Absolute import when run as a standalone script



# Database functions

DATABASE_URL = "sqlite:///jobs.db"
engine = create_engine(DATABASE_URL)

def init_db():
    Base.metadata.create_all(engine)

def remove_db():
    Base.metadata.drop_all(engine)


def delete_all_jobs():
    with Session(engine) as session:
        session.execute(delete(Job))
        session.commit()

def add_a_job(job: Job):
    job_id = job.id
    with Session(engine) as session:
        existing_job = session.get(Job, job_id)
        if existing_job is None:
            session.add(job)
            session.commit()
        else:
            print("Job already exists in the database")

def get_all_jobs():
    with Session(engine) as session:
        jobs = session.query(Job).all()
        return [job_to_dict(j) for j in jobs]

def delete_job_by_id(job_id: int):
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if job is not None:
            session.delete(job)
            session.commit()
        else:
            print("Job not found in the database")


# Helper functions
def get_job_id(job_link):
    match = re.search(r"/view/(\d+)/", job_link)
    job_id = int(match.group(1))
    return job_id

def job_to_dict(job):
    return {
        "id": getattr(job, "id", None),
        "job_link": getattr(job, "job_link", None),
        "job_location": getattr(job, "job_location", None),
        "company_name": getattr(job, "company_name", None),
        "job_title": getattr(job, "job_title", None),
        "job_description": getattr(job, "job_description", None),

        "technical_skills_score": getattr(job, "technical_skills_score", 0),
        "tools_frameworks_score": getattr(job, "tools_frameworks_score", 0),
        "experience_score": getattr(job, "experience_score", 0),
        "domain_score": getattr(job, "domain_score", 0),
        "education_score": getattr(job, "education_score", 0),
        "matching_score": getattr(job, "matching_score", 0),

        "review": getattr(job, "review", None),
        "job_keywords": getattr(job, "job_keywords", []),
    }

def dict_to_job(data: dict) -> Job:
    return Job(
        id=get_job_id(data.get("job_link")),
        job_link=data.get("job_link"),
        job_location=data.get("job_location"),
        company_name=data.get("company_name"),
        job_title=data.get("job_title"),
        job_description=data.get("job_description"),

        technical_skills_score=data.get("technical_skills_score", 0),
        tools_frameworks_score=data.get("tools_frameworks_score", 0),
        experience_score=data.get("experience_score", 0),
        domain_score=data.get("domain_score", 0),
        education_score=data.get("education_score", 0),
        matching_score=data.get("matching_score", 0),

        review=data.get("review"),
        job_keywords=data.get("job_keywords", []),
    )

if __name__ == "__main__":
    init_db()