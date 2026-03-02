# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "python-pptx",
# ]
# ///
"""Generate the HITL presentation PPTX from the AdvancedWorkflows template.

Usage:
    uv run presentations/generate_hitl_pptx.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".github" / "skills" / "pptx-from-template"))
from pptx_from_template import create_pptx_from_template  # noqa: E402

TEMPLATE = Path(__file__).resolve().parent.parent / "PythonAgents-AdvancedWorkflows.pptx"
OUTPUT = Path(__file__).resolve().parent.parent / "PythonAgents-HITLWorkflows.pptx"

# Layout indices from inspecting the template:
# 0  = '2_Section Header - option 2' (title slide with subtitle + speaker info)
# 1  = '3_Section Header - option 2' (section dividers)
# 6  = 'Content - option 3' (content + title, "Today we'll cover" style)
# 7  = 'Content - option 4' (title + content, most code/content slides)
# 10 = 'Title and Content' (series overview slide)

LAYOUT_TITLE_SLIDE = 0
LAYOUT_SECTION = 1
LAYOUT_CONTENT_ALT = 6
LAYOUT_CONTENT = 7
LAYOUT_SERIES = 10

slides = [
    # Slide 1: Series overview
    {
        "layout_index": LAYOUT_SERIES,
        "title": "Python + Agents",
        "body": (
            "Feb 24: Building your first agent in Python\n"
            "Feb 25: Adding context and memory to agents\n"
            "Feb 26: Monitoring and evaluating agents\n"
            "Mar 3: Building your first AI-driven workflows\n"
            "Mar 4: Orchestrating advanced multi-agent workflows\n"
            "Mar 5: Adding a human-in-the-loop to workflows \u2190 Today\n"
            "\n"
            "Register at aka.ms/PythonAgents/series"
        ),
    },
    # Slide 2: Title slide
    {
        "layout_index": LAYOUT_TITLE_SLIDE,
        "title": "Python + Agents",
        "body": "Adding a human-in-the-loop to workflows",
        "notes": "aka.ms/pythonagents/slides/hitlworkflows\nPamela Fox\nPython Cloud Advocate\nwww.pamelafox.org",
    },
    # Slide 3: Today we'll cover...
    {
        "layout_index": LAYOUT_CONTENT_ALT,
        "title": "Today we\u2019ll cover\u2026",
        "bullets": [
            "Why HITL matters for agentic workflows",
            "Requests and responses: structured human interaction",
            "Tool approval: gating sensitive operations",
            "Checkpoints and resuming: durable HITL workflows",
            "Handoff with HITL: interactive multi-agent routing",
            "Magentic with HITL: plan review before execution",
        ],
    },
    # Slide 4: Follow along
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Want to follow along?",
        "body": (
            '1. Open this GitHub repository:\n'
            '   aka.ms/python-agentframework-demos\n'
            '\n'
            '2. Use "Code" button to create a GitHub Codespace\n'
            '\n'
            '3. Wait a few minutes for Codespace to start up'
        ),
    },
    # Slide 5: Recap - What's an agentic workflow?
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Recap: What\u2019s an agentic workflow?",
        "body": (
            "An agentic workflow is a flow that involves an agent at some point,\n"
            "typically to handle decision making or answer synthesis.\n"
            "\n"
            "In agent-framework, a workflow is a graph with Executor nodes and edges between:\n"
            "\n"
            "  Executor  \u2192 edge \u2192  Executor  \u2192 edge \u2192  Executor\n"
            "  Input                                                    Output"
        ),
    },
    # Slide 6: Section — Why HITL?
    {
        "layout_index": LAYOUT_SECTION,
        "title": "Why add a human in the loop?",
    },
    # Slide 7: Why HITL matters
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Why add a human in the loop?",
        "body": (
            "LLMs can produce uncertain, inconsistent, or incorrect outputs.\n"
            "\n"
            "Human checkpoints provide:\n"
            "\n"
            "\u2022 Accuracy \u2014 Verify factual correctness before acting\n"
            "\u2022 Safety \u2014 Gate sensitive operations (refunds, emails, deployments)\n"
            "\u2022 Trust \u2014 Users see what the system will do before it acts\n"
            "\u2022 Compliance \u2014 Audit trail of human approvals for regulated workflows\n"
            "\u2022 Control \u2014 Humans can redirect, refine, or halt a workflow at any point"
        ),
    },
    # Slide 8: HITL patterns overview
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "HITL patterns in agent-framework",
        "body": (
            "Requests & Responses\n"
            "  Workflow needs human input to continue (answers, choices, feedback)\n"
            "\n"
            "Tool Approval\n"
            "  Sensitive tool calls must be approved before execution\n"
            "\n"
            "Checkpoints & Resuming\n"
            "  Long-running tasks where human may not be immediately available\n"
            "\n"
            "Handoff + HITL\n"
            "  Multi-agent routing with interactive user input between handoffs\n"
            "\n"
            "Magentic + HITL\n"
            "  Complex planning with human review before executing multi-step plans"
        ),
    },
    # Slide 9: Section — Requests and Responses
    {
        "layout_index": LAYOUT_SECTION,
        "title": "Requests and Responses",
        "body": "https://learn.microsoft.com/agent-framework/workflows/requests-and-responses",
    },
    # Slide 10: How request_info works
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "How requests and responses work",
        "body": (
            "Executors can pause a workflow and ask for human input:\n"
            "\n"
            "The request_info/response cycle is driven by application code:\n"
            "  1. Executor calls ctx.request_info(request_data=..., response_type=str)\n"
            "  2. Workflow emits WorkflowEvent with type=\"request_info\"\n"
            "  3. Application collects event, prompts user, gathers reply\n"
            "  4. Application calls workflow.run(responses={request_id: reply})\n"
            "  5. @response_handler receives the original request + user reply"
        ),
        "notes": (
            "Executor A calls ctx.request_info() -> workflow pauses\n"
            "Human responds -> @response_handler fires -> workflow resumes"
        ),
    },
    # Slide 11: Trip planner example code
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Example: Trip planner with HITL",
        "code": (
            'class TripCoordinator(Executor):\n'
            '  @handler\n'
            '  async def on_agent_response(self, result: AgentExecutorResponse, ctx):\n'
            '    response = PlannerOutput.model_validate_json(\n'
            '        result.agent_response.text)\n'
            '    if response.status == "need_info":\n'
            '      await ctx.request_info(\n'
            '        request_data=ClarificationRequest(\n'
            '            question=response.question),\n'
            '        response_type=str)\n'
            '    else:\n'
            '      await ctx.yield_output(response.itinerary)\n'
            '\n'
            '  @response_handler\n'
            '  async def on_human_answer(self, original_request, answer, ctx):\n'
            '    await ctx.send_message(AgentExecutorRequest(\n'
            '      messages=[Message("user", text=answer)],\n'
            '      should_respond=True))'
        ),
        "notes": (
            "User starts with a vague request: 'I want to go somewhere warm.'\n"
            "Agent asks clarifying questions one at a time, human answers each.\n"
            "Full example: workflow_hitl_requests.py"
        ),
    },
    # Slide 12: Trip planner event loop
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Driving the HITL loop from application code",
        "code": (
            'vague_request = "I want to go somewhere warm next month"\n'
            'stream = workflow.run(vague_request, stream=True)\n'
            '\n'
            'while True:\n'
            '  pending = {}\n'
            '  async for event in stream:\n'
            '    if event.type == "request_info":\n'
            '      pending[event.request_id] = event.data\n'
            '    elif event.type == "output":\n'
            '      print(f"Itinerary:\\n{event.data}")\n'
            '\n'
            '  if not pending:\n'
            '    break\n'
            '\n'
            '  for request_id, request in pending.items():\n'
            '    print(f"Agent asks: {request.question}")\n'
            '    answer = input("Your answer: ")\n'
            '    pending[request_id] = answer\n'
            '\n'
            '  stream = workflow.run(stream=True, responses=pending)'
        ),
        "notes": "Full example: workflow_hitl_requests.py",
    },
    # Slide 13: Section — Tool Approval
    {
        "layout_index": LAYOUT_SECTION,
        "title": "Tool Approval",
        "body": "https://learn.microsoft.com/agent-framework/workflows/tool-approval",
    },
    # Slide 14: Why tool approval?
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Why require tool approval?",
        "body": (
            "Without approval:\n"
            "  Agent decides to send email \u2192 Tool executes automatically\n"
            "  Email sent (possibly wrong!)\n"
            "\n"
            "With approval:\n"
            "  Agent wants to send email \u2192 Workflow pauses\n"
            '  Human reviews: "Send to alice@contoso?"\n'
            "  Human approves \u2713 or rejects \u2717\n"
            "  Tool executes only if approved\n"
            "\n"
            "Use approval for:\n"
            "\u2022 Financial operations (refunds, purchases)\n"
            "\u2022 Communications (emails, messages)\n"
            "\u2022 Destructive operations (deletions, deployments)\n"
            "\u2022 Any irreversible action"
        ),
    },
    # Slide 15: Tool approval code
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Defining tools that require approval",
        "code": (
            '@tool(approval_mode="always_require")\n'
            'async def send_email(\n'
            '  to: Annotated[str, "Recipient email address"],\n'
            '  subject: Annotated[str, "Email subject"],\n'
            '  body: Annotated[str, "Email body"],\n'
            ') -> str:\n'
            '  """Send an email."""\n'
            '  return "Email sent successfully."\n'
            '\n'
            '@tool(approval_mode="never_require")\n'
            'def get_current_date() -> str:\n'
            '  """Get the current date."""\n'
            '  return "2026-03-05"\n'
            '\n'
            '# approval_mode options:\n'
            '#   "always_require" - Always pause for approval\n'
            '#   "never_require"  - Never pause (default)'
        ),
        "notes": "Full example: workflow_hitl_tool_approval.py",
    },
    # Slide 16: Handling approval events
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Handling tool approval in the event loop",
        "code": (
            'events = await workflow.run(incoming_email)\n'
            'request_info_events = events.get_request_info_events()\n'
            '\n'
            'while request_info_events:\n'
            '  responses = {}\n'
            '  for event in request_info_events:\n'
            '    data = event.data\n'
            '    if data.type == "function_approval_request":\n'
            '      args = data.function_call.parse_arguments()\n'
            '      print(f"Tool: {data.function_call.name}")\n'
            '      print(f"Args: {args}")\n'
            '\n'
            '      approved = input("Approve? (y/n): ") == "y"\n'
            '      responses[event.request_id] = (\n'
            '        data.to_function_approval_response(\n'
            '            approved=approved))\n'
            '\n'
            '  events = await workflow.run(responses=responses)\n'
            '  request_info_events = events.get_request_info_events()'
        ),
        "notes": "Full example: workflow_hitl_tool_approval.py",
    },
    # Slide 17: Section — Checkpoints & Resuming
    {
        "layout_index": LAYOUT_SECTION,
        "title": "Checkpoints & Resuming",
        "body": "https://learn.microsoft.com/agent-framework/workflows/checkpoints",
    },
    # Slide 18: Why checkpoints for HITL?
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Why checkpoints for HITL workflows?",
        "body": (
            "Without checkpoints:\n"
            "  Workflow pauses for approval \u2192 Human is offline\n"
            "  Process crashes or restarts \u2192 \u274c All progress lost!\n"
            "\n"
            "With checkpoints:\n"
            "  Workflow pauses for approval \u2192 Human is offline\n"
            "  Checkpoint saved to disk \U0001f4be \u2192 Process can safely exit\n"
            "  ...hours later...\n"
            "  New process starts \u2192 Loads checkpoint from disk \U0001f4c2\n"
            "  Human provides approval \u2192 \u2705 Workflow resumes\n"
            "\n"
            "Checkpoints capture:\n"
            "\u2022 Executor states\n"
            "\u2022 Pending messages\n"
            "\u2022 Pending requests\n"
            "\u2022 Shared state"
        ),
    },
    # Slide 19: Checkpoint code setup
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Setting up checkpointed HITL workflows",
        "code": (
            'from agent_framework import (\n'
            '    FileCheckpointStorage, WorkflowBuilder)\n'
            '\n'
            'checkpoint_storage = FileCheckpointStorage(\n'
            '    storage_path="./checkpoints")\n'
            '\n'
            'workflow = (WorkflowBuilder(\n'
            '    start_executor=prepare_brief,\n'
            '    checkpoint_storage=checkpoint_storage)\n'
            '  .add_edge(prepare_brief, writer)\n'
            '  .add_edge(writer, review_gateway)\n'
            '  .add_edge(review_gateway, writer)  # revisions loop\n'
            '  .build())\n'
            '\n'
            '# Checkpoints saved automatically at end of each\n'
            '# superstep. When request_info is pending, status\n'
            '# is "awaiting human response".'
        ),
        "notes": "Full example: workflow_hitl_checkpoint.py",
    },
    # Slide 20: Resuming from checkpoint
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Resuming a workflow from a checkpoint",
        "code": (
            '# List available checkpoints\n'
            'checkpoints = await storage.list_checkpoints(\n'
            '    workflow_name=workflow.name)\n'
            '\n'
            '# Create a NEW workflow instance (fresh state)\n'
            'new_workflow = create_workflow(\n'
            '    checkpoint_storage=storage)\n'
            '\n'
            '# Resume from the checkpoint\n'
            'stream = new_workflow.run(\n'
            '  checkpoint_id=chosen.checkpoint_id,\n'
            '  stream=True)\n'
            '\n'
            '# Continue the HITL loop as normal\n'
            'async for event in stream:\n'
            '  if event.type == "request_info":\n'
            '    # Prompt user, collect response...\n'
            '  elif event.type == "output":\n'
            '    print(f"Result: {event.data}")'
        ),
        "notes": "Full example: workflow_hitl_checkpoint.py",
    },
    # Slide 21: Saving executor state
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Saving custom executor state in checkpoints",
        "code": (
            'class ReviewGateway(Executor):\n'
            '  def __init__(self, id: str):\n'
            '    super().__init__(id=id)\n'
            '    self._iteration = 0\n'
            '\n'
            '  @handler\n'
            '  async def on_agent_response(self, response, ctx):\n'
            '    self._iteration += 1\n'
            '    await ctx.request_info(\n'
            '      request_data=HumanApprovalRequest(\n'
            '        draft=response.agent_response.text,\n'
            '        iteration=self._iteration),\n'
            '      response_type=str)\n'
            '\n'
            '  async def on_checkpoint_save(self):\n'
            '    return {"iteration": self._iteration}\n'
            '\n'
            '  async def on_checkpoint_restore(self, state):\n'
            '    self._iteration = state.get("iteration", 0)'
        ),
        "notes": "Full example: workflow_hitl_checkpoint.py",
    },
    # Slide 22: Section — Handoff with HITL
    {
        "layout_index": LAYOUT_SECTION,
        "title": "Handoff with HITL",
        "body": "https://learn.microsoft.com/agent-framework/workflows/orchestrations/handoff",
    },
    # Slide 23: Recap Handoff orchestration
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Recap: Handoff orchestration",
        "body": (
            "No edges defined \u2014 routing emerges from conversation state.\n"
            "\n"
            "Unlike other orchestrations, Handoff is inherently interactive:\n"
            "\u2022 When an agent doesn\u2019t handoff, it requests user input\n"
            "\u2022 Workflow emits HandoffAgentUserRequest events\n"
            "\u2022 Application must respond for the workflow to continue\n"
            "\u2022 Use .with_autonomous_mode() to skip user input"
        ),
        "notes": "Previously covered in Advanced Workflows session. This is recap.",
    },
    # Slide 24: Handoff with user input + tool approval
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Handoff with user input and tool approval",
        "code": (
            '@tool(approval_mode="always_require")\n'
            'def process_refund(order_number: str) -> str:\n'
            '  """Process a refund for a given order."""\n'
            '  return f"Refund processed for {order_number}."\n'
            '\n'
            'workflow = (HandoffBuilder(\n'
            '    name="customer_support",\n'
            '    participants=[triage, refund_agent, order_agent])\n'
            '  .with_start_agent(triage)\n'
            '  .build())\n'
            '\n'
            '# Event loop handles BOTH types of requests:\n'
            'for event in pending_requests:\n'
            '  if isinstance(event.data, HandoffAgentUserRequest):\n'
            '    resp = HandoffAgentUserRequest.create_response(\n'
            '        user_input)\n'
            '    # Or: HandoffAgentUserRequest.terminate()\n'
            '  elif isinstance(event.data, FunctionApprovalRequest):\n'
            '    resp = event.data.create_response(approved=True)'
        ),
        "notes": (
            "Full example: workflow_hitl_handoff.py\n"
            "For durable handoff workflows, add checkpoint_storage to HandoffBuilder:\n"
            "HandoffBuilder(..., checkpoint_storage=FileCheckpointStorage('./checkpoints'))"
        ),
    },
    # Slide 25: Section — Magentic with HITL
    {
        "layout_index": LAYOUT_SECTION,
        "title": "Magentic with HITL",
        "body": "https://learn.microsoft.com/agent-framework/workflows/orchestrations/magentic",
    },
    # Slide 26: Magentic plan review
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Magentic orchestration with HITL plan review",
        "body": (
            "The Magentic orchestrator creates a plan before delegating to agents.\n"
            "With HITL plan review, humans can:\n"
            "\u2022 Approve the proposed plan\n"
            "\u2022 Revise the plan with feedback\n"
            "\n"
            "Enable with:\n"
            "  workflow = MagenticBuilder(\n"
            "    participants=[...],\n"
            "    enable_plan_review=True,\n"
            "    manager_agent=manager_agent,\n"
            "  ).build()"
        ),
    },
    # Slide 27: Magentic HITL code
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Handling Magentic plan review requests",
        "code": (
            'async for event in workflow.run_stream(task):\n'
            '  if (event.type == "output"\n'
            '      and isinstance(event.data,\n'
            '          AgentResponseUpdate)):\n'
            '    print(event.data, end="", flush=True)\n'
            '  elif (event.type == "request_info"\n'
            '        and event.request_type\n'
            '            is MagenticPlanReviewRequest):\n'
            '    plan_request = event\n'
            '\n'
            'if plan_request:\n'
            '  data = plan_request.data\n'
            '  print(f"Plan:\\n{data.plan.text}")\n'
            '  reply = input("Feedback (Enter=approve): ")\n'
            '  if reply.strip() == "":\n'
            '    resp = {plan_request.request_id:\n'
            '            data.approve()}\n'
            '  else:\n'
            '    resp = {plan_request.request_id:\n'
            '            data.revise(reply)}\n'
            '  async for event in workflow.run(\n'
            '      responses=resp): ...'
        ),
        "notes": "Full example: workflow_hitl_magentic.py",
    },
    # Slide 28: HITL patterns comparison
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Choosing the right HITL pattern",
        "body": (
            "Pattern                Trigger                          Best for\n"
            "\n"
            "Requests &             ctx.request_info()               General Q&A,\n"
            "Responses              in any Executor                  feedback loops\n"
            "\n"
            "Tool Approval          @tool(approval_mode=             Gating sensitive\n"
            '                       "always_require")                operations\n'
            "\n"
            "Checkpoints            FileCheckpointStorage            Long-running tasks,\n"
            "                                                        offline humans\n"
            "\n"
            "Handoff HITL           HandoffBuilder (no               Interactive multi-\n"
            "                       autonomous_mode)                 agent routing\n"
            "\n"
            "Magentic HITL          MagenticBuilder(enable_          Complex planning\n"
            "                       plan_review=True)                with review"
        ),
    },
    # Slide 29: Next steps / resources
    {
        "layout_index": LAYOUT_CONTENT,
        "title": "Next steps",
        "body": (
            "Register: https://aka.ms/PythonAgents/series\n"
            "\n"
            "Watch past recordings: aka.ms/pythonagents/resources\n"
            "\n"
            "Join office hours after each session in Discord:\n"
            "aka.ms/pythonai/oh\n"
            "\n"
            "Feb 24: Building your first agent in Python\n"
            "Feb 25: Adding context and memory to agents\n"
            "Feb 26: Monitoring and evaluating agents\n"
            "Mar 3: Building your first AI-driven workflows\n"
            "Mar 4: Orchestrating advanced multi-agent workflows\n"
            "Mar 5: Adding a human-in-the-loop to workflows \u2190 Today"
        ),
    },
]

if __name__ == "__main__":
    create_pptx_from_template(TEMPLATE, OUTPUT, slides)
