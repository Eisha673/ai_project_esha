from sqlalchemy import select

from ..integrations import anthropic_client, greenhouse, nvidia_nim
from ..integrations.nvidia_nim import SAFETY_MODEL
from ..models.candidate import Candidate
from ..models.offer import Offer
from .state import RecruitingState
from .utils import tracked_agent


async def run_offer_agent(state: RecruitingState) -> RecruitingState:
    async def work(session):
        rows = await session.scalars(select(Candidate).where(Candidate.job_id == state["job_id"], Candidate.stage == "interviewed"))
        offers = []
        for candidate in rows:
            compensation = {"base_salary": 0, "equity_percentage": 0, "bonus_percentage": 0}
            letter = await anthropic_client.draft_offer_letter({"name": candidate.full_name, "email": candidate.email}, compensation)
            safety = await nvidia_nim.check_bias(letter)
            if not safety["is_safe"]:
                state.setdefault("errors", []).append(f"Offer bias flagged for {candidate.id}: {safety['raw']}")
                continue
            gh_offer = await greenhouse.create_offer(str(candidate.id), compensation)
            offer = Offer(candidate_id=candidate.id, offer_letter_text=letter, greenhouse_offer_id=str(gh_offer.get("id", "")))
            session.add(offer)
            candidate.stage = "offered"
            offers.append({"candidate_id": str(candidate.id), "greenhouse_offer_id": offer.greenhouse_offer_id})
        await session.commit()
        state["offers"] = offers
        state["current_stage"] = "complete"
        state["human_approved"] = True
        state["_bias_model"] = SAFETY_MODEL
        return state

    return await tracked_agent(state, "offer", "anthropic+nvidia_nim", SAFETY_MODEL, work)
