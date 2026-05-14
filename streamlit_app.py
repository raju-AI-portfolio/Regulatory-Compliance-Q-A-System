import re
import html
import time
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Clarionyx",
    layout="wide",
)

# ---------- Helpers ----------
def remove_inline_citations(answer_text: str) -> str:
    if not answer_text:
        return ""
    text = str(answer_text).strip()
    text = re.sub(r"\n\s*Citations\s*:\s*.*$", "", text, flags=re.IGNORECASE | re.DOTALL)
    return text.strip()


def format_gdpr_citation(meta: dict) -> str | None:
    if not isinstance(meta, dict):
        return None

    article_number = str(meta.get("article_number", "")).strip()
    section_number = str(meta.get("section_number", "")).strip()
    page_number = meta.get("page_number")

    if article_number:
        if article_number.lower().startswith("art"):
            normalized_article = article_number
        else:
            normalized_article = f"Art. {article_number}"

        if section_number:
            return f"GDPR {normalized_article}({section_number})"
        return f"GDPR {normalized_article}"

    if page_number:
        return f"GDPR p.{page_number}"

    raw_citation = str(meta.get("citation", "")).strip()
    return raw_citation or None


def collect_citations(data: dict) -> list[str]:
    regulations = [
        str(r).strip().upper()
        for r in data.get("regulations", [])
        if str(r).strip()
    ]

    citations_by_framework: dict[str, list[str]] = {}
    all_citations: list[str] = []

    if isinstance(data.get("retrieved_chunks"), list):
        for chunk in data["retrieved_chunks"]:
            if not isinstance(chunk, dict):
                continue

            meta = chunk.get("metadata", {}) if isinstance(chunk.get("metadata"), dict) else {}
            regulation = str(meta.get("regulation") or chunk.get("regulation") or "").strip().upper()

            citation = None

            if regulation == "GDPR":
                citation = format_gdpr_citation(meta)
            else:
                raw_citation = str(meta.get("citation", "")).strip()
                page_number = meta.get("page_number")

                if raw_citation:
                    citation = raw_citation
                elif page_number and regulation:
                    citation = f"{regulation} p.{page_number}"
                elif page_number:
                    citation = f"p.{page_number}"

            if citation:
                citations_by_framework.setdefault(regulation or "OTHER", [])
                if citation not in citations_by_framework[regulation or "OTHER"]:
                    citations_by_framework[regulation or "OTHER"].append(citation)

                if citation not in all_citations:
                    all_citations.append(citation)

    if not all_citations and isinstance(data.get("citations"), list):
        for c in data["citations"]:
            citation = str(c).strip()
            if citation and citation not in all_citations:
                all_citations.append(citation)

    if not all_citations and isinstance(data.get("citations"), str):
        for c in data.get("citations", "").split(","):
            citation = str(c).strip()
            if citation and citation not in all_citations:
                all_citations.append(citation)

    if len(regulations) <= 1:
        return all_citations[:5]

    balanced_citations: list[str] = []

    for regulation in regulations:
        for citation in citations_by_framework.get(regulation, []):
            if citation not in balanced_citations:
                balanced_citations.append(citation)
                break

    for regulation in regulations:
        for citation in citations_by_framework.get(regulation, [])[1:]:
            if citation not in balanced_citations:
                balanced_citations.append(citation)
                if len(balanced_citations) >= 5:
                    return balanced_citations[:5]
                break

    for citation in all_citations:
        if citation not in balanced_citations:
            balanced_citations.append(citation)
        if len(balanced_citations) >= 5:
            break

    return balanced_citations[:5]


def render_kpi_card(label: str, value: str):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{html.escape(label)}</div>
            <div class="kpi-value">{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_citation_chips(citations: list[str]):
    if citations:
        citation_html = "".join(
            [f'<span class="citation-chip">{html.escape(str(c))}</span>' for c in citations]
        )
        st.markdown(
            f"""
            <div class="section-card compact-card">
                <div class="section-heading">Supporting Citations</div>
                <div>{citation_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="section-card compact-card">
                <div class="section-heading">Supporting Citations</div>
                <div class="small-muted">No structured citations were returned for this response.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def format_answer_html(answer_text: str) -> str:
    clean_answer = remove_inline_citations(answer_text)
    paragraphs = clean_answer.split("\n\n")
    formatted_parts = []

    for p in paragraphs:
        p = html.escape(p).replace("\n", "<br>")
        formatted_parts.append(f"<div style='margin-bottom:14px;'>{p}</div>")

    return "".join(formatted_parts)


# ---------- Styling ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1F2937;
    }

    .stApp {
        background: linear-gradient(180deg, #F5F9FF 0%, #FAFCFF 100%);
    }

    .block-container {
        max-width: 1240px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F4C81 0%, #1565A9 55%, #1D7CC2 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.14);
    }

    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] .stTextInput input {
        background: rgba(255, 255, 255, 0.92) !important;
        color: #0F4C81 !important;
        border: 1px solid rgba(255, 255, 255, 0.55) !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"] .stTextInput input::placeholder {
        color: #6B8BAE !important;
        opacity: 1 !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="tab-list"] {
        gap: 5px !important;
        border-bottom: none !important;
        background: rgba(0, 0, 0, 0.28) !important;
        border-radius: 12px !important;
        padding: 5px !important;
        flex-wrap: wrap !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="tab"] {
        color: rgba(255, 255, 255, 0.55) !important;
        font-weight: 600 !important;
        font-size: 0.83rem !important;
        background: transparent !important;
        border-radius: 8px !important;
        padding: 7px 12px !important;
        border: none !important;
        min-height: unset !important;
        height: auto !important;
    }

    section[data-testid="stSidebar"] [aria-selected="true"] {
        color: #FFFFFF !important;
        background: #0F4C81 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35) !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="tab-highlight"],
    section[data-testid="stSidebar"] [data-baseweb="tab-border"] {
        display: none !important;
    }

    .brand-shell {
        background: linear-gradient(135deg, #0F4C81 0%, #1565A9 55%, #1D7CC2 100%);
        border-radius: 22px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(15, 76, 129, 0.18);
        color: white;
    }

    .brand-topline {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 8px;
    }

    .brand-logo {
        width: 52px;
        height: 52px;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.16);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        border: 1px solid rgba(255, 255, 255, 0.22);
    }

    .brand-name {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0;
        color: #FFFFFF;
    }

    .brand-tagline {
        font-size: 1.08rem;
        color: rgba(255, 255, 255, 0.96);
        margin-top: 4px;
        line-height: 1.65;
        font-weight: 600;
    }

    .brand-subbar {
        margin-top: 14px;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .brand-pill {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.14);
        border: 1px solid rgba(255, 255, 255, 0.22);
        color: #FFFFFF;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .section-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 18px rgba(16, 24, 40, 0.05);
    }

    .compact-card {
        padding-top: 16px;
        padding-bottom: 16px;
    }

    .response-card {
        background: #FFFFFF;
        border: 1px solid #D9E4F0;
        border-radius: 18px;
        padding: 22px 24px;
        margin-bottom: 0;
        box-shadow: 0 6px 22px rgba(16, 24, 40, 0.06);
    }

    .reviewed-response-card {
        background: #FFFFFF;
        border: 1px solid #D9E4F0;
        border-radius: 18px;
        padding: 22px 24px;
        margin-bottom: 0;
        box-shadow: 0 6px 22px rgba(16, 24, 40, 0.06);
    }

    .section-heading {
        font-size: 1.28rem;
        font-weight: 800;
        color: #111827;
        margin-bottom: 12px;
    }

    .response-heading {
        font-size: 1.24rem;
        font-weight: 800;
        color: #0F4C81;
        margin-bottom: 12px;
    }

    .response-body {
        font-size: 1.14rem;
        color: #1F2937;
        line-height: 2.0;
        max-height: 420px;
        min-height: 120px;
        overflow-y: auto;
        resize: vertical;
        padding-right: 6px;
    }

    .response-body::-webkit-scrollbar {
        width: 5px;
    }

    .response-body::-webkit-scrollbar-track {
        background: #F1F5F9;
        border-radius: 999px;
    }

    .response-body::-webkit-scrollbar-thumb {
        background: #CBD5E1;
        border-radius: 999px;
    }

    .response-body::-webkit-scrollbar-thumb:hover {
        background: #94A3B8;
    }

    .question-body {
        font-size: 1.12rem;
        color: #111827;
        line-height: 1.8;
    }

    .citation-chip {
        display: inline-block;
        background: #EEF6FF;
        color: #0F4C81;
        border: 1px solid #C7D7EA;
        border-radius: 999px;
        padding: 5px 10px;
        margin: 4px 6px 4px 0;
        font-size: 0.82rem;
        font-weight: 700;
    }

    .request-id-box {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 14px;
        color: #374151;
        font-size: 0.95rem;
    }

    .request-id-inline {
        margin-top: 10px;
        background: #F8FAFC;
        border: 1px solid #D8E3F0;
        border-radius: 12px;
        padding: 12px 14px;
        font-size: 1.12rem;
        font-weight: 700;
        color: #0F4C81;
        word-break: break-all;
        font-family: monospace;
    }

    .governance-success {
        background: #ECFDF3;
        border: 1px solid #ABEFC6;
        color: #05603A;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 14px;
        font-size: 0.98rem;
    }

    .governance-warning {
        background: #FFF8E8;
        border: 1px solid #EACB7A;
        color: #8A5A00;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 14px;
        font-size: 0.98rem;
    }

    .governance-info {
        background: #F2F4F7;
        border: 1px solid #D0D5DD;
        color: #344054;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 14px;
        font-size: 0.98rem;
    }

    .message-box {
        background: #FFF7ED;
        border: 1px solid #FDBA74;
        color: #9A3412;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 14px;
        font-size: 0.98rem;
        font-weight: 600;
    }

    .kpi-card {
        background: linear-gradient(135deg, #0F4C81 0%, #1565A9 100%);
        border: 1px solid #0E5B97;
        border-radius: 16px;
        padding: 14px 16px;
        min-height: 92px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 6px 18px rgba(15, 76, 129, 0.18);
    }

    .kpi-label {
        font-size: 0.72rem;
        color: rgba(255,255,255,0.82);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 1rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.35;
        word-break: break-word;
        margin-top: auto;
    }

    .review-summary-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 18px rgba(16, 24, 40, 0.05);
    }

    .review-row {
        margin-bottom: 8px;
        color: #344054;
        line-height: 1.6;
        font-size: 1rem;
    }

    .small-muted {
        color: #667085;
        font-size: 0.98rem;
        line-height: 1.6;
    }

    .sidebar-card {
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 18px;
        padding: 16px 16px;
        margin-bottom: 14px;
        box-shadow: 0 4px 16px rgba(16, 24, 40, 0.08);
        backdrop-filter: blur(4px);
    }

    .sidebar-title {
        font-size: 0.96rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 8px;
    }

    .sidebar-text {
        font-size: 0.92rem;
        color: rgba(255, 255, 255, 0.92);
        line-height: 1.72;
    }

    .sidebar-list {
        margin: 0;
        padding-left: 18px;
        color: rgba(255, 255, 255, 0.92);
        line-height: 1.8;
        font-size: 0.92rem;
    }

    label, .stSelectbox label, .stTextArea label, .stTextInput label,
    .stSelectbox label p, .stTextArea label p, .stTextInput label p,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stTextInput"] label {
        font-size: 1.28rem !important;
        font-weight: 800 !important;
        color: #0F4C81 !important;
    }

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stTextInput label,
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] label,
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] label p {
        color: #FFFFFF !important;
        font-size: 1rem !important;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 12px !important;
        border: 1px solid #D0D5DD !important;
        background-color: #FFFFFF !important;
        font-size: 1.08rem !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #0F4C81 0%, #1565A9 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.58rem 1rem;
        font-weight: 700;
        min-height: 44px;
        box-shadow: 0 6px 18px rgba(15, 76, 129, 0.2);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #0C3B64 0%, #104E83 100%);
        color: white;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 18px;
        border-bottom: 2px solid #D1D5DB;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: nowrap;
        font-weight: 700;
        font-size: 1.18rem !important;
        color: #374151 !important;
        padding-left: 4px;
        padding-right: 4px;
    }

    .stTabs [aria-selected="true"] {
        color: #0F4C81 !important;
        border-bottom: 3px solid #0F4C81 !important;
    }

    .stExpander {
        border-radius: 16px !important;
    }

    .copy-id-wrap {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 10px;
    }

    .record-id-text {
        flex: 1;
        background: #F8FAFC;
        border: 1px solid #D8E3F0;
        border-radius: 10px;
        padding: 11px 16px;
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F4C81;
        word-break: break-all;
        font-family: monospace;
    }

    .copy-btn {
        flex-shrink: 0;
        background: #0F4C81;
        color: #FFFFFF !important;
        border: none;
        border-radius: 10px;
        padding: 10px 18px;
        font-size: 0.92rem;
        font-weight: 700;
        cursor: pointer;
        transition: background 0.18s, transform 0.12s;
        display: flex;
        align-items: center;
        gap: 6px;
        white-space: nowrap;
    }

    .copy-btn:hover {
        background: #0C3B64;
        transform: translateY(-1px);
    }

    .copy-btn:active {
        transform: translateY(0);
    }

    .copy-btn.copied {
        background: #059669;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

API_URL = "http://127.0.0.1:8000/query"
REVIEW_URL_BASE = "http://127.0.0.1:8000/review-result-record"

if "latest_record_id" not in st.session_state:
    st.session_state.latest_record_id = ""

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:12px; padding:14px 4px 10px 4px; margin-bottom:6px;">
            <div style="
                width:52px; height:52px; border-radius:16px;
                background: rgba(255,255,255,0.18);
                border: 2px solid rgba(255,255,255,0.35);
                display:flex; align-items:center; justify-content:center;
                font-size:1.7rem; flex-shrink:0;
                box-shadow: 0 4px 14px rgba(0,0,0,0.18);">
                🛡️
            </div>
            <div>
                <div style="font-size:1.45rem; font-weight:900; color:#FFFFFF; letter-spacing:-0.02em; line-height:1.1;">Clarionyx</div>
                <div style="font-size:0.76rem; color:rgba(255,255,255,0.75); font-weight:600; margin-top:2px; letter-spacing:0.04em; text-transform:uppercase;">Regulatory Intelligence</div>
            </div>
        </div>
        <hr style="border:none; border-top:1px solid rgba(255,255,255,0.18); margin:0 0 10px 0;">
        """,
        unsafe_allow_html=True,
    )
    user_id = st.text_input("User ID", value="demo_user", key="sidebar_user_id")

    side_tab1, side_tab2, side_tab3, side_tab4 = st.tabs(
        ["About", "User Manual", "Frameworks", "Review Flow"]
    )

    with side_tab1:
        st.markdown(
            """
            <div class="sidebar-card">
                <div class="sidebar-title">About Clarionyx</div>
                <div class="sidebar-text">
                    Clarionyx is an AI-powered regulatory intelligence assistant built for healthcare and life sciences compliance teams.
                    It delivers grounded, citation-backed answers drawn exclusively from approved regulatory sources — including GDPR, HIPAA, and NIST frameworks.
                </div>
            </div>
            <div class="sidebar-card">
                <div class="sidebar-title">Why Clarionyx?</div>
                <ul class="sidebar-list">
                    <li><strong style="color:#fff;">Accurate:</strong> Responses are grounded in verified regulatory documents, not general knowledge.</li>
                    <li><strong style="color:#fff;">Transparent:</strong> Every answer includes citations referencing the exact article, section, or page.</li>
                    <li><strong style="color:#fff;">Governed:</strong> Low-confidence responses are automatically routed for expert human review before being marked final.</li>
                    <li><strong style="color:#fff;">Efficient:</strong> Reduces hours of manual compliance research to seconds.</li>
                </ul>
            </div>
            <div class="sidebar-card">
                <div class="sidebar-title">Who is it for?</div>
                <div class="sidebar-text">
                    Designed for compliance officers, data protection leads, legal teams, and IT security professionals who need fast, defensible answers to regulatory questions.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with side_tab2:
        st.markdown(
            """
            <div class="sidebar-card">
                <div class="sidebar-title">Getting Started</div>
                <ul class="sidebar-list">
                    <li>Enter your User ID in the field above (or leave as <em>demo_user</em>).</li>
                    <li>Select the appropriate regulatory framework from the dropdown, or choose <strong style="color:#fff;">All Frameworks</strong> to search across all approved sources simultaneously.</li>
                    <li>Type your compliance question in plain business language — no need for legal jargon.</li>
                    <li>Click <strong style="color:#fff;">Submit Question</strong> and wait for the AI to process your query.</li>
                </ul>
            </div>
            <div class="sidebar-card">
                <div class="sidebar-title">Reading Results</div>
                <ul class="sidebar-list">
                    <li>Review the <strong style="color:#fff;">AI Response</strong> card for the full answer.</li>
                    <li>Check the <strong style="color:#fff;">Supporting Citations</strong> section to see which articles or pages the answer is based on.</li>
                    <li>The <strong style="color:#fff;">KPI cards</strong> show confidence score, workflow status, applicable frameworks, and execution time at a glance.</li>
                    <li>If <strong style="color:#fff;">Review Required</strong> shows Yes, the response is pending expert validation.</li>
                </ul>
            </div>
            <div class="sidebar-card">
                <div class="sidebar-title">Retrieving Reviewed Responses</div>
                <ul class="sidebar-list">
                    <li>Switch to the <strong style="color:#fff;">Reviewed Responses</strong> tab after submitting a question.</li>
                    <li>The latest Request ID is auto-populated, or paste one manually.</li>
                    <li>Click <strong style="color:#fff;">Retrieve Reviewed Response</strong> to fetch the final reviewer-approved answer.</li>
                    <li>Use the <strong style="color:#fff;">Copy ID</strong> button to share or log your request ID.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with side_tab3:
        st.markdown(
            """
            <div class="sidebar-card">
                <div class="sidebar-title">GDPR</div>
                <div class="sidebar-text">
                    <strong style="color:#fff;">General Data Protection Regulation</strong> — EU Regulation 2016/679.<br>
                    Governs the collection, processing, storage, and transfer of personal data for individuals within the European Union and EEA. Covers lawful bases for processing, data subject rights, controller and processor obligations, breach notification, and cross-border data transfers.
                </div>
            </div>
            <div class="sidebar-card">
                <div class="sidebar-title">HIPAA</div>
                <div class="sidebar-text">
                    <strong style="color:#fff;">Health Insurance Portability and Accountability Act</strong> — US Federal Law (1996).<br>
                    Protects the privacy and security of Protected Health Information (PHI). Encompasses the Privacy Rule, Security Rule, Breach Notification Rule, and Enforcement Rule. Applies to covered entities and their business associates handling health records.
                </div>
            </div>
            <div class="sidebar-card">
                <div class="sidebar-title">NIST</div>
                <div class="sidebar-text">
                    <strong style="color:#fff;">National Institute of Standards and Technology</strong> — Cybersecurity Framework and Special Publications.<br>
                    Provides guidance on risk management, cybersecurity controls, and information security best practices. Commonly referenced frameworks include NIST CSF, SP 800-53 (security controls), and SP 800-171 (protecting controlled unclassified information).
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with side_tab4:
        st.markdown(
            """
            <div class="sidebar-card">
                <div class="sidebar-title">How Review Works</div>
                <div class="sidebar-text">
                    Every AI response is assigned a confidence score. Responses that fall below the defined confidence threshold are automatically flagged and routed to a qualified human reviewer for validation before being released as the authoritative final answer.
                </div>
            </div>
            <div class="sidebar-card">
                <div class="sidebar-title">Review Workflow Steps</div>
                <ul class="sidebar-list">
                    <li><strong style="color:#fff;">Step 1 — Query submitted:</strong> Your question is sent to the AI engine and a unique Request ID is assigned.</li>
                    <li><strong style="color:#fff;">Step 2 — Confidence assessed:</strong> The system scores its response. High-confidence answers are returned immediately.</li>
                    <li><strong style="color:#fff;">Step 3 — Routed for review:</strong> Low-confidence responses are queued in Airtable for expert review.</li>
                    <li><strong style="color:#fff;">Step 4 — Reviewer decision:</strong> A reviewer approves, edits, or overrides the AI response and records their decision.</li>
                    <li><strong style="color:#fff;">Step 5 — Final answer available:</strong> Use the Reviewed Responses tab with your Request ID to retrieve the approved answer.</li>
                </ul>
            </div>
            <div class="sidebar-card">
                <div class="sidebar-title">Review Statuses</div>
                <ul class="sidebar-list">
                    <li><strong style="color:#fff;">Pending:</strong> Awaiting assignment to a reviewer.</li>
                    <li><strong style="color:#fff;">In Review:</strong> Currently being assessed by a compliance expert.</li>
                    <li><strong style="color:#fff;">Approved:</strong> AI answer confirmed as accurate and compliant.</li>
                    <li><strong style="color:#fff;">Overridden:</strong> Reviewer has provided a corrected authoritative response.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------- Header ----------
st.markdown(
    """
    <div class="brand-shell">
        <div class="brand-topline">
            <div class="brand-logo">🛡️</div>
            <div>
                <div class="brand-name">Clarionyx</div>
                <div class="brand-tagline">
                    Regulatory Compliance Intelligence System For Health Care and Lifesciences
                </div>
            </div>
        </div>
        <div class="brand-subbar">
            <span class="brand-pill">Healthcare AI</span>
            <span class="brand-pill">Regulatory Compliance</span>
            <span class="brand-pill">Human-in-the-Loop Review</span>
            <span class="brand-pill">GDPR • HIPAA • NIST</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["Ask a Question", "Reviewed Responses"])

# ---------- Tab 1 ----------
with tab1:
    framework_options = {
        "Not sure — search across all approved sources": "auto",
        "GDPR — EU personal data / privacy": "gdpr",
        "HIPAA — US protected health information": "hipaa",
        "NIST — cybersecurity / control requirements": "nist",
    }

    selected_framework_label = st.selectbox(
        "Select the relevant compliance framework / jurisdiction",
        options=list(framework_options.keys()),
        index=0,
        help="Choose a framework when you know the regulatory context. Use 'Not sure' to search across all approved sources."
    )
    selected_framework = framework_options[selected_framework_label]

    question = st.text_area("Enter your compliance question", height=140)

    with st.expander("Suggested demo questions"):
        st.markdown(
            """
- **Direct response:** What is Protected Health Information (PHI) under HIPAA?
- **Direct response:** What does GDPR say about withdrawal of consent?
- **Direct response:** What does HIPAA allow for treatment, payment, and healthcare operations?
- **Direct response:** What are the core functions of the NIST Cybersecurity Framework?
- **Reviewer validation:** Can GDPR, HIPAA, and NIST together define the exact legal compliance steps for AI-based patient risk scoring across Germany and the US, including all exceptions?
"""
        )

    if st.button("Generate Answer", key="generate_answer_btn"):
        if not question.strip():
            st.warning("Please enter a question before submitting.")
        else:
            try:
                start_time = time.time()

                with st.spinner("Analyzing sources and generating response..."):
                    response = requests.post(
                        API_URL,
                        json={
                            "question": question,
                            "user_id": user_id.strip() or "demo_user",
                            "framework": selected_framework,
                        },
                        timeout=120,
                    )
                    response.raise_for_status()
                    data = response.json()

                execution_time_sec = round(time.time() - start_time, 2)
                st.session_state.latest_record_id = data.get("record_id", "")

                # Question
                st.markdown(
                    f"""
                    <div class="section-card">
                        <div class="section-heading">User Question</div>
                        <div class="question-body">{html.escape(str(data.get("question", question)))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Generated Answer
                raw_answer = data.get("answer")
                if raw_answer is None or str(raw_answer).strip() == "":
                    raw_answer = "No response returned."

                answer_html = format_answer_html(raw_answer)

                with st.expander("Generated Answer", expanded=True):
                    st.markdown(
                        f"""
                        <div class="response-card">
                            <div class="response-heading">Response</div>
                            <div class="response-body">{answer_html}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Citations
                citations = collect_citations(data)
                render_citation_chips(citations)

                # Request Record ID
                if st.session_state.latest_record_id:
                    record_id_escaped = html.escape(st.session_state.latest_record_id)
                    st.markdown(
                        f"""
                        <div class="section-card compact-card">
                            <div class="section-heading">Request Record ID</div>
                            <div class="small-muted">Save this ID to retrieve the reviewed response later.</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    components.html(
                        f"""
                        <div style="display:flex;align-items:center;gap:10px;font-family:'Inter',sans-serif;">
                            <div id="rid1" style="flex:1;background:#F8FAFC;border:1px solid #D8E3F0;border-radius:10px;
                                padding:11px 16px;font-size:1rem;font-weight:700;color:#0F4C81;
                                word-break:break-all;font-family:monospace;">
                                {record_id_escaped}
                            </div>
                            <button id="cbtn1" onclick="
                                navigator.clipboard.writeText(document.getElementById('rid1').innerText.trim())
                                .then(function(){{
                                    document.getElementById('cbtn1').innerText='✓ Copied!';
                                    document.getElementById('cbtn1').style.background='#059669';
                                    setTimeout(function(){{
                                        document.getElementById('cbtn1').innerText='⧉ Copy ID';
                                        document.getElementById('cbtn1').style.background='#0F4C81';
                                    }},2000);
                                }})
                                .catch(function(){{
                                    var t=document.createElement('textarea');
                                    t.value=document.getElementById('rid1').innerText.trim();
                                    t.style.position='fixed';t.style.opacity='0';
                                    document.body.appendChild(t);t.focus();t.select();
                                    document.execCommand('copy');document.body.removeChild(t);
                                    document.getElementById('cbtn1').innerText='✓ Copied!';
                                    document.getElementById('cbtn1').style.background='#059669';
                                    setTimeout(function(){{
                                        document.getElementById('cbtn1').innerText='⧉ Copy ID';
                                        document.getElementById('cbtn1').style.background='#0F4C81';
                                    }},2000);
                                }});
                            "
                            style="flex-shrink:0;background:#0F4C81;color:#fff;border:none;border-radius:10px;
                                padding:10px 20px;font-size:0.92rem;font-weight:700;cursor:pointer;
                                white-space:nowrap;font-family:'Inter',sans-serif;">
                                ⧉ Copy ID
                            </button>
                        </div>
                        """,
                        height=55,
                    )

                # Optional backend message
                if data.get("message"):
                    st.markdown(
                        f"""
                        <div class="message-box">
                            {html.escape(str(data["message"]))}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                regulations = data.get("regulations", [])
                regulations_text = ", ".join(regulations) if regulations else "N/A"
                confidence = data.get("confidence", "N/A")
                status = data.get("status", "N/A")
                needs_review = data.get("needs_human_review", False)

             

                # KPI cards
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    render_kpi_card("Workflow Status", str(status).replace("_", " ").title())
                with col2:
                    render_kpi_card("Review Required", "Yes" if needs_review else "No")
                with col3:
                    render_kpi_card("Applicable Frameworks", regulations_text)
                with col4:
                    confidence_text = f"{confidence:.3f}" if isinstance(confidence, (int, float)) else "N/A"
                    render_kpi_card("Confidence", confidence_text)
                with col5:
                    render_kpi_card("Execution Time", f"{execution_time_sec:.2f} sec")

                with st.expander("Response Metadata"):
                    response_metadata = dict(data)
                    response_metadata["selected_framework"] = selected_framework
                    response_metadata["execution_time_sec"] = execution_time_sec
                    response_metadata["user_id"] = user_id.strip() or "demo_user"
                    st.json(response_metadata)

            except requests.exceptions.RequestException as e:
                st.error(f"API request failed: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

# ---------- Tab 2 ----------
with tab2:
    st.markdown(
        """
        <div class="small-muted">
            Retrieve the authoritative reviewed response using the most recent request ID from this session,
            or enter an Airtable record ID manually.
        </div>
        """,
        unsafe_allow_html=True,
    )

    manual_record_id = st.text_input(
        "Airtable Record ID (optional override)",
        value="",
        key="manual_record_id_input",
    )

    record_id_to_use = manual_record_id.strip() or st.session_state.latest_record_id

    if record_id_to_use:
        record_id_escaped2 = html.escape(record_id_to_use)
        st.markdown(
            """
            <div class="section-card compact-card" style="margin-bottom:6px;">
                <div class="section-heading">Current Request Record ID</div>
                <div class="small-muted">Paste an ID above or use the one from your last query.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        components.html(
            f"""
            <div style="display:flex;align-items:center;gap:10px;font-family:'Inter',sans-serif;">
                <div id="rid2" style="flex:1;background:#F8FAFC;border:1px solid #D8E3F0;border-radius:10px;
                    padding:11px 16px;font-size:1rem;font-weight:700;color:#0F4C81;
                    word-break:break-all;font-family:monospace;">
                    {record_id_escaped2}
                </div>
                <button id="cbtn2" onclick="
                    navigator.clipboard.writeText(document.getElementById('rid2').innerText.trim())
                    .then(function(){{
                        document.getElementById('cbtn2').innerText='✓ Copied!';
                        document.getElementById('cbtn2').style.background='#059669';
                        setTimeout(function(){{
                            document.getElementById('cbtn2').innerText='⧉ Copy ID';
                            document.getElementById('cbtn2').style.background='#0F4C81';
                        }},2000);
                    }})
                    .catch(function(){{
                        var t=document.createElement('textarea');
                        t.value=document.getElementById('rid2').innerText.trim();
                        t.style.position='fixed';t.style.opacity='0';
                        document.body.appendChild(t);t.focus();t.select();
                        document.execCommand('copy');document.body.removeChild(t);
                        document.getElementById('cbtn2').innerText='✓ Copied!';
                        document.getElementById('cbtn2').style.background='#059669';
                        setTimeout(function(){{
                            document.getElementById('cbtn2').innerText='⧉ Copy ID';
                            document.getElementById('cbtn2').style.background='#0F4C81';
                        }},2000);
                    }});
                "
                style="flex-shrink:0;background:#0F4C81;color:#fff;border:none;border-radius:10px;
                    padding:10px 20px;font-size:0.92rem;font-weight:700;cursor:pointer;
                    white-space:nowrap;font-family:'Inter',sans-serif;">
                    ⧉ Copy ID
                </button>
            </div>
            """,
            height=55,
        )
    else:
       st.markdown(
          """
          <div class="section-card compact-card">
             <div class="small-muted">None available yet — submit a question first.</div>
          </div>
          """,
          unsafe_allow_html=True,
        )

    if st.button("Retrieve Reviewed Response", key="retrieve_reviewed_btn"):
        if not record_id_to_use:
            st.warning("No request ID is available yet. Submit a question first, or paste a record ID.")
        else:
            try:
                with st.spinner("Retrieving reviewed response..."):
                    response = requests.get(
                        f"{REVIEW_URL_BASE}/{record_id_to_use}",
                        timeout=60,
                    )
                    response.raise_for_status()
                    data = response.json()

                if not data.get("found", False):
                    st.warning(data.get("message", "No review record found."))
                else:
                    st.markdown(
                        f"""
                        <div class="review-summary-card">
                            <div class="section-heading">Review Summary</div>
                            <div class="review-row"><strong>Question:</strong> {html.escape(str(data.get("question", "")))}</div>
                            <div class="review-row"><strong>Decision:</strong> {html.escape(str(data.get("review_decision", "")))}</div>
                            <div class="review-row"><strong>Reviewed By:</strong> {html.escape(str(data.get("reviewed_by", "")))}</div>
                            <div class="review-row"><strong>Reviewed At:</strong> {html.escape(str(data.get("reviewed_at", "")))}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    final_answer_html = format_answer_html(
                        data.get("effective_final_answer", "No final reviewed response available.")
                    )

                    with st.expander("Final Reviewed Response", expanded=True):
                        st.markdown(
                            f"""
                            <div class="reviewed-response-card">
                                <div class="response-heading">Final Reviewed Response</div>
                                <div class="response-body">{final_answer_html}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    if data.get("reviewer_notes"):
                        st.markdown(
                            f"""
                            <div class="section-card">
                                <div class="section-heading">Reviewer Notes</div>
                                <div class="response-body">{html.escape(str(data["reviewer_notes"]))}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    if data.get("citations"):
                        if isinstance(data.get("citations"), list):
                            citations_list = [str(c).strip() for c in data.get("citations", []) if str(c).strip()]
                        else:
                            citations_text = str(data.get("citations", ""))
                            citations_list = [c.strip() for c in citations_text.split(",") if c.strip()]
                        render_citation_chips(citations_list)

                    with st.expander("Review Metadata"):
                        st.json(data)

            except requests.exceptions.RequestException as e:
                st.error(f"Review API request failed: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")