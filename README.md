# ✉️ AI Email Reply Agent — Complete Project Reference

All files in one place. Copy-paste each section into the correct file.

---

## 📁 File 1 — requirements.txt

```
crewai
crewai-tools
openai
langchain
langchain-openai
langchain-community
langchain-core
chromadb
sentence-transformers
transformers
torch
ddgs
python-dotenv
streamlit
```

---

## 📁 File 2 — .env

```
OPENAI_API_KEY=your_actual_openai_key_here
```

---

## 📁 File 3 — .gitignore

```
# Never upload the API key
.env

# Never upload the virtual environment
venv/

# Python cache files
__pycache__/
*.pyc
*.pyo

# Chroma database files
chroma_db/

# VS Code settings
.vscode/

# Windows system files
Thumbs.db
desktop.ini
```

---

## 📁 File 4 — tools.py

```python
# tools.py
# ============================================================
# This file contains all 3 AI tools our agents will use:
#   1. Sentiment Analysis  — detects email tone
#   2. Web Search          — fetches live information
#   3. RAG Pipeline        — searches company documents
# ============================================================

import os
from dotenv import load_dotenv
from transformers import pipeline
from crewai.tools import BaseTool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from ddgs import DDGS

# Load the API key from your .env file
load_dotenv()

# ============================================================
# TOOL 1 — Sentiment Analysis
# Uses a free HuggingFace model, runs on your computer
# No extra API key needed
# ============================================================

print("Loading sentiment model... (first time takes ~30 seconds)")

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    truncation=True,
    max_length=512
)

print("Sentiment model ready!")


class SentimentAnalysisTool(BaseTool):
    name: str = "Sentiment Analysis Tool"
    description: str = (
        "Analyzes the emotional tone of an email. "
        "Returns POSITIVE or NEGATIVE sentiment with a confidence "
        "score and a recommended response strategy."
    )

    def _run(self, email_text: str) -> str:
        result = sentiment_pipeline(email_text[:512])[0]
        label = result["label"]
        score = result["score"]
        confidence = round(score * 100, 1)

        if label == "NEGATIVE" and score > 0.85:
            strategy = (
                "ESCALATION RECOMMENDED — tone is strongly negative. "
                "Use an empathetic, apologetic opening. "
                "Offer concrete next steps and resolution."
            )
        elif label == "NEGATIVE":
            strategy = (
                "HANDLE WITH CARE — tone is mildly negative. "
                "Acknowledge concern early. Keep reply warm and solution-focused."
            )
        elif label == "POSITIVE" and score > 0.85:
            strategy = (
                "POSITIVE TONE — reply can be friendly and upbeat. "
                "Match their enthusiasm."
            )
        else:
            strategy = (
                "NEUTRAL TONE — keep reply professional and clear."
            )

        return (
            f"Sentiment   : {label}\n"
            f"Confidence  : {confidence}%\n"
            f"Strategy    : {strategy}"
        )


# ============================================================
# TOOL 2 — Web Search
# Uses DuckDuckGo — completely free, no API key needed
# ============================================================

class WebSearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = (
        "Searches the web for current, relevant information "
        "related to the topic of an email. Use this when you need "
        "up-to-date facts or best practices to craft a better reply."
    )

    def _run(self, query: str) -> str:
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=4):
                    results.append(r)

            if not results:
                return "No web results found for this query."

            formatted = []
            for i, r in enumerate(results, 1):
                formatted.append(
                    f"Result {i}:\n"
                    f"  Title  : {r.get('title', 'N/A')}\n"
                    f"  Source : {r.get('href', 'N/A')}\n"
                    f"  Summary: {r.get('body', 'N/A')}\n"
                )
            return "\n".join(formatted)

        except Exception as e:
            return f"Web search failed: {str(e)}"


# ============================================================
# TOOL 3 — RAG Pipeline
# Stores company documents as vectors for smart retrieval
# ============================================================

company_documents = [
    Document(
        page_content="""
        SHIPPING POLICY — Last updated January 2025
        Standard delivery takes 5-7 business days.
        Express delivery takes 1-2 business days and costs $15 extra.
        International shipping takes 10-14 business days.
        If an order is delayed beyond the estimated date, customers are
        entitled to a $10 store credit applied automatically to their account.
        For delays exceeding 14 days, customers may request a full refund.
        Contact support@shopexample.com for all shipping inquiries.
        """,
        metadata={"source": "shipping_policy.pdf"}
    ),
    Document(
        page_content="""
        REFUND & RETURNS POLICY — Last updated March 2025
        Customers may return any item within 30 days of delivery.
        Items must be unused and in original packaging.
        Refunds are processed within 5-7 business days of receiving the return.
        Digital products and gift cards are non-refundable.
        To initiate a return, email returns@shopexample.com.
        Shipping costs for returns are covered by the company if the item
        arrived damaged or defective.
        """,
        metadata={"source": "refund_policy.pdf"}
    ),
    Document(
        page_content="""
        CUSTOMER SERVICE GUIDELINES — Internal Document
        Always greet the customer by name if known.
        Acknowledge the customer's frustration before offering solutions.
        Never make promises about timelines you cannot guarantee.
        For angry customers: listen first, apologise second, solve third.
        Escalate to a senior agent if the customer has contacted us more than
        3 times about the same issue, or if the order value exceeds $500.
        Always close an email by offering a direct contact point.
        Response time target: within 24 hours on business days.
        """,
        metadata={"source": "cs_guidelines.pdf"}
    ),
    Document(
        page_content="""
        PRODUCT WARRANTY INFORMATION
        All electronics come with a 12-month manufacturer warranty.
        Clothing and accessories have a 90-day quality guarantee.
        Warranty claims must include proof of purchase.
        Warranty replacements are shipped within 3-5 business days.
        For warranty claims email warranty@shopexample.com with your
        order number and a description of the defect.
        """,
        metadata={"source": "warranty_info.pdf"}
    ),
    Document(
        page_content="""
        FREQUENTLY ASKED QUESTIONS
        Q: Where is my order?
        A: Log into your account and visit Order History for live tracking.
        Q: My item arrived damaged. What do I do?
        A: Email support@shopexample.com with photos within 48 hours.
        We will arrange a free replacement or full refund.
        Q: Do you offer price matching?
        A: Yes, within 7 days of purchase if you find a lower price at a
        major retailer. Send us a link to the lower price.
        """,
        metadata={"source": "faq.pdf"}
    ),
]

print("Building knowledge base...")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.environ["OPENAI_API_KEY"]
)

vectorstore = Chroma.from_documents(
    documents=company_documents,
    embedding=embeddings,
    collection_name="company_knowledge_base"
)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 2}
)

print("Knowledge base ready!")


class RAGTool(BaseTool):
    name: str = "Company Knowledge Base Tool"
    description: str = (
        "Retrieves relevant information from the company's internal "
        "knowledge base including shipping policies, refund policies, "
        "warranty information, customer service guidelines, and FAQs. "
        "Use this to ground email responses in accurate company policy."
    )

    def _run(self, query: str) -> str:
        docs = retriever.invoke(query)
        if not docs:
            return "No relevant documents found in the knowledge base."

        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            formatted.append(
                f"Document {i} (from {source}):\n{doc.page_content.strip()}"
            )
        return "\n\n---\n\n".join(formatted)


# ============================================================
# Create one instance of each tool
# These get imported by agents.py and app.py
# ============================================================

sentiment_tool = SentimentAnalysisTool()
web_search_tool = WebSearchTool()
rag_tool        = RAGTool()

print("All 3 tools are ready!")
```

---

## 📁 File 5 — agents.py

```python
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
                  SENTIMENT SUMMARY
                  KEY CUSTOMER ISSUE
                  RELEVANT COMPANY POLICY
                  EXTERNAL BEST PRACTICES
                  RECOMMENDED RESPONSE STRATEGY
                  ESCALATION NEEDED? (yes or no and why)
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
        ESCALATION FLAG: This email has been flagged for senior review.
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
# This is what app.py calls when the button is clicked
# Returns the final email, sentiment, confidence, and escalation flag
# ============================================================

def run_email_agent(incoming_email: str) -> dict:
    """
    Runs the full CrewAI pipeline on an incoming email.
    Returns a dictionary with reply, sentiment, confidence, escalation.
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

    # Step 4 — run in a separate thread to avoid async event loop conflicts
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
```

---

## 📁 File 6 — app.py

```python
# app.py
# ============================================================
# This is the Streamlit web interface
# Warm Sand theme — creamy white + amber orange
# Run it with: streamlit run app.py
# ============================================================

import streamlit as st
from agents import run_email_agent

# ============================================================
# PAGE CONFIGURATION
# Must be the very first Streamlit command
# ============================================================

st.set_page_config(
    page_title="MailAgent AI",
    page_icon="✉️",
    layout="wide"
)

# ============================================================
# CUSTOM CSS — Warm Sand Theme
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #fffbf0;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.main .block-container {
    padding: 2rem 3rem;
    max-width: 1100px;
}

.app-header {
    background: linear-gradient(135deg, #d97706, #dc2626);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    color: white;
}
.app-header h1 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 6px 0;
    color: white;
}
.app-header p {
    font-size: 0.95rem;
    opacity: 0.88;
    margin: 0 0 1rem 0;
    color: white;
}
.badge-row { display: flex; gap: 10px; flex-wrap: wrap; }
.badge {
    background: rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.78rem;
    font-weight: 600;
    color: white;
}

.sand-card {
    background: white;
    border: 1px solid #fde68a;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
}

.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #b45309;
    margin-bottom: 0.6rem;
}

textarea {
    background: #fffbf0 !important;
    border: 1px solid #fde68a !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    color: #1c1917 !important;
}
textarea:focus {
    border-color: #d97706 !important;
    box-shadow: 0 0 0 3px rgba(217,119,6,0.15) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #d97706, #dc2626) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    width: 100% !important;
}

.metric-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 1.2rem;
}
.metric-card {
    background: #fffbf0;
    border: 1px solid #fde68a;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.metric-value { font-size: 1.4rem; font-weight: 700; margin-bottom: 4px; }
.metric-label {
    font-size: 0.72rem;
    color: #92400e;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.step-row {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #fffbf0;
    border: 1px solid #fde68a;
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 0.85rem;
    color: #1c1917;
}
.step-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #d97706;
    flex-shrink: 0;
}

.escalation-banner {
    background: #fef3c7;
    border: 1px solid #fcd34d;
    border-left: 4px solid #d97706;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 0.88rem;
    font-weight: 600;
    color: #78350f;
    margin-bottom: 1rem;
}

[data-testid="stSidebar"] {
    background: white;
    border-right: 1px solid #fde68a;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SAMPLE EMAILS
# ============================================================

SAMPLE_EMAILS = {
    "😡 Angry customer": """Subject: Completely unacceptable - Order #45821 still not arrived

To Whom It May Concern,

I placed an order on your website 3 weeks ago and my package still has not arrived. I have tried tracking it but the tracking page just says in transit with no updates for 10 days.

I have emailed your support team twice already and received no response. This is absolutely unacceptable. I paid $89 for this order and I expect either my package or a full refund immediately.

If I do not hear back within 24 hours I will be disputing the charge with my credit card company.

Extremely frustrated,
James""",

    "😊 Happy customer": """Subject: Love your products!

Hi there,

I just received my order #67234 and I absolutely love everything! The packaging was beautiful and everything arrived in perfect condition.

I was wondering if you offer a loyalty program or any discounts for returning customers? I am already planning my next purchase!

Also one of the items has a small defect — a loose thread on the sleeve. Nothing major but wanted to let you know.

Thanks so much, you have got a customer for life!

Best,
Maria""",

    "📦 Damaged item": """Subject: Item arrived broken - Order #91042

Hello,

I received my order #91042 yesterday but unfortunately the ceramic vase I ordered arrived completely shattered. The box itself looked fine on the outside but the item inside was in pieces.

I paid $45 for this item and would like either a replacement or a full refund. I have taken photos of the damage.

Please let me know how to proceed.

Thank you,
David""",

    "💰 Refund request": """Subject: Requesting refund for order #33019

Hi,

I ordered a jacket two weeks ago (order #33019) but when it arrived it was the wrong size — I ordered a Large but received a Small.

I would like to return it and get a full refund. I have not worn it and it is still in the original packaging with all tags attached.

Could you please send me the return instructions?

Regards,
Emma"""
}

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 1.5rem'>
        <div style='font-size:2.5rem'>✉️</div>
        <div style='font-size:1.1rem; font-weight:700; color:#78350f'>MailAgent AI</div>
        <div style='font-size:0.75rem; color:#b45309; margin-top:4px'>CrewAI · GPT-4o-mini</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🧪 Try a sample")
    st.markdown("Click any sample to auto-fill the email box:")

    for label in SAMPLE_EMAILS:
        if st.button(label, key=f"sample_{label}"):
            st.session_state["email_input"] = SAMPLE_EMAILS[label]

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.78rem; color:#92400e; line-height:1.8'>
        <strong>🛠 Tools active</strong><br>
        🎭 Sentiment analysis<br>
        📚 RAG knowledge base<br>
        🔍 Web search<br><br>
        <strong>⚡ Escalation logic</strong><br>
        Auto-flags strongly negative emails for senior review
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if "total_processed" not in st.session_state:
        st.session_state["total_processed"] = 0
    if "total_escalations" not in st.session_state:
        st.session_state["total_escalations"] = 0

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Processed", st.session_state["total_processed"])
    with col2:
        st.metric("Escalations", st.session_state["total_escalations"])

# ============================================================
# MAIN PAGE HEADER
# ============================================================

st.markdown("""
<div class="app-header">
    <h1>✉️ AI Email Reply Agent</h1>
    <p>Paste any customer email and get a professional, policy-grounded reply in seconds</p>
    <div class="badge-row">
        <span class="badge">🎭 Sentiment-aware</span>
        <span class="badge">📚 Policy-grounded</span>
        <span class="badge">🔍 Web-enhanced</span>
        <span class="badge">⚠️ Auto-escalation</span>
        <span class="badge">🤖 Powered by CrewAI</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# TWO COLUMN LAYOUT
# ============================================================

left_col, right_col = st.columns([1, 1], gap="large")

# ---- LEFT COLUMN ----
with left_col:
    st.markdown('<div class="sand-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📨 Customer email</div>', unsafe_allow_html=True)

    email_input = st.text_area(
        label="",
        placeholder="Paste the customer email here...",
        height=280,
        key="email_input"
    )

    generate = st.button("⚡ Generate AI Reply", key="generate_btn")
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("ℹ️ How does this work?"):
        st.markdown("""
        **Step 1 — Sentiment analysis**
        A local AI model reads the email and detects whether the tone
        is positive or negative, with a confidence score.

        **Step 2 — Knowledge base search (RAG)**
        The agent searches the company's internal documents —
        shipping policies, refund rules, FAQs — and retrieves
        the most relevant policy for this email.

        **Step 3 — Web search**
        The agent searches the web for current best practices
        on handling this type of customer issue.

        **Step 4 — Email generation**
        A writer agent combines all three sources and crafts
        a professional, tone-matched reply — with an escalation
        flag if the email is strongly negative.
        """)

# ---- RIGHT COLUMN ----
with right_col:

    if generate and email_input.strip():
        with st.spinner("🤖 Agents are working... (30-60 seconds)"):
            try:
                result = run_email_agent(email_input)
                st.session_state["result"] = result
                st.session_state["total_processed"] += 1
                if result["escalation"]:
                    st.session_state["total_escalations"] += 1
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")

    elif generate and not email_input.strip():
        st.warning("⚠️ Please paste a customer email first!")

    if "result" in st.session_state:
        result = st.session_state["result"]
        sentiment = result["sentiment"]
        confidence = result["confidence"]
        sentiment_color = "#dc2626" if sentiment == "NEGATIVE" else "#059669"

        st.markdown(f"""
        <div class="sand-card">
            <div class="section-label">📊 Analysis results</div>
            <div class="metric-row">
                <div class="metric-card">
                    <div class="metric-value" style="color:{sentiment_color}">{sentiment}</div>
                    <div class="metric-label">Sentiment</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" style="color:#d97706">{confidence}</div>
                    <div class="metric-label">Confidence</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" style="color:#d97706">3</div>
                    <div class="metric-label">Tools used</div>
                </div>
            </div>
            <div class="section-label">🔧 Pipeline steps</div>
            <div class="step-row">
                <div class="step-dot"></div>
                <span>✅ Sentiment analysis completed</span>
            </div>
            <div class="step-row">
                <div class="step-dot"></div>
                <span>✅ Company knowledge base searched</span>
            </div>
            <div class="step-row">
                <div class="step-dot"></div>
                <span>✅ Web search completed</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sand-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">✉️ Generated reply</div>', unsafe_allow_html=True)

        if result["escalation"]:
            st.markdown("""
            <div class="escalation-banner">
                ⚠️ ESCALATION FLAG — This email has been flagged for senior review
            </div>
            """, unsafe_allow_html=True)

        st.text_area(
            label="",
            value=result["reply"],
            height=300,
            key="reply_display"
        )

        st.download_button(
            label="📥 Download reply as .txt",
            data=result["reply"],
            file_name="email_reply.txt",
            mime="text/plain",
            use_container_width=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size:0.78rem; color:#b45309; text-align:center; margin-top:8px">
            💡 Click inside the reply box → Ctrl+A to select all → Ctrl+C to copy
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="sand-card" style="text-align:center; padding:3rem 1.5rem">
            <div style="font-size:3rem; margin-bottom:1rem">✉️</div>
            <div style="font-size:1rem; font-weight:600; color:#78350f; margin-bottom:8px">
                Ready to generate
            </div>
            <div style="font-size:0.85rem; color:#b45309; line-height:1.7">
                Paste a customer email on the left<br>
                or click a sample in the sidebar<br>
                then hit Generate AI Reply
            </div>
        </div>
        """, unsafe_allow_html=True)
```

---

## 📁 File 7 — README.md

```markdown
# ✉️ AI Email Reply Agent

An intelligent email generation system built with **CrewAI**, **GPT-4o-mini**, and three specialized AI tools — sentiment analysis, RAG pipeline, and web search. The agent reads incoming customer emails, analyses their tone, retrieves relevant company policies, searches the web for best practices, and generates professional replies automatically.

---

## 📸 Screenshots

### Input and Analysis
![Input and analysis results](assets/screenshot_1.png)
*Paste any customer email on the left — the agent runs sentiment analysis, searches the knowledge base, and fetches web results automatically*

### Generated Reply with Escalation Flag
![Generated reply](assets/screenshot_2.png)
*The writer agent produces a professional reply with an escalation flag for strongly negative emails, grounded in actual company policy*

---

## 🚀 Features

- 🎭 **Sentiment Analysis** — detects positive or negative tone with a confidence score using a local HuggingFace model
- 📚 **RAG Pipeline** — searches company documents stored in a ChromaDB vector database and retrieves the most relevant policy
- 🔍 **Web Search** — fetches real-time best practices using DuckDuckGo
- ⚠️ **Auto Escalation** — strongly negative emails are automatically flagged for senior review
- 🎨 **Beautiful UI** — warm sand themed Streamlit interface with sidebar, metric cards, and pipeline tracker
- 📥 **Download Reply** — save the generated reply as a .txt file

---

## 🧠 How It Works

**Step 1 — Analyst Agent reads the incoming email and runs 3 tools**

- Runs the Sentiment Analysis Tool to detect tone and confidence score
- Runs the RAG Tool to retrieve the most relevant company policy
- Runs the Web Search Tool to find current best practices
- Produces a structured briefing with all findings

**Step 2 — Writer Agent reads the briefing and writes the reply**

- Matches tone to sentiment — empathetic for negative, friendly for positive
- References actual company policy in the reply
- Adds escalation flag automatically if sentiment is strongly negative
- Produces a 150 to 250 word professional reply

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Agent framework | CrewAI |
| Language model | GPT-4o-mini (OpenAI) |
| Sentiment analysis | DistilBERT (HuggingFace Transformers) |
| Vector database | ChromaDB |
| Embeddings | OpenAI text-embedding-3-small |
| Web search | DuckDuckGo Search (ddgs) |
| Web framework | Streamlit |
| Language | Python 3.12 |

---

## 📁 Project Structure

| File | Purpose |
|---|---|
| `.env` | Stores API key securely — never uploaded to GitHub |
| `.gitignore` | Files excluded from Git |
| `requirements.txt` | All project dependencies |
| `tools.py` | The 3 AI tools — sentiment, web search, RAG |
| `agents.py` | CrewAI agents, tasks, and main runner function |
| `app.py` | Streamlit web interface with Warm Sand theme |
| `assets/` | Screenshots and images for README |

---

## ⚙️ Setup and Installation

### Prerequisites

- Python 3.10 or higher
- An OpenAI API key — [get one here](https://platform.openai.com)
- Git

### Step 1 — Clone the repository

```bash
git clone https://github.com/shivaniharane/email-agent-app.git
cd email-agent-app
```

### Step 2 — Create a virtual environment

```bash
python -m venv venv
```

**Windows**
```bash
venv\Scripts\activate
```

**Mac and Linux**
```bash
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Set up your API key

Create a `.env` file in the root folder and add this line:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 5 — Run the app

```bash
streamlit run app.py
```

Then open your browser at `http://localhost:8501`

---

## 💡 Sample Emails Included

| Sample | What it tests |
|---|---|
| 😡 Angry customer | Delayed order, demands refund — triggers escalation flag |
| 😊 Happy customer | Positive feedback with a minor product defect |
| 📦 Damaged item | Broken item on arrival, wants replacement |
| 💰 Refund request | Wrong size delivered, wants return instructions |

---

## 📚 Knowledge Base Documents

| Document | Contents |
|---|---|
| `shipping_policy.pdf` | Delivery times, delay rules, store credit policy |
| `refund_policy.pdf` | Return window, refund processing time |
| `cs_guidelines.pdf` | Internal tone and escalation guidelines |
| `warranty_info.pdf` | Product warranty periods and claim process |
| `faq.pdf` | Common customer questions and answers |

---

## ⚠️ Escalation Logic

An email is automatically flagged for escalation when both conditions are met:

- Sentiment detected is **NEGATIVE**
- Confidence score is **above 85%**

---

## 🔮 Future Improvements

- Add email history tab to track all processed emails in a session
- Support PDF upload so users can add their own company documents
- Add multi-language support for international customers
- Deploy on Streamlit Community Cloud for public access
- Add Gmail and Outlook integration to send replies directly

---

## 🚀 How to Run the App

```bash
cd E:\email_agent_app
venv\Scripts\activate
streamlit run app.py
```

Or double-click `run.bat` if you created it.

---

## 📌 Quick Git Commands

Push changes to GitHub:

```bash
git add .
git commit -m "your message here"
git push
```
