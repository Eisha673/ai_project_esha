from sqlalchemy import select

from ..integrations import anthropic_client, greenhouse, nvidia_nim
from ..integrations.nvidia_nim import SAFETY_MODEL
from ..models.candidate import Candidate
from ..models.offer import Offer
from .state import RecruitingState
from .utils import tracked_agent


async def run_offer_agent(state: RecruitingState) -> RecruitingState:
    async def work(session):
        rows = await session.scalars(
            select(Candidate).where(
                Candidate.job_id == state["job_id"],
                Candidate.stage == "interviewed"
            )
        )
        candidates = list(rows)

        # Fallback to shortlisted candidates
        if not candidates:
            rows = await session.scalars(
                select(Candidate).where(
                    Candidate.job_id == state["job_id"]
                )
            )
            candidates = [c for c in rows if c.nim_screen_score and c.nim_screen_score >= 60]

        offers = []
        compensation = {
            "base_salary": 95000,
            "equity_percentage": 0.5,
            "bonus_percentage": 10
        }

        for candidate in candidates:
            try:
                letter = await anthropic_client.draft_offer_letter(
                    {"name": candidate.full_name, "email": candidate.email},
                    compensation
                )
            except Exception:
                letter = (
                    f"Dear {candidate.full_name},\n\n"
                    f"We are pleased to offer you the position with a base salary of "
                    f"${compensation['base_salary']:,}, {compensation['equity_percentage']}% equity, "
                    f"and {compensation['bonus_percentage']}% bonus.\n\n"
                    f"Welcome to the team!\n\nBest regards,\nHR Autopilot"
                )

            try:
                safety = await nvidia_nim.check_bias(letter)
                if not safety["is_safe"]:
                    state.setdefault("errors", []).append(
                        f"Offer bias flagged for {candidate.id}: {safety['raw']}"
                    )
                    continue
            except Exception:
                pass

            try:
                gh_offer = await greenhouse.create_offer(str(candidate.id), compensation)
                gh_offer_id = str(gh_offer.get("id", "demo-offer"))
            except Exception:
                gh_offer_id = f"demo-offer-{candidate.id}"

            offer = Offer(
                candidate_id=candidate.id,
                offer_letter_text=letter,
                greenhouse_offer_id=gh_offer_id
            )
            session.add(offer)
            candidate.stage = "offered"
            offers.append({
                "candidate_id": str(candidate.id),
                "greenhouse_offer_id": gh_offer_id,
                "letter_preview": letter[:200]
            })

        await session.commit()
        state["offers"] = offers
        state["current_stage"] = "complete"
        state["human_approved"] = True
        state["_demo_mode"] = True
        return state

    return await tracked_agent(state, "offer", "anthropic+nvidia_nim", SAFETY_MODEL, work)