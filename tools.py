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

print("⏳ Loading sentiment model... (first time takes ~30 seconds)")

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    truncation=True,
    max_length=512
)

print("✅ Sentiment model ready!")


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
# Uses DuckDuckGo — free, no API key needed
# ============================================================

class WebSearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = (
        "Searches the web for current, relevant information "
        "related to the topic of an email. Use this to find "
        "best practices and up-to-date context for the reply."
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
# Stores company documents so agents can search them smartly
# ============================================================

# These are the company documents our agents can reference
# In a real project these would be your actual company PDFs
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
        Shipping costs for returns are covered by the company if the
        item arrived damaged or defective.
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
        Escalate to a senior agent if the customer has contacted us more
        than 3 times about the same issue, or if order value exceeds $500.
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
        A: Yes, within 7 days of purchase if you find a lower price
        at a major retailer. Send us a link to the lower price.
        """,
        metadata={"source": "faq.pdf"}
    ),
]

print("⏳ Building knowledge base...")

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

print("✅ Knowledge base ready!")


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

print("✅ All 3 tools are ready!")