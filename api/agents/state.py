from typing import Any, Literal, TypedDict


class RecruitingState(TypedDict, total=False):
    job_id: str
    role: str
    department: str
    seniority: str
    notes: str
    skills: list[str]
    location: str
    job_requirements: str
    jd_text: str
    greenhouse_job_id: str
    linkedin_job_url: str
    candidates: list[dict[str, Any]]
    shortlist: list[dict[str, Any]]
    assessments: dict[str, Any]
    interviews: list[dict[str, Any]]
    offers: list[dict[str, Any]]
    current_stage: Literal["jd", "search", "assessment", "interview", "offer", "complete"]
    human_approved: bool
    errors: list[str]
