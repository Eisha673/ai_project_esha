from sqlalchemy import select

from ..integrations import calendly, greenhouse, nvidia_nim, openai_client
from ..integrations.nvidia_nim import SAFETY_MODEL
from ..models.candidate import Candidate
from ..models.interview import Interview
from .state import RecruitingState
from .utils import tracked_agent


async def run_interview_agent(state: RecruitingState) -> RecruitingState:
    async def work(session):
        rows = await session.scalars(select(Candidate).where(Candidate.job_id == state["job_id"], Candidate.assessment_pass.is_(True)))
        interviews = []
        for candidate in rows:
            questions = await openai_client.generate_interview_questions(
                {"name": candidate.full_name, "score": candidate.nim_screen_score, "reasoning": candidate.nim_screen_reasoning},
                state.get("role", ""),
            )
            safety = await nvidia_nim.check_bias("\n".join(questions))
            if not safety["is_safe"]:
                state.setdefault("errors", []).append(f"Interview questions bias flagged for {candidate.id}: {safety['raw']}")
                continue
            link = await calendly.create_scheduling_link(candidate.full_name or "Candidate", state.get("role", "Interview"))
            calendly_link = link.get("resource", {}).get("booking_url") or link.get("booking_url") or link.get("url")
            await greenhouse.send_candidate_message(str(candidate.id), "Interview invitation", calendly_link or "")
            interview = Interview(candidate_id=candidate.id, calendly_link=calendly_link, question_bank=questions)
            session.add(interview)
            interviews.append({"candidate_id": str(candidate.id), "calendly_link": calendly_link, "questions": questions})
            candidate.stage = "interviewed"
        await session.commit()
        state["interviews"] = interviews
        state["current_stage"] = "offer"
        state["human_approved"] = True
        state["_bias_model"] = SAFETY_MODEL
        return state

    return await tracked_agent(state, "interview", "openai+nvidia_nim", SAFETY_MODEL, work)
