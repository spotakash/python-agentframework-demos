"""Magentic orchestration with HITL plan review before execution.

Demonstrates: MagenticBuilder(enable_plan_review=True), MagenticPlanReviewRequest,
event_data.approve() / event_data.revise(feedback), and streaming agent output.

A manager agent coordinates a researcher and an analyst to complete a research
task. Before executing the plan, the manager presents it to the human for
review. The human can approve the plan or provide feedback to revise it.

Run:
    uv run examples/workflow_hitl_magentic.py
"""

import asyncio
import json
import os
from typing import cast

from agent_framework import (
    Agent,
    AgentResponseUpdate,
    MagenticPlanReviewRequest,
    Message,
    WorkflowEvent,
)
from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import MagenticBuilder
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv

load_dotenv(override=True)
API_HOST = os.getenv("API_HOST", "github")

# Configure the chat client based on the API host
async_credential = None
if API_HOST == "azure":
    async_credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(async_credential, "https://cognitiveservices.azure.com/.default")
    client = OpenAIChatClient(
        base_url=f"{os.environ['AZURE_OPENAI_ENDPOINT']}/openai/v1/",
        api_key=token_provider,
        model_id=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
    )
elif API_HOST == "github":
    client = OpenAIChatClient(
        base_url="https://models.github.ai/inference",
        api_key=os.environ["GITHUB_TOKEN"],
        model_id=os.getenv("GITHUB_MODEL", "openai/gpt-5-mini"),
    )
else:
    client = OpenAIChatClient(
        api_key=os.environ["OPENAI_API_KEY"], model_id=os.environ.get("OPENAI_MODEL", "gpt-5-mini")
    )


# --- Agents ---

researcher_agent = Agent(
    name="ResearcherAgent",
    description="Specialist in research and information gathering",
    instructions=(
        "You are a Researcher. You find information and provide factual summaries. "
        "Do not perform quantitative analysis — leave that to the analyst."
    ),
    chat_client=client,
)

analyst_agent = Agent(
    name="AnalystAgent",
    description="Specialist in data analysis and quantitative reasoning",
    instructions=(
        "You are an Analyst. You take research findings and perform quantitative analysis, "
        "create comparisons, and produce structured recommendations."
    ),
    chat_client=client,
)

manager_agent = Agent(
    name="MagenticManager",
    description="Orchestrator that coordinates the research and analysis workflow",
    instructions="You coordinate a team to complete complex research tasks efficiently.",
    chat_client=client,
)


# --- Main ---


async def main() -> None:
    """Run the Magentic workflow with HITL plan review."""
    workflow = MagenticBuilder(
        participants=[researcher_agent, analyst_agent],
        manager_agent=manager_agent,
        enable_plan_review=True,
        max_round_count=10,
        max_stall_count=1,
        max_reset_count=2,
    ).build()

    task = (
        "Compare the pros and cons of three popular Python web frameworks "
        "(Django, Flask, and FastAPI) for building a REST API. "
        "Consider performance, ease of use, community support, and async capabilities. "
        "Provide a recommendation for a small startup building their first API."
    )

    print(f"📋 Task: {task}\n")

    pending_request: WorkflowEvent | None = None
    pending_responses: dict | None = None
    output_event: WorkflowEvent | None = None

    while not output_event:
        if pending_responses is not None:
            stream = workflow.run(responses=pending_responses)
        else:
            stream = workflow.run_stream(task)

        last_message_id: str | None = None
        async for event in stream:
            if event.type == "output" and isinstance(event.data, AgentResponseUpdate):
                message_id = event.data.message_id
                if message_id != last_message_id:
                    if last_message_id is not None:
                        print("\n")
                    print(f"🤖 {event.executor_id}: ", end="", flush=True)
                    last_message_id = message_id
                print(event.data, end="", flush=True)

            elif event.type == "request_info" and event.request_type is MagenticPlanReviewRequest:
                pending_request = event

            elif event.type == "output":
                output_event = event

        pending_responses = None

        # Handle plan review request
        if pending_request is not None:
            event_data = cast(MagenticPlanReviewRequest, pending_request.data)

            print("\n\n" + "=" * 60)
            print("📝 PLAN REVIEW REQUESTED")
            print("=" * 60)

            if event_data.current_progress is not None:
                print("\nCurrent Progress:")
                print(json.dumps(event_data.current_progress.to_dict(), indent=2))

            print(f"\nProposed Plan:\n{event_data.plan.text}\n")
            print("Please provide your feedback (press Enter to approve):")

            reply = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
            if reply.strip() == "":
                print("✅ Plan approved.\n")
                pending_responses = {pending_request.request_id: event_data.approve()}
            else:
                print("📝 Plan revised by human.\n")
                pending_responses = {pending_request.request_id: event_data.revise(reply)}
            pending_request = None

    # Final output
    output_messages = cast(list[Message], output_event.data)
    final_output = output_messages[-1].text if output_messages else "No output"
    print(f"\n\n{'=' * 60}")
    print("📊 FINAL RESULT")
    print("=" * 60)
    print(final_output)

    if async_credential:
        await async_credential.close()


if __name__ == "__main__":
    asyncio.run(main())
