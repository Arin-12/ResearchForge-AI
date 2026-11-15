
import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm
from google.adk.models.google_llm import Gemini

# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)

logger = logging.getLogger("ResearchForge")

APP_NAME = os.getenv("APP_NAME", "researchforge")
USER_ID = os.getenv("USER_ID", "researcher")
SESSION_ID = os.getenv("SESSION_ID", "research-session")

# --------------------------------------------------
# API KEYS
# --------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_API_KEY2 = os.getenv("GROQ_API_KEY2", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Configure Gemini environment variable
if GEMINI_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# --------------------------------------------------
# MODEL NAMES
# --------------------------------------------------

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "groq/openai/gpt-oss-20b"
).strip()

GROQ_MODEL2 = os.getenv(
    "GROQ_MODEL2",
    GROQ_MODEL
).strip()

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
).strip()

MAX_PAPERS = int(os.getenv("MAX_PAPERS", "2"))

# --------------------------------------------------
# MODEL CLIENTS
# --------------------------------------------------

# Groq Key 1: Analysis Agent
GROQ_LLM = None

if GROQ_API_KEY:
    GROQ_LLM = LiteLlm(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        include_reasoning=False,
        max_tokens=int(os.getenv("GROQ_MAX_TOKENS", "1536")),
    )

# Groq Key 2: Research Agent
GROQ_LLM2 = None

if GROQ_API_KEY2:
    GROQ_LLM2 = LiteLlm(
        model=GROQ_MODEL2,
        api_key=GROQ_API_KEY2,
        include_reasoning=False,
        max_tokens=int(os.getenv("GROQ_MAX_TOKENS2", "1536")),
    )

# Gemini: Report and Reviewer Agents
GEMINI_LLM = None

if GEMINI_API_KEY:
    GEMINI_LLM = Gemini(
        model=GEMINI_MODEL,
    )

# --------------------------------------------------
# CENTRALIZED AGENT MODEL ALLOCATION
# --------------------------------------------------

AGENT_MODEL_MAP = {
    "research": GROQ_LLM2,
    "analysis": GROQ_LLM,
    "report": GEMINI_LLM,
    "reviewer": GEMINI_LLM,
}

AGENT_ALLOCATION_INFO = {
    "research": ("Groq", GROQ_MODEL2, "Groq Key 2"),
    "analysis": ("Groq", GROQ_MODEL, "Groq Key 1"),
    "report": ("Gemini", GEMINI_MODEL, "Gemini API"),
    "reviewer": ("Gemini", GEMINI_MODEL, "Gemini API"),
}

# --------------------------------------------------
# GET MODEL FOR AGENT
# --------------------------------------------------

def get_model_for_agent(agent_name: str):

    if agent_name not in AGENT_MODEL_MAP:
        raise ValueError(f"Unknown agent: {agent_name}")

    model = AGENT_MODEL_MAP[agent_name]

    if model is None:
        raise RuntimeError(
            f"Model for agent '{agent_name}' is not configured. "
            "Check the required API key in your .env file."
        )

    provider, model_name, credential = AGENT_ALLOCATION_INFO[agent_name]

    logger.info(
        "Agent: %s | Provider: %s | Model: %s | Credential: %s",
        agent_name,
        provider,
        model_name,
        credential,
    )

    return model

# --------------------------------------------------
# PRINT MODEL ALLOCATION
# --------------------------------------------------

def print_model_allocation():

    print("\nResearchForge Model Allocation")
    print("-" * 55)

    for agent_name, model in AGENT_MODEL_MAP.items():

        provider, model_name, credential = AGENT_ALLOCATION_INFO[agent_name]

        status = "CONFIGURED" if model is not None else "MISSING"

        print(
            f"{agent_name.capitalize():10} : "
            f"{provider:6} | {model_name} | {credential} | {status}"
        )

    print("-" * 55)

# --------------------------------------------------
# INSPECT ACTUAL AGENT MODEL OBJECTS
# --------------------------------------------------

def inspect_agent_models():

    from researchforge.agent import root_agent

    print("\nACTUAL AGENT MODEL OBJECTS")
    print("-" * 60)

    for agent in root_agent.sub_agents:

        model = agent.model

        print(f"\nAgent: {agent.name}")
        print(f"Model class: {type(model).__name__}")
        print(f"Model name: {getattr(model, 'model', 'Unknown')}")

        # Verify which configured object was assigned.
        if model is GROQ_LLM2:
            print("Assigned credential: Groq Key 2")

        elif model is GROQ_LLM:
            print("Assigned credential: Groq Key 1")

        elif model is GEMINI_LLM:
            print("Assigned credential: Gemini API")

        else:
            print("Assigned credential: Unknown model object")

    print("-" * 60)

# --------------------------------------------------
# SECONDARY GROQ CLIENT
# --------------------------------------------------

def get_groq_fallback_model():

    if GROQ_LLM2 is None:
        raise RuntimeError("GROQ_API_KEY2 is not configured")

    return GROQ_LLM2

# --------------------------------------------------
# CONFIGURATION VALIDATION
# --------------------------------------------------

def validate_config():

    required_keys = {
        "GROQ_API_KEY": GROQ_API_KEY,
        "GROQ_API_KEY2": GROQ_API_KEY2,
        "GEMINI_API_KEY": GEMINI_API_KEY,
    }

    for key_name, key_value in required_keys.items():

        if not key_value:
            raise RuntimeError(
                f"{key_name} is missing in .env"
            )

    if not GROQ_MODEL:
        raise RuntimeError("GROQ_MODEL cannot be empty")

    if not GROQ_MODEL2:
        raise RuntimeError("GROQ_MODEL2 cannot be empty")

    if not GEMINI_MODEL:
        raise RuntimeError("GEMINI_MODEL cannot be empty")

    if MAX_PAPERS < 1:
        raise RuntimeError("MAX_PAPERS must be at least 1")

    logger.info("Configuration validation successful.")
