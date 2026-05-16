# Teacher Coach AI

Teacher Coach AI is an AI-powered educational assistant designed to support teachers in underserved and low-resource schools.

The platform helps educators analyze student performance, identify learning gaps, and generate curriculum-aware reinforcement recommendations using Gemma.

---

## Problem

In many underserved communities, teachers manage overcrowded classrooms with limited access to:

- Educational advisors
- Analytics tools
- Personalized learning support
- Reliable internet connectivity

This makes individualized academic reinforcement difficult to provide consistently.

---

## Solution

Teacher Coach AI combines:

- Curriculum configuration
- Student performance analysis
- Learning gap detection
- AI-generated educational recommendations

to support teachers with practical and personalized guidance.

The platform is designed with an offline-first approach and can run on affordable hardware.

---

## Features

- Upload curriculum configuration using CSV/Excel
- Upload student performance data
- Detect students with learning gaps
- Generate curriculum-aware recommendations
- AI-powered educational reinforcement
- Simple teacher dashboard
- Designed for low-resource environments

---

## Technology Stack

- Python
- Streamlit
- Pandas
- Jupyter Notebook
- Google Generative AI
- Gemma

---

## Project Structure

```text
teacher-coach-ai/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── admin_curriculum_example.csv
│   └── student_scores.csv
│
├── kaggle/
│   └── teacher_coach_ai_gemma_demo.ipynb
│
└── docs/