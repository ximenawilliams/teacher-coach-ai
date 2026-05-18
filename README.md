# Teacher Coach AI

Teacher Coach AI is an autonomous, intelligent educational assistant designed to support teachers in rural schools and under-resourced communities. The platform helps educators analyze student performance, identify learning gaps in real-time, and generate personalized, curriculum-aligned reinforcement recommendations, operating strictly locally (*offline-first*) with zero cloud operational costs.

---

## 📋 The Problem: The Disconnected Classroom

In many vulnerable communities and rural areas across Latin America, teachers face multi-grade or overcrowded classrooms under severe infrastructural constraints:
- **Lack of Guidance:** Absence of pedagogical advisors or advanced data analytics tools.
- **Zero Connectivity:** Limited, unstable, or non-existent internet access, rendering cloud AI APIs useless.
- **Legacy Hardware:** Low-cost computers or donated hardware with limited RAM/CPU, incapable of running heavy enterprise platforms.

This makes it extremely difficult to provide personalized tracking and design effective leveling strategies for each student.

---

## 💡 The Solution

Teacher Coach AI combines local data processing with a hardware-adaptive local AI inference engine to offer instant diagnostics. The system securely ingests grades and attendance, detects at-risk students, and leverages local open models to structure actionable pedagogical plans—all without sending a single byte of data outside the school's local computer, ensuring absolute student data privacy.

---

## ✨ Key Features

- **📴 Offline & Low-Cost Design:** Optimized to run 100% without an internet connection and on standard, low-spec legacy hardware.
- **⚡ 1-Click Installation:** Automated, non-technical setup scripts with Multilingual support (English, Español, Português, and Français) to provision the environment seamlessly.
- **🌐 Native Multilingual Interface:** Complete, hot-swappable localization across 4 production languages: English, Español, Português, and Français.
- **🤖 Hardware-Adaptive Edge Engine:** Built-in dynamic discovery service that queries the local Ollama daemon and gracefully adapts execution between frontier heavy models or ultra-lightweight text weights.
- **📋 Admin Curriculum Ingestion (RAG-Lite):** Allows loading official guidelines (e.g., MEDUCA national curriculum frameworks) to contextually steer AI responses and match regional educational goals.
- **📊 Predictive Gap Diagnostics:** Automated grading risk categorization (High, Medium, Low) driven by configurable thresholds on academic score and attendance rates.


---

## 🛠️ Technology Stack

- **Language:** Python 3.9+
- **User Interface:** Streamlit (Optimized for decoupled session state management)
- **Data Processing:** Pandas, OpenPyXL
- **Local Inference Engine:** Ollama Core Service
- **Supported AI Models:** Google Gemma Family (`gemma4:e2b`, `gemma2:2b`, `gemma3:1b`)

---

## 🏗️ Architectural Engineering Feats

To ensure the system could run reliably inside a classroom environment without dedicated GPUs or data center access, the application incorporates the following professional software architecture paradigms:

### 1. Graceful Hardware Degradation
The system abstracts model execution. If high-end hardware is present, it runs **Gemma 4 Edge (5.1B)** to leverage advanced multimodal and reasoning (*thinking*) capabilities. On ultra-constrained hardware, the user can downscale seamlessly to **Gemma 2 (2B)** or **Gemma 3 (1B)**, lowering RAM requirements to less than 2 GB while keeping the prompt framework intact.

### 2. Single-Worker Concurrency Control
Running heavy LLM inference locally on standard CPUs easily triggers thread starvation and OS lockups. The backend implements an asynchronous isolation layer using `concurrent.futures.ThreadPoolExecutor(max_workers=1)`. This forces a structured sequential queue that updates the UI progress bar in real time while protecting the host CPU from thermal throttling or Out-Of-Memory (OOM) crashes.

### 3. Decoupled UI Data Contracts
To prevent multi-language prompting from breaking down on smaller models, the layout structure is fully decoupled. The application extracts translation strings from the master `I18N` dictionary and injects them dynamically as structural layout constraints (`labels_out`). This preserves formatting consistency across all target languages without strict hardcoding.

### 4. Calibrated Context Windows
The inference options are fine-tuned at the engine level (`num_ctx: 8192`, `num_predict: 1200`). This specific ceiling provides the necessary context headroom to hold large chunks of injected curriculum guidelines (RAG) while giving the model's reasoning block the exact token budget needed to complete text generation without abrupt cuts.

---

## 🧠 Core RAG Pipeline Implementation

The core inference engine targets local context isolation, mapping student parameters against curriculum frameworks dynamically:

```python
def get_gemma_recommendation(row, model_name, curriculum_description, target_lang, labels_out):
    gap_lbl, act_lbl, guide_lbl = labels_out
    
    # Decoupled layout instructions injected dynamically via unpacked language labels
    prompt = f"""
Respond STRICTLY and ONLY in {target_lang}.
Do not greet. Do not explain that you are an AI.

Respond using exactly this layout structure format structure:
{gap_lbl}:

{act_lbl}:

{guide_lbl}:

Maximum 80 words.

Student Performance Context Parameters:
- Name: {row.get('Student', '')}
- Grade: {row.get('Grade', '')}
- Subject: {row.get('Subject', '')}
- Topic: {row.get('Topic', '')}
- Score: {row.get('Score', '')}
- Attendance: {row.get('Attendance', '')}
"""
    if curriculum_description:
        prompt += f"\nTake into account the following school curriculum framework:\n{curriculum_description}"

    response = ollama.chat(
        model=model_name,
        messages=[
            {"role": "system", "content": f"You are a helpful local educational advisor. You respond in {target_lang}."},
            {"role": "user", "content": prompt}
        ],
        options={
            "num_ctx": 8192,       # Calibrated RAG headroom
            "num_predict": 1200,   # Secure window for reasoning chains
            "temperature": 0.3     # Format determinism ceiling
        }
    )
    return response.get("message", {}).get("content", "").strip()
```

---

## 🧭 Workflow

```text
[1. Admin Curriculum Upload] ──> [2. Teacher Data Ingestion] ──> [3. Dynamic Variable Mapping]
                                                                              │
                                                                              ▼
[5. Interactive Dashboard]   <── [4. Single-Worker Thread Queue] <── [AI Gap Analysis Clicked]
```

1. **Institutional Setup:** The administrator or principal uploads the base educational framework (e.g., MEDUCA CSV guidelines) inside the Admin tab.
2. **Teacher Input:** The teacher downloads the Excel template, adds their group's grades, and drops the student registry file into the workspace.
3. **Dynamic Mapping:** The interface matches user-defined column layouts onto the system's required core variables.
4. **Local Analysis Execution:** Upon clicking analyze, the background queue safely dispatches records to the local Ollama backend one by one.
5. **Insights Visualization:** The UI builds an aggregate diagnostic dashboard showing group weaknesses alongside direct student pedagogical recommendations.

---

## 📂 Project Structure

```text
teacher-coach-ai/
│
├── start_teacher_coach.bat      # 1-Click Windows Setup & Run Script
├── start_teacher_coach.sh       # 1-Click Linux/Mac Setup & Run Script
├── app.py                       # Main Streamlit Application (Core UI & RAG Pipeline)
├── requirements.txt             # Target Python dependencies
├── README.md                    # System documentation
│
├── data/
│   └── admin_curriculum_example.csv  # Base template for institutional frameworks (MEDUCA)
│
├── curriculum_uploads/          # Persistent local storage for administrative targets
├── uploads/                     # Secure local directory for teacher grade uploads
│
├── kaggle/
│   └── teacher_coach_ai_gemma_demo.ipynb  # Notebook sandbox for cloud validation
└── docs/                        # Engineering design specifications
```

---

## 🚀 Requirements & Quick Start (1-Click Install)

This architecture is built for immediate local deployment by non-technical users. It completely automates virtual environment setup, package installations, and model provisioning.

### Prerequisites
1. **Python 3.9+** must be installed on your operating system.
2. **Ollama Core Daemon** must be running in the background. Download it from [ollama.com](https://ollama.com).

### Automated Execution
Clone or extract this repository into a local directory, open the folder, and run the wrapper script matching your environment:

**For Windows Environments:**
Double-click the `start_teacher_coach.bat` file.

**For Linux / macOS Environments:**
Open a terminal instance inside the project root and run:
```bash
chmod +x start_teacher_coach.sh
./start_teacher_coach.sh
```

*The script initialization pipeline will automatically ask for your setup language, build a localized virtual environment, install dependencies, verify/pull your chosen lightweight Gemma weights from the local daemon registries, and launch the application directly in your default browser.*

---

## 👨‍💻 Credits & Mentorship

- **Ximena Williams:** Software Architect, Lead Developer & Project Creator.
- **David Guevara:** Lead Software Architect, Core Developer & AI Mentor.
