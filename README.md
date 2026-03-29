# 🚀 AI Resume Screening System

> Production-grade resume screening powered by **Sentence Transformers**, **weighted multi-factor scoring**, and **full explainability** — built with FastAPI + Streamlit.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Semantic Matching** | Sentence Transformer embeddings (MiniLM / MPNet) instead of keyword matching |
| **Weighted Scoring** | Skills (40%) + Semantic (30%) + Experience (20%) + Education (10%) |
| **Explainability** | Verdicts, matched/missing skills, strengths, weaknesses for every candidate |
| **Model Comparison** | Compare TF-IDF vs MiniLM vs MPNet with timing and NDCG metrics |
| **REST API** | FastAPI backend with Swagger docs, file upload, screening, model comparison |
| **Modern UI** | Streamlit frontend with dark theme, glassmorphism, and interactive cards |
| **Multi-format** | Supports PDF, DOCX, and TXT resume uploads |
| **Export** | Download ranked results as CSV |

---

## 📁 Project Structure

```
resume_screening/
├── app/
│   ├── api.py              # FastAPI REST API (5 endpoints)
│   ├── models.py           # Pydantic request/response schemas
│   └── config.py           # Environment-based configuration
├── core/
│   ├── pipeline.py         # Resume parsing (PDF/DOCX/TXT)
│   ├── text_cleaner.py     # Text cleaning + feature extraction
│   ├── embeddings.py       # Multi-model embedding manager
│   ├── scoring.py          # Weighted scoring system
│   ├── explainer.py        # Explainability & verdicts
│   └── evaluator.py        # Model comparison & metrics
├── ui/
│   └── streamlit_app.py    # Streamlit frontend
├── sample_data/
│   └── generate_samples.py # Generate test resumes
├── tests/
│   └── test_pipeline.py    # Unit tests
├── resumes/                # Sample resume files
├── requirements.txt
├── Dockerfile
├── render.yaml             # Render deployment config
└── .env.example
```

---

## 🛠️ Setup

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/ai-resume-screener.git
cd ai-resume-screener
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

### 2. Generate Sample Resumes

```bash
python sample_data/generate_samples.py
```

### 3. Run FastAPI Backend

```bash
uvicorn app.api:app --reload --port 8000
```

Open **http://localhost:8000/docs** for interactive Swagger documentation.

### 4. Run Streamlit UI

```bash
streamlit run ui/streamlit_app.py --server.port 8501
```

Open **http://localhost:8501** for the full UI experience.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/upload-resume` | Upload a resume file (PDF/DOCX/TXT) |
| `GET` | `/api/resumes` | List all uploaded resumes |
| `DELETE` | `/api/resumes` | Clear all uploaded resumes |
| `POST` | `/api/screen` | Screen resumes against a job description |
| `POST` | `/api/compare-models` | Compare TF-IDF vs Transformer models |

### Example: Screen Resumes

```bash
# Upload a resume
curl -X POST http://localhost:8000/api/upload-resume \
  -F "file=@resumes/alice_ml_engineer.txt"

# Screen against a job description
curl -X POST http://localhost:8000/api/screen \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Looking for a Python ML engineer with NLP experience",
    "model_name": "all-MiniLM-L6-v2",
    "top_n": 3
  }'
```

---

## 📊 Scoring System

```
Final Score = (0.40 × Skills Match)
            + (0.30 × Semantic Similarity)
            + (0.20 × Experience Match)
            + (0.10 × Education Match)
```

Each component produces a 0–100% score. Weights are configurable via environment variables or the Streamlit sidebar.

### Verdicts

| Score Range | Verdict |
|-------------|---------|
| ≥ 75% | 🟢 STRONG MATCH |
| ≥ 55% | 🔵 GOOD MATCH |
| ≥ 35% | 🟡 PARTIAL MATCH |
| < 35% | 🔴 WEAK MATCH |

---

## 🧪 Running Tests

```bash
python -m pytest tests/test_pipeline.py -v
```

---

## 🚢 Deployment

### Render

1. Push code to GitHub
2. Connect your repo on [render.com](https://render.com)
3. Render auto-detects `render.yaml` and deploys

### Docker

```bash
docker build -t ai-resume-screener .
docker run -p 8000:8000 ai-resume-screener
```

### HuggingFace Spaces (Streamlit)

1. Create a new Space with **Streamlit** SDK
2. Upload all project files
3. Set the main file to `ui/streamlit_app.py`

---

## 🧠 Models Used

| Model | Dimensions | Speed | Quality |
|-------|-----------|-------|---------|
| `all-MiniLM-L6-v2` | 384 | ⚡ Fast | Good |
| `all-mpnet-base-v2` | 768 | 🐢 Slower | Better |
| TF-IDF (baseline) | Variable | ⚡⚡ Fastest | Basic |

---

## 📈 GitHub Portfolio Tips

- ⭐ Add descriptive tags: `nlp`, `machine-learning`, `resume-screening`, `fastapi`, `transformers`
- 📝 Include screenshots of the Streamlit UI in your README
- 🎥 Record a demo GIF using the app
- 📊 Include model comparison results in your README
- 🧪 Maintain test coverage above 80%
- 🔄 Add GitHub Actions CI for running tests on every push

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

**Built with ❤️ for AI Engineer portfolios**
