# app.py
# ============================================================
# This is the Streamlit web interface
# It uses the Warm Sand theme — creamy white + amber orange
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
# This overrides Streamlit's default boring styling
# ============================================================

st.markdown("""
<style>
/* ---- Google Font ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ---- Base ---- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #fffbf0;
}

/* ---- Hide Streamlit default header & footer ---- */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ---- Main container ---- */
.main .block-container {
    padding: 2rem 3rem;
    max-width: 1100px;
}

/* ---- App header ---- */
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
.badge-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}
.badge {
    background: rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.78rem;
    font-weight: 600;
    color: white;
}

/* ---- Section cards ---- */
.sand-card {
    background: white;
    border: 1px solid #fde68a;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
}

/* ---- Section label ---- */
.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #b45309;
    margin-bottom: 0.6rem;
}

/* ---- Sample email chips ---- */
.chip-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}
.chip {
    background: #fef3c7;
    border: 1px solid #fcd34d;
    color: #78350f;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
}

/* ---- Textarea ---- */
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

/* ---- Generate button ---- */
.stButton > button {
    background: linear-gradient(135deg, #d97706, #dc2626) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
}

/* ---- Metric cards ---- */
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
.metric-value {
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 4px;
}
.metric-label {
    font-size: 0.72rem;
    color: #92400e;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ---- Pipeline steps ---- */
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
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #d97706;
    flex-shrink: 0;
}

/* ---- Escalation banner ---- */
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

/* ---- Reply box ---- */
.reply-box {
    background: #fffbf0;
    border: 1px solid #fde68a;
    border-left: 4px solid #d97706;
    border-radius: 0 12px 12px 0;
    padding: 1.2rem 1.4rem;
    font-size: 0.9rem;
    line-height: 1.8;
    color: #1c1917;
    white-space: pre-wrap;
}

/* ---- Copy button ---- */
.copy-btn > button {
    background: white !important;
    color: #b45309 !important;
    border: 1px solid #fde68a !important;
    border-radius: 10px !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
}
.copy-btn > button:hover {
    background: #fef3c7 !important;
}

/* ---- Spinner color ---- */
.stSpinner > div {
    border-top-color: #d97706 !important;
}

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: white;
    border-right: 1px solid #fde68a;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SAMPLE EMAILS
# These appear as quick-fill buttons in the sidebar
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
        <div style='font-size:0.75rem; color:#b45309; margin-top:4px'>
            CrewAI · GPT-4o-mini
        </div>
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

    # Session stats
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
# Left: email input   Right: results
# ============================================================

left_col, right_col = st.columns([1, 1], gap="large")

# ---- LEFT COLUMN — Email Input ----
with left_col:
    st.markdown('<div class="sand-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📨 Customer email</div>',
                unsafe_allow_html=True)

    # Text area — pre-fills when sample button is clicked
    email_input = st.text_area(
        label="",
        placeholder="Paste the customer email here...",
        height=280,
        key="email_input"
    )

    # Generate button
    generate = st.button("⚡ Generate AI Reply", key="generate_btn")
    st.markdown('</div>', unsafe_allow_html=True)

    # How it works expander
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

# ---- RIGHT COLUMN — Results ----
with right_col:

    # Store result in session_state so it persists across reruns
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

    # Show results if we have them in session
    if "result" in st.session_state:
        result = st.session_state["result"]
        sentiment = result["sentiment"]
        confidence = result["confidence"]
        sentiment_color = "#dc2626" if sentiment == "NEGATIVE" else "#059669"

        # ---- Metric cards ----
        st.markdown(f"""
        <div class="sand-card">
            <div class="section-label">📊 Analysis results</div>
            <div class="metric-row">
                <div class="metric-card">
                    <div class="metric-value" style="color:{sentiment_color}">
                        {sentiment}
                    </div>
                    <div class="metric-label">Sentiment</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" style="color:#d97706">
                        {confidence}
                    </div>
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

        # ---- Reply section ----
        st.markdown('<div class="sand-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">✉️ Generated reply</div>',
                    unsafe_allow_html=True)

        # Escalation banner
        if result["escalation"]:
            st.markdown("""
            <div class="escalation-banner">
                ⚠️ ESCALATION FLAG — This email has been flagged for senior review
            </div>
            """, unsafe_allow_html=True)

        # Reply displayed in a styled text area
        # This lets users click inside and use Ctrl+A, Ctrl+C
        st.text_area(
            label="",
            value=result["reply"],
            height=300,
            key="reply_display"
        )

        # Download button — native Streamlit, works perfectly
        st.download_button(
            label="📥 Download reply as .txt",
            data=result["reply"],
            file_name="email_reply.txt",
            mime="text/plain",
            use_container_width=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

        # Helpful tip
        st.markdown("""
        <div style="font-size:0.78rem; color:#b45309; text-align:center;
                    margin-top:8px">
            💡 Click inside the reply box → Ctrl+A to select all → Ctrl+C to copy
        </div>
        """, unsafe_allow_html=True)

    else:
        # Placeholder shown before any email is processed
        st.markdown("""
        <div class="sand-card" style="text-align:center; padding:3rem 1.5rem">
            <div style="font-size:3rem; margin-bottom:1rem">✉️</div>
            <div style="font-size:1rem; font-weight:600;
                        color:#78350f; margin-bottom:8px">
                Ready to generate
            </div>
            <div style="font-size:0.85rem; color:#b45309; line-height:1.7">
                Paste a customer email on the left<br>
                or click a sample in the sidebar<br>
                then hit Generate AI Reply
            </div>
        </div>
        """, unsafe_allow_html=True)