# Teacher Coach AI

Teacher Coach AI is an autonomous, intelligent educational assistant designed to support teachers in rural schools and under-resourced communities. The platform helps educators analyze student performance, identify learning gaps in real-time, and generate personalized, curriculum-aligned reinforcement recommendations, operating strictly locally (*offline-first*).

---

## 📋 The Problem

In many vulnerable communities and rural areas, teachers face multi-grade or overcrowded classrooms, operating under the following constraints:
- Lack of pedagogical advisors or advanced analytics tools.
- Limited, unstable, or non-existent internet connectivity.
- Low-cost computers or limited hardware unable to run heavy enterprise software.

This makes it extremely difficult to provide personalized tracking and design effective leveling strategies for each student.

---

## 💡 The Solution

Teacher Coach AI combines performance data ingestion with a local Artificial Intelligence engine to offer instant diagnostics. The system securely processes grades and attendance, detects at-risk students, and leverages Google's open models to structure actionable pedagogical plans—all without sending a single byte of data outside the school's local computer.

---

## ✨ Key Features

- **Flexible Data Upload:** Interface to upload student lists via Excel or CSV with dynamic column mapping.
- **Admin Curriculum Configuration:** Allows uploading official guidelines (e.g., MEDUCA national curriculum frameworks) to guide AI responses.
- **Predictive Gap Analysis:** Local algorithms that classify school risk levels based on grades and attendance.
- **Smart RAG-Lite Recommendations:** Dynamic injection of the curriculum into the model's prompt to ensure pedagogical alignment and prevent AI hallucinations.
- **Teacher Dashboard:** Interactive visual panel with bar charts to identify weak subject areas at a group level.
- **Offline & Low-Cost Design:** Optimized to run 100% without internet connection and on standard, low-spec hardware.
- **1-Click Installation:** Automated setup scripts with bilingual support (English/Spanish) for non-technical users.

---

## 🛠️ Technology Stack

- **Language:** Python 3.9+
- **User Interface:** Streamlit
- **Data Processing:** Pandas, OpenPyXL
- **Local Inference Engine:** Ollama
- **AI Models:** Gemma 4 Open Models Family (Google)

---

## 🧠 Local AI & Curriculum Integration (RAG-Lite)

The technical core of the application uses a Retrieval-Augmented Generation (RAG) approach adapted for local environments. Before performing inference, the system intercepts the evaluated topic, extracts the corresponding objectives and contents from the loaded institutional curriculum, and builds an enriched prompt.

To ensure stability on standard school computers without dedicated GPUs, the backend is configured by default to use **`gemma4:e2b`**, requiring less than 3 GB of RAM/VRAM for smooth inference execution.

### RAG Pipeline Implementation Example

```python
import ollama

# Official curriculum context is dynamically injected based on the student's topic
prompt = f"""
Student Data:
- Topic: {row['Topic']}
- Score: {row['Score']}/100

Official curriculum context:
{curriculum_context}

Generate a brief pedagogical recommendation using local environmental resources.
"""

response = ollama.chat(
    model="gemma4:e2b", # Lightweight edge model optimized for low-cost hardware
    messages=[
        {"role": "system", "content": "You are an educational assistant. You respond briefly, directly, and in a structured format."},
        {"role": "user", "content": prompt}
    ]
)

recommendation = response.get("message", {}).get("content", "").strip()
```

---

## 🧭 Workflow

1. **Institutional Setup:** The administrator or principal uploads the educational curriculum file and defines alignment rules in the admin tab.
2. **Teacher Input:** The teacher downloads the Excel template, adds their group's grades, and uploads it to the system.
3. **Dynamic Mapping:** The software adapts any file structure to the required application variables.
4. **Gap Analysis:** Upon clicking analyze, the system calculates risk levels and triggers concurrent calls to Ollama.
5. **Insights Visualization:** The system generates a dashboard showing group weaknesses and a detailed table with exact pedagogical recommendations for each student.

---

## 📂 Project Structure

```text
teacher-coach-ai/
│
├── start_teacher_coach.bat      # 1-Click Windows Setup & Run Script
├── start_teacher_coach.sh       # 1-Click Linux/Mac Setup & Run Script
├── app.py                       # Main Streamlit app (UI & RAG Logic)
├── requirements.txt             # Project dependencies
├── README.md                    # Main documentation
│
├── data/
│   └── admin_curriculum_example.csv  # Sample curriculum dataset (MEDUCA)
│
├── curriculum_uploads/          # Local storage for uploaded curricula
├── uploads/                     # Local storage for uploaded student files
│
├── kaggle/
│   └── teacher_coach_ai_gemma_demo.ipynb  # Cloud testing and dev environment
└── docs/                        # Additional technical documentation
```

---

## 🚀 Requirements & Quick Start (1-Click Install)

This project is designed for users without technical backgrounds (like rural educators). You do not need to install dependencies or pull models manually.

### Prerequisites
1. **Python 3.9+** must be installed on your system.
2. **Ollama** must be installed and running in the background. Download it from [ollama.com](https://ollama.com).

### Setup & Run
Download or clone this repository, open the folder, and run the automated script for your operating system:

**For Windows:**
Double-click the `start_teacher_coach.bat` file.

**For Linux / macOS:**
Open your terminal, navigate to the folder, and run:
```bash
chmod +x start_teacher_coach.sh
./start_teacher_coach.sh
```

*The script will automatically ask for your preferred setup language (English/Spanish), install all Python dependencies, verify/pull the required `gemma4:e2b` local model, and launch the application directly in your web browser.*

---

## 👨‍💻 Credits & Mentorship

- **Ximena Williams:** Software Architect, Lead Developer & Project Creator.
- **David Guevara:** Lead Software Architect, Core Developer & AI Mentor.
