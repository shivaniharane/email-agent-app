# agents.py
# ============================================================
# This file contains:
#   - 2 CrewAI agents (Analyst + Writer)
#   - 2 Tasks (Analyse + Write)
#   - 1 function that runs the full pipeline
# ============================================================

import asyncio
import threading
from crewai import Agent, Task, Crew, Process
from tools import sentiment_tool, web_search_tool, rag_tool

# ============================================================
# AGENT 1 — Email Analyst
# This agent reads the email and runs all 3 tools
# It produces a structured briefing for the writer
# ============================================================

analyst_agent = Agent(
    role="Senior Email Analyst",
    goal=(
        "Thoroughly analyse an incoming customer email by detecting its "
        "sentiment, retrieving relevant company policies from the knowledge "
        "base, and gathering external context via web search. "
        "Produce a clear structured briefing for the writer agent."
    ),
    backstory=(
        "You are a senior customer service analyst with 10 years of "
        "experience handling customer communications for an e-commerce "
        "company. You always ground your analysis in actual company policy "
        "rather than guesswork."
    ),
    tools=[sentiment_tool, rag_tool, web_search_tool],
    llm="gpt-4o-mini",
    verbose=True,
    allow_delegation=False,
    max_iter=4
)

# ============================================================
# AGENT 2 — Email Writer
# This agent reads the analyst's briefing and writes the reply
# It does not use any tools — just writes
# ============================================================

writer_agent = Agent(
    role="Professional Email Writer",
    goal=(
        "Write a polished, empathetic, and effective email reply "
        "based on the analyst briefing. Match tone to sentiment — "
        "empathetic for negative emails, friendly for positive ones. "
        "Always include concrete next steps."
    ),
    backstory=(
        "You are an expert business writer specialising in customer "
        "communications. Your emails are clear, warm, and professional. "
        "Every email you write makes the customer feel heard and leaves "
        "them knowing exactly what happens next."
    ),
    tools=[],
    llm="gpt-4o-mini",
    verbose=True,
    allow_delegation=False,
    max_iter=2
)


# ============================================================
# TASK FACTORIES
# We use functions so we can create fresh tasks for each email
# ============================================================

def create_analysis_task(incoming_email: str) -> Task:
    return Task(
        description=f"""
        Analyse the following customer email step by step:

        ---
        {incoming_email}
        ---

        You MUST complete ALL of these steps:

        Step 1 — Run the Sentiment Analysis Tool on the email text.
                  Note the sentiment, confidence score, and strategy.

        Step 2 — Run the Company Knowledge Base Tool with a query
                  relevant to the customer's issue.

        Step 3 — Run the Web Search Tool for best practices on
                  handling this type of customer issue.

        Step 4 — Write a structured briefing with these 6 sections:
                  • SENTIMENT SUMMARY
                  • KEY CUSTOMER ISSUE
                  • RELEVANT COMPANY POLICY
                  • EXTERNAL BEST PRACTICES
                  • RECOMMENDED RESPONSE STRATEGY
                  • ESCALATION NEEDED? (yes or no and why)
        """,
        expected_output=(
            "A structured briefing document with all 6 sections "
            "filled out based on actual tool results."
        ),
        agent=analyst_agent
    )


def create_writing_task(analysis_task: Task) -> Task:
    return Task(
        description="""
        Using the structured briefing from the analyst agent,
        write a complete professional email reply to the customer.

        The email MUST:
        - Start with a subject line
        - Address the customer warmly
        - Acknowledge their specific issue in the opening paragraph
        - Reference the actual company policy that applies
        - Offer at least one concrete next step or resolution
        - Match the tone to the sentiment
        - Close with: Sarah Chen, Customer Support
        - Be between 150 and 250 words

        If escalation is recommended in the briefing, add this
        at the very top of the email:
        ⚠️ ESCALATION FLAG: This email has been flagged for senior review.
        """,
        expected_output=(
            "A complete ready-to-send email reply with subject line, "
            "greeting, body paragraphs, and sign-off."
        ),
        agent=writer_agent,
        context=[analysis_task]
    )


# ============================================================
# MAIN RUNNER FUNCTION
# This is what app.py will call when the button is clicked
# Returns 3 things: the final email, sentiment, and escalation flag
# ============================================================

def run_email_agent(incoming_email: str) -> dict:
    """
    Runs the full CrewAI pipeline on an incoming email.

    Returns a dictionary with:
      - reply      : the final email text
      - sentiment  : POSITIVE or NEGATIVE
      - confidence : confidence score as a percentage string
      - escalation : True or False
    """

    # Step 1 — run sentiment separately so we can show it in the UI
    from tools import sentiment_pipeline
    raw = sentiment_pipeline(incoming_email[:512])[0]
    sentiment_label = raw["label"]
    confidence      = f"{round(raw['score'] * 100, 1)}%"
    escalation      = sentiment_label == "NEGATIVE" and raw["score"] > 0.85

    # Step 2 — create fresh tasks for this email
    analysis_task = create_analysis_task(incoming_email)
    writing_task  = create_writing_task(analysis_task)

    # Step 3 — assemble the crew
    crew = Crew(
        agents=[analyst_agent, writer_agent],
        tasks=[analysis_task, writing_task],
        process=Process.sequential,
        verbose=True
    )

    # Step 4 — run in a separate thread to avoid Colab/Streamlit
    #           async event loop conflicts
    result_container = {}

    def run_in_thread():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result_container["output"] = crew.kickoff()
        except Exception as e:
            result_container["error"] = str(e)
        finally:
            loop.close()

    thread = threading.Thread(target=run_in_thread)
    thread.start()
    thread.join()

    if "error" in result_container:
        raise Exception(result_container["error"])

    return {
        "reply"      : str(result_container["output"]),
        "sentiment"  : sentiment_label,
        "confidence" : confidence,
        "escalation" : escalation
    }