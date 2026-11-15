
import logging
import time
from uuid import uuid4
import json

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from researchforge.config import (
    APP_NAME,
    USER_ID,
    validate_config,
)
from researchforge.agent import root_agent
from researchforge.tools.citation_validation import validate_report_structure


logger = logging.getLogger(__name__)

AGENT_NAMES = {
    "research_agent": "Research",
    "analysis_agent": "Analysis",
    "report_agent": "Report",
    "reviewer_agent": "Reviewer",
}

AGENT_PROVIDERS = {
    "research_agent": "Groq",
    "analysis_agent": "Groq",
    "report_agent": "Gemini",
    "reviewer_agent": "Gemini",
}


def get_token_count(usage, field):
    """Safely extract token counts from ADK usage metadata."""
    if usage is None:
        return 0

    if isinstance(usage, dict):
        value = usage.get(field, 0)
    else:
        value = getattr(usage, field, 0)

    return value or 0


def create_usage_counter():
    """Initialize provider and agent token counters."""

    providers = {
        "Groq": {"input": 0, "output": 0, "total": 0},
        "Gemini": {"input": 0, "output": 0, "total": 0},
    }

    agents = {}

    return providers, agents


async def run_research_workflow(topic: str) -> str:
    """Run the ADK sequential workflow and return the final reviewed report."""

    if not topic or not topic.strip():
        raise ValueError("Research topic cannot be empty.")

    validate_config()

    session_id = f"research-{uuid4().hex[:12]}"

    logger.info("=" * 60)
    logger.info("RESEARCHFORGE WORKFLOW STARTED")
    logger.info("Topic: %s", topic.strip())
    logger.info("Session: %s", session_id)
    logger.info("=" * 60)

    sessions = InMemorySessionService()

    await sessions.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=sessions,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(text=f"Research topic: {topic.strip()}")
        ],
    )

    final_text = ""

    workflow_start = time.perf_counter()
    agent_start_times = {}
    completed_agents = set()

    token_usage, agent_token_usage = create_usage_counter()

    try:
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session_id,
            new_message=message,
        ):

            author = getattr(event, "author", None)

            # ----------------------------------------
            # 1. Agent execution monitoring
            # ----------------------------------------

            if author in AGENT_NAMES:
                agent_name = AGENT_NAMES[author]

                if author not in agent_start_times:
                    agent_start_times[author] = time.perf_counter()

                    logger.info(
                        "[START] %s Agent | Provider: %s",
                        agent_name,
                        AGENT_PROVIDERS[author],
                    )

                if (
                    event.is_final_response()
                    and author not in completed_agents
                ):
                    duration = (
                        time.perf_counter()
                        - agent_start_times[author]
                    )

                    completed_agents.add(author)

                    logger.info(
                        "[COMPLETED] %s Agent | ADK turn wall time: %.2f seconds",
                        agent_name,
                        duration,
                    )
                    logger.info(
                        "Timing note: ADK event timing includes orchestration and tool waits; "
                        "it is not isolated provider/model-call latency."
                    )



            # ----------------------------------------
            # Tool call and result size monitoring
            # ----------------------------------------

            if event.content and event.content.parts:
                for part in event.content.parts:

                    function_call = getattr(part, "function_call", None)

                    if function_call:
                        args_size = len(
                            json.dumps(
                                function_call.args or {},
                                default=str
                            )
                        )

                        logger.info(
                            "[TOOL CALL] %s | Arguments: %d characters",
                            function_call.name,
                            args_size,
                        )

                    function_response = getattr(
                        part,
                        "function_response",
                        None
                    )

                    if function_response:
                        result_size = len(
                            json.dumps(
                                function_response.response,
                                default=str
                            )
                        )

                        logger.info(
                            "[TOOL RESULT] %s | Result: %d characters",
                            function_response.name,
                            result_size,
                        )

            # ----------------------------------------
            # 2. Token usage monitoring
            # ----------------------------------------

            usage = getattr(event, "usage_metadata", None)

            if usage and author in AGENT_NAMES:

                input_tokens = get_token_count(
                    usage,
                    "prompt_token_count",
                )

                output_tokens = get_token_count(
                    usage,
                    "candidates_token_count",
                )

                total_tokens = get_token_count(
                    usage,
                    "total_token_count",
                )

                if total_tokens == 0:
                    total_tokens = input_tokens + output_tokens

                provider = AGENT_PROVIDERS[author]

                if author not in agent_token_usage:
                    agent_token_usage[author] = {
                        "input": 0,
                        "output": 0,
                        "total": 0,
                    }

                agent_token_usage[author]["input"] += input_tokens
                agent_token_usage[author]["output"] += output_tokens
                agent_token_usage[author]["total"] += total_tokens

                token_usage[provider]["input"] += input_tokens
                token_usage[provider]["output"] += output_tokens
                token_usage[provider]["total"] += total_tokens

                # Log token usage for each model response immediately
                logger.info(
                    "[TOKEN EVENT] Agent: %s | Provider: %s | Input: %d | "
                    "Output: %d | Total: %d",
                    AGENT_NAMES[author],
                    provider,
                    input_tokens,
                    output_tokens,
                    total_tokens,
                )

            # ----------------------------------------
            # 3. Capture final workflow response
            # ----------------------------------------

            if (
                event.is_final_response()
                and event.content
                and event.content.parts
            ):
                final_text = "\n".join(
                    part.text
                    for part in event.content.parts
                    if getattr(part, "text", None)
                ).strip()

        workflow_duration = time.perf_counter() - workflow_start

        if not final_text:
            logger.warning(
                "Workflow completed without final text."
            )

            return (
                "No final report was returned. "
                "Check logs, model access, and API configuration."
            )

        # ----------------------------------------
        # 4. Deterministic final structure check
        # ----------------------------------------

        structure_check = validate_report_structure(final_text)
        logger.info(
            "Final report structure | Valid: %s | Headings: %d/%d | Missing: %s | References content: %s",
            structure_check["valid"],
            structure_check["headings_present"],
            structure_check["required_headings"],
            structure_check["missing_headings"],
            structure_check["references_section_has_content"],
        )
        if not structure_check["valid"]:
            logger.warning("Final report failed deterministic structural validation: %s", structure_check)

        # ----------------------------------------
        # 5. Workflow summary
        # ----------------------------------------

        logger.info("=" * 60)
        logger.info("RESEARCHFORGE WORKFLOW COMPLETED")

        logger.info(
            "Agents completed: %d/%d",
            len(completed_agents),
            len(AGENT_NAMES),
        )

        logger.info(
            "Total execution time: %.2f seconds",
            workflow_duration,
        )

        logger.info(
            "Final report length: %d characters",
            len(final_text),
        )

        # ----------------------------------------
        # 6. Per-agent token usage
        # ----------------------------------------

        logger.info("-" * 60)
        logger.info("TOKEN USAGE BY AGENT")

        for agent, usage in agent_token_usage.items():
            logger.info(
                "%s | Input: %d | Output: %d | Total: %d",
                AGENT_NAMES.get(agent, agent),
                usage["input"],
                usage["output"],
                usage["total"],
            )

        # ----------------------------------------
        # 7. Provider token totals
        # ----------------------------------------

        logger.info("-" * 60)
        logger.info("TOKEN USAGE BY PROVIDER")

        for provider, usage in token_usage.items():
            logger.info(
                "%s | Input: %d | Output: %d | Total: %d",
                provider,
                usage["input"],
                usage["output"],
                usage["total"],
            )

        logger.info("=" * 60)

        return final_text

    except Exception:
        logger.exception("ResearchForge workflow failed.")
        raise
