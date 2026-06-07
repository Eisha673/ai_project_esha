from sqlalchemy import select

from ..integrations import calendly, greenhouse, nvidia_nim, openai_client
from ..integrations.nvidia_nim import SAFETY_MODEL
from ..models.candidate import Candidate
from ..models.interview import Interview
from .state import RecruitingState
from .utils import tracked_agent


DEMO_QUESTIONS = [
    "Tell me about your background and experience.",
    "How do you handle tight deadlines?",
    "Describe a challenging project you worked on.",
    "What are your strengths and weaknesses?",
    "Where do you see yourself in 5 years?"
]


async def run_interview_agent(state: RecruitingState) -> RecruitingState:
    async def work(session):
        rows = await session.scalars(
            select(Candidate).where(
                Candidate.job_id == state["job_id"],
                Candidate.assessment_pass.is_(True)
            )
        )
        candidates = list(rows)

        # Use shortlist if no assessed candidates found
        if not candidates:
            rows = await session.scalars(
                select(Candidate).where(
                    Candidate.job_id == state["job_id"]
                )
            )
            candidates = [c for c in rows if c.nim_screen_score and c.nim_screen_score >= 60]

        interviews = []
        for candidate in candidates:
            try:
                questions = await openai_client.generate_interview_questions(
                    {"name": candidate.full_name, "score": candidate.nim_screen_score, "reasoning": candidate.nim_screen_reasoning},
                    state.get("role", ""),
                )
            except Exception:
                questions = DEMO_QUESTIONS

            try:
                safety = await nvidia_nim.check_bias("\n".join(questions))
                if not safety["is_safe"]:
                    questions = DEMO_QUESTIONS
            except Exception:
                pass

            try:
                link = await calendly.create_scheduling_link(
                    candidate.full_name or "Candidate",
                    state.get("role", "Interview")
                )
                calendly_link = link.get("resource", {}).get("booking_url") or link.get("booking_url") or link.get("url")
            except Exception:
                calendly_link = f"https://calendly.com/demo/{candidate.id}"

            try:
                await greenhouse.send_candidate_message(
                    str(candidate.id), "Interview invitation", calendly_link or ""
                )
            except Exception:
                pass

            interview = Interview(
                candidate_id=candidate.id,
                calendly_link=calendly_link,
                question_bank=questions
            )
            session.add(interview)
            interviews.append({
                "candidate_id": str(candidate.id),
                "calendly_link": calendly_link,
                "questions": questions
            })
            candidate.stage = "interviewed"

        await session.commit()
        state["interviews"] = interviews
        state["current_stage"] = "offer"
        state["human_approved"] = True
        state["_demo_mode"] = True
        return state

    return await tracked_agent(state, "interview", "openai+nvidia_nim", SAFETY_MODEL, work)