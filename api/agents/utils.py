import time
from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from ..database import AsyncSessionLocal
from ..models.agent_run import AgentRun


async def log_agent_run(
    session: AsyncSession,
    job_id: str | None,
    agent_name: str,
    llm_provider: str,
    nim_model: str | None,
    status: str,
    input_summary: str = "",
    output_summary: str = "",
    duration_ms: int | None = None,
):
    session.add(
        AgentRun(
            job_id=job_id,
            agent_name=agent_name,
            llm_provider=llm_provider,
            nim_model=nim_model,
            status=status,
            input_summary=input_summary[:2000],
            output_summary=output_summary[:4000],
            duration_ms=duration_ms,
        )
    )
    await session.commit()


async def tracked_agent(state: dict, agent_name: str, provider: str, nim_model: str | None, fn: Callable[[AsyncSession], Awaitable[dict]]) -> dict:
    start = time.perf_counter()
    async with AsyncSessionLocal() as session:
        try:
            updated = await fn(session)
            await log_agent_run(
                session,
                state.get("job_id"),
                agent_name,
                provider,
                nim_model,
                "done" if not updated.get("errors") else "failed",
                input_summary=str({k: state.get(k) for k in ("job_id", "current_stage")}),
                output_summary=str(updated.get("errors") or updated.get("current_stage")),
                duration_ms=int((time.perf_counter() - start) * 1000),
            )
            return updated
        except Exception as exc:
            state.setdefault("errors", []).append(str(exc))
            await log_agent_run(
                session,
                state.get("job_id"),
                agent_name,
                provider,
                nim_model,
                "failed",
                output_summary=str(exc),
                duration_ms=int((time.perf_counter() - start) * 1000),
            )
            return state
