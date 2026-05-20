# ✉️ AI Email Reply Agent

An intelligent email generation system built with **CrewAI**, **GPT-4o-mini**, and three specialized AI tools — sentiment analysis, RAG pipeline, and web search. The agent reads incoming customer emails, analyses their tone, retrieves relevant company policies, searches the web for best practices, and generates professional replies automatically.

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

---

## ⚙️ Setup and Installation

### Prerequisites

- Python 3.10 or higher
- An OpenAI API key — [get one here](https://platform.openai.com)
- Git

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/email-agent-app.git
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
OPENAI_API_KEY=your_openai_api_key_here

### Step 5 — Run the app

```bash
streamlit run app.py
```

Then open your browser at `http://localhost:8501`

---

## 💡 Sample Emails Included

The sidebar includes 4 built-in sample emails to test the app instantly:

| Sample | What it tests |
|---|---|
| 😡 Angry customer | Delayed order, demands refund — triggers escalation flag |
| 😊 Happy customer | Positive feedback with a minor product defect |
| 📦 Damaged item | Broken item on arrival, wants replacement |
| 💰 Refund request | Wrong size delivered, wants return instructions |

---

## 📚 Knowledge Base Documents

The RAG pipeline searches these 5 company documents:

| Document | Contents |
|---|---|
| `shipping_policy.pdf` | Delivery times, delay rules, store credit policy |
| `refund_policy.pdf` | Return window, refund processing time |
| `cs_guidelines.pdf` | Internal tone and escalation guidelines |
| `warranty_info.pdf` | Product warranty periods and claim process |
| `faq.pdf` | Common customer questions and answers |

Documents are converted into vectors using OpenAI embeddings and stored in ChromaDB. When an email arrives the RAG tool finds the 2 most relevant documents and passes them to the analyst agent.

---

## ⚠️ Escalation Logic

An email is automatically flagged for escalation when both conditions are met:

- Sentiment detected is **NEGATIVE**
- Confidence score is **above 85%**

When flagged the generated reply includes this banner at the top:

> ⚠️ ESCALATION FLAG: This email has been flagged for senior review.

---

## 🔮 Future Improvements

- Add email history tab to track all processed emails in a session
- Support PDF upload so users can add their own company documents
- Add multi-language support for international customers
- Deploy on Streamlit Community Cloud for public access
- Add Gmail and Outlook integration to send replies directly

---

## 👤 Author

Built as part of an AI Agents course project demonstrating multi-agent systems, RAG pipelines, sentiment analysis, and tool integration using CrewAI.



