"""
🚀 AI Resume Screening System — Streamlit Frontend

A modern dark-themed UI for uploading resumes, screening candidates,
and comparing models with full explainability.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import streamlit as st
import pandas as pd

from core.pipeline import parse_resume, ParseError
from core.text_cleaner import process_resume, ResumeData
from core.embeddings import EmbeddingManager
from core.scoring import ResumeScorer, ScoringResult
from core.explainer import ResumeExplainer
from core.evaluator import ModelEvaluator

# ── Page Config ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1040 30%, #0d1b2a 70%, #0a0e27 100%);
        color: #e0e6ed;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1535 0%, #111a3a 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.15);
    }

    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #818cf8, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        letter-spacing: -0.5px;
    }

    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 2rem;
        font-weight: 300;
    }

    .metric-card {
        background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.3rem;
    }

    .verdict-strong {
        background: linear-gradient(135deg, rgba(34,197,94,0.15), rgba(34,197,94,0.05));
        border-left: 4px solid #22c55e;
        padding: 1rem 1.5rem;
        border-radius: 0 12px 12px 0;
        margin: 0.5rem 0;
    }

    .verdict-good {
        background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(59,130,246,0.05));
        border-left: 4px solid #3b82f6;
        padding: 1rem 1.5rem;
        border-radius: 0 12px 12px 0;
        margin: 0.5rem 0;
    }

    .verdict-partial {
        background: linear-gradient(135deg, rgba(234,179,8,0.15), rgba(234,179,8,0.05));
        border-left: 4px solid #eab308;
        padding: 1rem 1.5rem;
        border-radius: 0 12px 12px 0;
        margin: 0.5rem 0;
    }

    .verdict-weak {
        background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(239,68,68,0.05));
        border-left: 4px solid #ef4444;
        padding: 1rem 1.5rem;
        border-radius: 0 12px 12px 0;
        margin: 0.5rem 0;
    }

    .skill-tag-match {
        display: inline-block;
        background: rgba(34,197,94,0.15);
        color: #4ade80;
        border: 1px solid rgba(34,197,94,0.3);
        border-radius: 20px;
        padding: 0.25rem 0.75rem;
        font-size: 0.8rem;
        margin: 0.15rem;
        font-weight: 500;
    }

    .skill-tag-missing {
        display: inline-block;
        background: rgba(239,68,68,0.15);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.3);
        border-radius: 20px;
        padding: 0.25rem 0.75rem;
        font-size: 0.8rem;
        margin: 0.15rem;
        font-weight: 500;
    }

    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #c7d2fe;
        margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(99, 102, 241, 0.2);
    }

    div[data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #818cf8, #a78bfa) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Session State Init ─────────────────────────────────────────────────────

if "resume_store" not in st.session_state:
    st.session_state.resume_store: dict[str, ResumeData] = {}
if "results" not in st.session_state:
    st.session_state.results = None


# ── Sidebar ────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    model_name = st.selectbox(
        "Embedding Model",
        ["all-MiniLM-L6-v2", "all-mpnet-base-v2"],
        help="MiniLM is faster; MPNet is more accurate.",
    )
    top_n = st.slider("Top Candidates", 1, 20, 5)

    st.markdown("---")
    st.markdown("### 📊 Scoring Weights")
    w_skills = st.slider("Skills", 0.0, 1.0, 0.40, 0.05)
    w_semantic = st.slider("Semantic", 0.0, 1.0, 0.30, 0.05)
    w_experience = st.slider("Experience", 0.0, 1.0, 0.20, 0.05)
    w_education = st.slider("Education", 0.0, 1.0, 0.10, 0.05)

    total_w = w_skills + w_semantic + w_experience + w_education
    if abs(total_w - 1.0) > 0.01:
        st.warning(f"⚠️ Weights sum to {total_w:.2f} — should be 1.0")

    st.markdown("---")
    st.markdown(
        f"**Resumes Loaded:** {len(st.session_state.resume_store)}"
    )
    if st.button("🗑️ Clear All Resumes"):
        st.session_state.resume_store.clear()
        st.session_state.results = None
        st.rerun()


# ── Main Content ───────────────────────────────────────────────────────────

st.markdown('<div class="main-title">🚀 AI Resume Screening System</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Semantic matching · Weighted scoring · Full explainability</div>',
    unsafe_allow_html=True,
)

# ── Upload + JD ────────────────────────────────────────────────────────────

col_upload, col_jd = st.columns(2)

with col_upload:
    st.markdown('<div class="section-header">📂 Upload Resumes</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Drag and drop resume files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        for uf in uploaded_files:
            if uf.name not in st.session_state.resume_store:
                try:
                    raw = parse_resume(uf.read(), filename=uf.name)
                    rd = process_resume(raw, filename=uf.name)
                    st.session_state.resume_store[uf.name] = rd
                except ParseError as e:
                    st.error(f"❌ {uf.name}: {e}")

        st.success(
            f"✅ {len(st.session_state.resume_store)} resume(s) loaded"
        )

with col_jd:
    st.markdown('<div class="section-header">📄 Job Description</div>', unsafe_allow_html=True)
    job_description = st.text_area(
        "Paste the job description here",
        height=200,
        placeholder="We are looking for a Python developer with 3+ years of experience in machine learning...",
        label_visibility="collapsed",
    )


# ── Action Buttons ─────────────────────────────────────────────────────────

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    run_screening = st.button("🔍 Screen Resumes", use_container_width=True)

with col_btn2:
    run_comparison = st.button("📊 Compare Models", use_container_width=True)


# ── Screening Logic ───────────────────────────────────────────────────────

if run_screening:
    if not job_description or len(job_description) < 10:
        st.warning("⚠️ Please enter a job description (at least 10 characters).")
    elif not st.session_state.resume_store:
        st.warning("⚠️ Please upload at least one resume.")
    else:
        with st.spinner("🧠 Analyzing resumes with AI..."):
            filenames = list(st.session_state.resume_store.keys())
            resume_texts = [
                st.session_state.resume_store[fn].clean_text
                for fn in filenames
            ]

            # Semantic similarity
            emb = EmbeddingManager(model_name)
            sem_scores = emb.semantic_similarity(job_description, resume_texts)

            # Scoring + Explainability
            scorer = ResumeScorer(w_skills, w_semantic, w_experience, w_education)
            explainer = ResumeExplainer()

            all_results = []
            for i, fname in enumerate(filenames):
                sr = scorer.score(
                    resume_text=resume_texts[i],
                    jd_text=job_description,
                    semantic_sim=float(sem_scores[i]),
                    filename=fname,
                )
                expl = explainer.explain(sr)
                all_results.append((sr, expl))

            # Sort by score
            all_results.sort(key=lambda x: x[0].final_score, reverse=True)
            st.session_state.results = all_results

# ── Display Results ────────────────────────────────────────────────────────

if st.session_state.results:
    results = st.session_state.results

    st.markdown('<div class="section-header">🏆 Screening Results</div>', unsafe_allow_html=True)

    # Overview metrics
    m1, m2, m3, m4 = st.columns(4)
    top_score = results[0][0].final_score * 100 if results else 0
    avg_score = sum(r[0].final_score for r, _ in results) / len(results) * 100
    strong_count = sum(1 for _, e in results if e.verdict == "STRONG MATCH")

    with m1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{len(results)}</div>'
            f'<div class="metric-label">Total Resumes</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{top_score:.1f}%</div>'
            f'<div class="metric-label">Top Score</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{avg_score:.1f}%</div>'
            f'<div class="metric-label">Avg Score</div></div>',
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{strong_count}</div>'
            f'<div class="metric-label">Strong Matches</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("")

    # Candidate cards
    for rank, (sr, expl) in enumerate(results[:top_n], 1):
        pct = sr.final_score * 100
        verdict_class = {
            "STRONG MATCH": "verdict-strong",
            "GOOD MATCH": "verdict-good",
            "PARTIAL MATCH": "verdict-partial",
            "WEAK MATCH": "verdict-weak",
        }.get(expl.verdict, "verdict-partial")

        # Verdict emoji
        verdict_emoji = {
            "STRONG MATCH": "🟢",
            "GOOD MATCH": "🔵",
            "PARTIAL MATCH": "🟡",
            "WEAK MATCH": "🔴",
        }.get(expl.verdict, "⚪")

        st.markdown(
            f'<div class="{verdict_class}">'
            f'<strong>#{rank} {sr.filename}</strong> — '
            f'{pct:.1f}% {verdict_emoji} {expl.verdict}'
            f'</div>',
            unsafe_allow_html=True,
        )

        with st.expander(f"📋 Details for {sr.filename}"):
            # Summary
            st.markdown(f"**{expl.summary}**")

            # Score breakdown
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Skills", f"{sr.skills_score*100:.1f}%")
            c2.metric("Semantic", f"{sr.semantic_score*100:.1f}%")
            c3.metric("Experience", f"{sr.experience_score*100:.1f}%")
            c4.metric("Education", f"{sr.education_score*100:.1f}%")

            # Skills tags
            col_matched, col_missing = st.columns(2)
            with col_matched:
                st.markdown("**✅ Matched Skills**")
                if expl.matched_skills:
                    tags = " ".join(
                        f'<span class="skill-tag-match">{s}</span>'
                        for s in expl.matched_skills
                    )
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.caption("No matching skills found")

            with col_missing:
                st.markdown("**❌ Missing Skills**")
                if expl.missing_skills:
                    tags = " ".join(
                        f'<span class="skill-tag-missing">{s}</span>'
                        for s in expl.missing_skills
                    )
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.caption("No missing skills")

            # Strengths / Weaknesses
            if expl.strengths:
                st.markdown("**💪 Strengths**")
                for s in expl.strengths:
                    st.markdown(f"- {s}")
            if expl.weaknesses:
                st.markdown("**⚠️ Weaknesses**")
                for w in expl.weaknesses:
                    st.markdown(f"- {w}")

    # CSV Export
    st.markdown("---")
    export_data = []
    for rank, (sr, expl) in enumerate(results, 1):
        export_data.append({
            "Rank": rank,
            "Filename": sr.filename,
            "Final Score (%)": round(sr.final_score * 100, 2),
            "Verdict": expl.verdict,
            "Skills (%)": round(sr.skills_score * 100, 2),
            "Semantic (%)": round(sr.semantic_score * 100, 2),
            "Experience (%)": round(sr.experience_score * 100, 2),
            "Education (%)": round(sr.education_score * 100, 2),
            "Matched Skills": ", ".join(expl.matched_skills),
            "Missing Skills": ", ".join(expl.missing_skills),
        })

    df = pd.DataFrame(export_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Results CSV",
        csv,
        "screening_results.csv",
        "text/csv",
        use_container_width=True,
    )

# ── Model Comparison ──────────────────────────────────────────────────────

if run_comparison:
    if not job_description or len(job_description) < 10:
        st.warning("⚠️ Please enter a job description.")
    elif not st.session_state.resume_store:
        st.warning("⚠️ Please upload at least one resume.")
    else:
        with st.spinner("🔬 Running model comparison..."):
            filenames = list(st.session_state.resume_store.keys())
            resume_texts = [
                st.session_state.resume_store[fn].clean_text
                for fn in filenames
            ]

            evaluator = ModelEvaluator()
            report = evaluator.compare(
                job_description=job_description,
                resume_texts=resume_texts,
                resume_filenames=filenames,
            )

        st.markdown('<div class="section-header">📊 Model Comparison</div>', unsafe_allow_html=True)

        # Timing
        time_cols = st.columns(len(report.benchmarks))
        for col, bm in zip(time_cols, report.benchmarks):
            with col:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-value">{bm.elapsed_seconds:.3f}s</div>'
                    f'<div class="metric-label">{bm.model_name}</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("")

        # Score comparison table
        comp_data = {"Resume": filenames}
        for bm in report.benchmarks:
            comp_data[bm.model_name] = [
                f"{s*100:.2f}%" for s in bm.scores
            ]
        comp_df = pd.DataFrame(comp_data)
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

        # Ranking comparison
        st.markdown("**Rankings by Model**")
        rank_data = {"Resume": filenames}
        for bm in report.benchmarks:
            rank_data[bm.model_name] = bm.ranking
        rank_df = pd.DataFrame(rank_data)
        st.dataframe(rank_df, use_container_width=True, hide_index=True)

        # Bar chart
        chart_data = pd.DataFrame({
            bm.model_name: bm.scores for bm in report.benchmarks
        }, index=filenames)
        st.bar_chart(chart_data)
