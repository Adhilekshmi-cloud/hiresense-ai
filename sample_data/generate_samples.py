"""
Generate sample resume TXT files for testing the screening system.
"""
from __future__ import annotations

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent
RESUMES_DIR = _project_root / "resumes"

SAMPLE_RESUMES = {
    "alice_ml_engineer.txt": """ALICE MARTINEZ
Senior Machine Learning Engineer

SUMMARY
Experienced ML engineer with 5+ years building production NLP and computer vision systems.
Passionate about deploying scalable AI solutions using modern frameworks.

SKILLS
Python, PyTorch, TensorFlow, Scikit-learn, Pandas, NumPy, Hugging Face Transformers,
BERT, GPT, Natural Language Processing, Deep Learning, Docker, AWS, Kubernetes,
FastAPI, SQL, PostgreSQL, Git, CI/CD, MLOps, Model Deployment

EXPERIENCE
Senior ML Engineer — TechCorp AI (2021–Present)
- Built a resume screening pipeline using Sentence Transformers and FAISS
- Deployed NLP models serving 10K+ daily requests via FastAPI on AWS
- Achieved 94% accuracy on text classification tasks using fine-tuned BERT

ML Engineer — DataWorks Inc. (2019–2021)
- Developed computer vision models for product quality inspection
- Reduced inference time by 40% using model quantization (ONNX)
- Built data pipelines processing 2TB+ daily using Apache Spark

EDUCATION
M.S. Computer Science — Stanford University (2019)
B.Tech Information Technology — IIT Bombay (2017)
""",
    "bob_frontend_dev.txt": """BOB JOHNSON
Frontend Developer

SUMMARY
Creative frontend developer with 3 years of experience building responsive web apps.
Strong in React ecosystem and modern CSS.

SKILLS
JavaScript, TypeScript, React, Next.js, HTML, CSS, Tailwind, Node.js, Express,
REST API, GraphQL, Git, Figma, UI/UX Design

EXPERIENCE
Frontend Developer — WebStudio (2022–Present)
- Built a SaaS dashboard using React and Next.js with 50K MAU
- Implemented responsive designs with Tailwind CSS and Framer Motion
- Integrated REST APIs and GraphQL endpoints

Junior Developer — StartupXYZ (2021–2022)
- Developed landing pages and marketing sites
- Improved page load speed by 60% using Next.js SSR

EDUCATION
B.S. Computer Science — University of Michigan (2021)
""",
    "carol_data_scientist.txt": """CAROL CHEN
Data Scientist

SUMMARY
Data scientist with 4 years of experience in statistical modeling, machine learning,
and NLP. Skilled at turning business questions into data-driven solutions.

SKILLS
Python, R, Scikit-learn, Pandas, NumPy, SQL, Matplotlib, Seaborn, Tableau,
Machine Learning, Natural Language Processing, Data Analysis, Feature Engineering,
Statistical Modeling, A/B Testing, Power BI, Excel, Communication

EXPERIENCE
Senior Data Scientist — AnalyticsCo (2022–Present)
- Developed an NLP-based customer sentiment analysis system (BERT + Scikit-learn)
- Built recommendation engine improving user engagement by 25%
- Lead A/B testing framework across 3 product teams

Data Analyst — BigRetail (2020–2022)
- Created dashboards in Tableau and Power BI for executive reporting
- Performed cohort analysis and churn prediction using logistic regression
- Automated ETL pipelines saving 20 hours/week

EDUCATION
M.S. Data Science — Columbia University (2020)
B.S. Mathematics — UC Berkeley (2018)
""",
    "dave_devops.txt": """DAVE WILSON
DevOps Engineer

SUMMARY
DevOps engineer with 6 years experience in cloud infrastructure and CI/CD automation.
Focused on AWS and Kubernetes-based deployments.

SKILLS
AWS, Azure, GCP, Docker, Kubernetes, Terraform, Ansible, Jenkins, CI/CD,
Linux, Bash, Python, Git, GitHub Actions, Prometheus, Grafana, Helm

EXPERIENCE
Senior DevOps Engineer — CloudScale (2020–Present)
- Managed 200+ microservices on Kubernetes across 3 AWS regions
- Built CI/CD pipelines reducing deployment time from 2 hours to 15 minutes
- Implemented infrastructure-as-code with Terraform (100+ modules)

DevOps Engineer — ServerPros (2018–2020)
- Migrated on-premise systems to AWS (50+ services)
- Set up monitoring and alerting with Prometheus and Grafana

EDUCATION
B.S. Computer Engineering — Georgia Tech (2018)
""",
    "eve_nlp_researcher.txt": """EVE PATEL
NLP Research Scientist

SUMMARY
NLP researcher with 4 years of experience in language models, text mining,
and information extraction. Published 5 papers in top-tier NLP conferences.

SKILLS
Python, PyTorch, TensorFlow, Hugging Face Transformers, BERT, GPT, LLM,
Natural Language Processing, Deep Learning, Scikit-learn, Pandas, NumPy,
Data Science, Machine Learning, Feature Engineering, Model Deployment,
Research, Academic Writing, Communication

EXPERIENCE
NLP Research Scientist — AI Research Lab (2022–Present)
- Fine-tuned LLMs for domain-specific text classification (F1: 0.96)
- Developed a novel entity recognition system for medical texts
- Published 3 papers at ACL and EMNLP conferences

Research Assistant — University NLP Lab (2020–2022)
- Built text summarization models using BART and T5
- Created benchmark datasets for sentiment analysis in low-resource languages
- 2 papers published at NAACL

EDUCATION
Ph.D. Computer Science (NLP) — Carnegie Mellon University (2024, expected)
M.S. Artificial Intelligence — University of Edinburgh (2020)
B.Tech Computer Science — IIT Delhi (2018)
""",
}


def generate_samples():
    """Write sample resumes to the resumes/ directory."""
    RESUMES_DIR.mkdir(exist_ok=True)
    for filename, content in SAMPLE_RESUMES.items():
        (RESUMES_DIR / filename).write_text(content.strip(), encoding="utf-8")
    print(f"[OK] Generated {len(SAMPLE_RESUMES)} sample resumes in {RESUMES_DIR}")


if __name__ == "__main__":
    generate_samples()
