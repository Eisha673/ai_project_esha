import asyncio
from uuid import UUID
from api.database import get_session
from api.models.pipeline_state import PipelineState
from api.agents.jd_agent import run_jd_agent

async def test():
    job_id = '455b9e9d-d872-451c-8f43-91a3a18a918e'
    print("Getting session...")
    async for session in get_session():
        print("Got session!")
        row = await session.get(PipelineState, UUID(job_id))
        print("Row:", row)
        if not row:
            print("NO ROW FOUND!")
            return
        state = dict(row.state_json)
        state["job_id"] = job_id
        print("State:", state)
        print("Running JD agent...")
        updated = await run_jd_agent(state)
        print("Updated stage:", updated.get("current_stage"))
        row.current_stage = updated.get("current_stage")
        row.human_approved = updated.get("human_approved", False)
        row.state_json = updated
        await session.commit()
        print("Done! New stage:", updated.get("current_stage"))
        break

asyncio.run(test())