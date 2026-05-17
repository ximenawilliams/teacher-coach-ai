import streamlit as st
import pandas as pd
import ollama
from io import BytesIO
from pathlib import Path
import concurrent.futures

if "curriculum_df" not in st.session_state:
    try:
        st.session_state.curriculum_df = pd.read_csv("data/admin_curriculum_example.csv")
    except Exception:
        st.session_state.curriculum_df = None

CURRICULUM_UPLOAD_DIR = Path("curriculum_uploads")
CURRICULUM_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Teacher Coach AI", page_icon="📚", layout="wide")

# ==========================================
# Gemma Model Configuration (Official V4)
# ==========================================
OLLAMA_MODELS = [
    "gemma4:e2b",  # Lightweight Edge model (Default)
    "gemma4:e4b",  # Medium Edge model
    "gemma4:26b",  # Heavy reasoning model
    "gemma4:31b",  # Advanced reasoning model
    "gemma4",
]

selected_model = st.sidebar.selectbox(
    "Select Gemma/Ollama model",
    OLLAMA_MODELS,
    index=0
)

st.session_state.selected_model = selected_model

st.markdown("""
<style>
.block-container { padding-top: 2rem; padding-bottom: 3rem; }
.title { font-size:42px; font-weight:900; color:#0f172a; margin-bottom:6px; }
.subtitle { font-size:18px; color:#475569; margin-bottom:24px; }
.card { background:white; padding:24px; border-radius:24px; border:1px solid #e2e8f0; box-shadow:0 12px 35px rgba(15,23,42,.08); margin-bottom:18px; }
.badge { display:inline-block; background:#eef6ff; color:#1d4ed8; padding:8px 14px; border-radius:999px; font-weight:800; margin-bottom:12px; }
.offline { background:#fef3c7; color:#92400e; }
.metric { background:white; padding:20px; border-radius:20px; border:1px solid #e2e8f0; box-shadow:0 10px 25px rgba(15,23,42,.06); }
.metric-label { color:#64748b; font-size:14px; font-weight:700; }
.metric-value { color:#0f172a; font-size:32px; font-weight:900; }
.recommendation { background:#f8fafc; border:1px solid #e2e8f0; padding:14px; border-radius:16px; margin-bottom:10px; color:#334155; }
</style>
""", unsafe_allow_html=True)

sample_data = pd.DataFrame({
    "Student": ["Ana", "Luis", "Marta", "Carlos", "Sofia", "Pedro", "Elena", "Diego"],
    "Grade": [5, 5, 5, 5, 5, 5, 5, 5],
    "Subject": ["Math", "Reading", "Math", "Science", "Math", "Reading", "Math", "Science"],
    "Topic": ["Fractions", "Main Idea", "Decimals", "Plants", "Fractions", "Inference", "Fractions", "Water Cycle"],
    "Competency": ["Problem Solving", "Comprehension", "Numerical Reasoning", "Observation", "Problem Solving", "Inference", "Problem Solving", "Scientific Thinking"],
    "Score": [58, 62, 55, 72, 61, 69, 57, 75],
    "Attendance": [82, 90, 78, 95, 88, 80, 76, 92],
    "Objective": ["Improve classroom performance"] * 8,
    "Resources": ["Notebook, board, local objects"] * 8,
    "Teaching_Method": ["Guided practice"] * 8,
    "Evaluation_Type": ["Short quiz"] * 8
})

required_columns = ["Student", "Grade", "Subject", "Topic", "Competency", "Score", "Attendance"]

def create_template():
    output = BytesIO()
    sample_data.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    return output

def read_uploaded_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)

def load_uploaded_dataframe(uploaded_file):
    content = uploaded_file.getvalue()
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(BytesIO(content))
    return pd.read_excel(BytesIO(content))

def save_uploaded_file(uploaded_file, save_dir):
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / Path(uploaded_file.name).name
    with open(file_path, "wb") as out_file:
        out_file.write(uploaded_file.getvalue())
    return file_path

def validate_file(df):
    return [col for col in required_columns if col not in df.columns]

# Executed safely on the Main Thread
def build_curriculum_description():

    # 1. Intentar usar curriculum subido por docente/admin
    curriculum_df = st.session_state.get("curriculum_df")

    # 2. Si no existe, cargar curriculum default
    if curriculum_df is None or curriculum_df.empty:
        default_path = Path("data/admin_curriculum_example.csv")

        if default_path.exists():
            try:
                curriculum_df = pd.read_csv(default_path)
            except Exception:
                curriculum_df = None

    # 3. Si aun no existe nada
    if curriculum_df is None or curriculum_df.empty:
        return "Use general teaching recommendations aligned with the uploaded student data."

    # 4. Construir descripción curriculum
    text = "Curriculum guidelines found:\n"

    target_columns = [
        "Subject",
        "Topic",
        "Objectives",
        "Contents",
        "Indicators",
        "Activities"
    ]

    available_cols = [c for c in target_columns if c in curriculum_df.columns]

    if not available_cols:
        available_cols = list(curriculum_df.columns[:4])

    for index, row in curriculum_df.head(3).fillna("").iterrows():

        parts = [
            f"{col}: {row[col]}"
            for col in available_cols
            if str(row[col]).strip()
        ]

        if parts:
            text += f"{index + 1}. " + "; ".join(parts) + "\n"

    text += "\nUse this curriculum to validate learning gaps and propose aligned activities."

    return text

# Thread-safe function: All context is explicitly passed as arguments
def get_gemma_recommendation(row, model_name, curriculum_description):
    prompt = f"""
Respond ONLY with this format.
Do not greet.
Do not say "Hello".
Do not say "As Gemma".
Do not explain that you are an AI.

Learning Gap:
Reinforcement Activity:
Teacher Guide:

Maximum 80 words.

Student Data:
- Name: {row.get('Student', '')}
- Grade: {row.get('Grade', '')}
- Subject: {row.get('Subject', '')}
- Topic: {row.get('Topic', '')}
- Competency: {row.get('Competency', '')}
- Score: {row.get('Score', '')}
- Attendance: {row.get('Attendance', '')}
"""

    if curriculum_description:
        prompt += f"""
Take into account the following school curriculum when generating the recommendation:

{curriculum_description}

Educational Context:
- Curriculum Source: {st.session_state.get("curriculum_source")}
- Grade Level: {st.session_state.get("curriculum_grade")}
- Subjects: {st.session_state.get("curriculum_subject")}
- Teacher Guidance: {st.session_state.get("curriculum_instructions")}

Validate the student's learning gap based on this curriculum.

Suggest activities aligned with:
- objectives
- contents
- indicators
- classroom activities

The recommendation MUST explicitly align with the uploaded curriculum.

If the gap cannot be directly covered by the curriculum,
suggest complementary activities that respect its objectives.
"""
    else:
        prompt += """
No specific curriculum was found.
Generate open pedagogical recommendations using educational best practices for low-resource classrooms.
Do not assume internet access or expensive materials.
"""

    prompt += """
Generate a practical and brief recommendation for the teacher.

Include:
1. Learning Gap
2. Reinforcement Activity
3. Brief guide for the teacher
"""


    try:
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are an educational assistant. You respond briefly, directly, and in a structured format. No greetings."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response.get("message", {}).get("content", "").strip()
    except Exception as e:
        return f"Error generating recommendation: {e}"

# Thread-safe execution pipeline
def generate_gemma_recommendations(df, model_name, curriculum_description):
    records = df.to_dict(orient="records")
    total = len(records)
    progress = st.progress(0)
    status_text = st.empty()
    
    recommendations = [None] * total
    completed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Explicitly passing model_name and curriculum_description to the worker threads
        future_to_index = {
            executor.submit(get_gemma_recommendation, row, model_name, curriculum_description): i 
            for i, row in enumerate(records)
        }
        
        for future in concurrent.futures.as_completed(future_to_index):
            i = future_to_index[future]
            try:
                recommendations[i] = future.result()
            except Exception as e:
                recommendations[i] = f"Error generating recommendation: {e}"
            
            completed += 1
            progress.progress(int(completed / total * 100))
            status_text.text(f"⚡ Processing with threads: {completed} of {total} students completed using {model_name}...")
            
    progress.empty()
    status_text.empty()
    return recommendations


def analyze_students(df, model_name, curriculum_description):
    df = df.copy()
    df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
    df["Attendance"] = pd.to_numeric(df["Attendance"], errors="coerce")

    def risk(row):
        if row["Score"] < 60 or row["Attendance"] < 80:
            return "High"
        if row["Score"] < 70:
            return "Medium"
        return "Low"

    df["Risk_Level"] = df.apply(risk, axis=1)
    df["Gemma_4_Recommendation"] = generate_gemma_recommendations(df, model_name, curriculum_description)

    summary = {
        "students": df["Student"].nunique(),
        "average": round(df["Score"].mean(), 1),
        "at_risk": df[df["Risk_Level"].isin(["High", "Medium"])]["Student"].nunique(),
        "weakest_subject": df.groupby("Subject")["Score"].mean().sort_values().index[0],
    }
    return df, summary

if "screen" not in st.session_state:
    st.session_state.screen = "login"
if "df" not in st.session_state:
    st.session_state.df = sample_data.copy()
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "curriculum_file_path" not in st.session_state:
    st.session_state.curriculum_file_path = ""
if "student_column_mapping" not in st.session_state:
    st.session_state.student_column_mapping = {}
if "curriculum_column_mapping" not in st.session_state:
    st.session_state.curriculum_column_mapping = {}
if "curriculum_source" not in st.session_state:
    st.session_state.curriculum_source = "MEDUCA"
if "curriculum_grade" not in st.session_state:
    st.session_state.curriculum_grade = "5th Grade"
if "curriculum_subject" not in st.session_state:
    st.session_state.curriculum_subject = "Math / Reading / Science"
if "curriculum_instructions" not in st.session_state:
    st.session_state.curriculum_instructions = "Align recommendations with the official curriculum. Do not suggest content outside the current school plan unless it reinforces required learning objectives."
if "username" not in st.session_state:
    st.session_state.username = ""
if "password" not in st.session_state:
    st.session_state.password = "admin"
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0
if "force_curriculum_view" not in st.session_state:
    st.session_state.force_curriculum_view = False

st.markdown("<div class='title'>📚 Teacher Coach AI</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Offline educational assistant powered by Gemma for rural and low-resource schools.</div>", unsafe_allow_html=True)

if st.session_state.screen == "login":
    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        st.markdown("<span class='badge offline'>📴 Local · Low Cost · Offline Ready</span>", unsafe_allow_html=True)
        st.markdown("## Welcome, teacher")
        st.write("Analyze student grades, identify learning gaps, and receive practical recommendations to improve classroom performance, even in places with limited internet access.")
        st.markdown("- 📊 Student performance analysis\n- 🤖 Gemma AI recommendations\n- 🧭 Curriculum alignment\n- 👩‍🏫 Personalized support per student")
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Teacher Login")
        username = st.text_input("Username", value=st.session_state.get("username", ""))
        password = st.text_input("Password", type="password", value=st.session_state.get("password", "admin"))
        if st.button("Login", use_container_width=True):
            if username == "admin" and password == "admin":
                st.session_state.username = username
                st.session_state.password = password
                st.session_state.screen = "index"
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Incorrect username or password. Use admin/admin.")
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.screen == "index":
    st.markdown("<span class='badge'>🤖 AI Analysis Setup</span>", unsafe_allow_html=True)
    
    if st.session_state.force_curriculum_view:
        st.markdown("## Admin Curriculum Configuration")
        st.write("Upload MEDUCA content, national curriculum, school director guidelines, or the teacher's base lesson plan. This becomes the minimum educational framework Gemma must follow.")
        curriculum_source = st.selectbox(
            "Curriculum source",
            ["MEDUCA", "National Ministry of Education", "School Director Guidelines", "Teacher Base Plan", "Regional Curriculum"],
            index=["MEDUCA", "National Ministry of Education", "School Director Guidelines", "Teacher Base Plan", "Regional Curriculum"].index(st.session_state.curriculum_source),
        )
        grade_level = st.text_input("Grade level", value=st.session_state.curriculum_grade)
        subject = st.text_input("Subject", value=st.session_state.curriculum_subject)
        uploaded_curriculum = st.file_uploader("Browse curriculum file", type=["xlsx", "csv", "pdf", "docx"])
        curriculum_instructions = st.text_area("Curriculum alignment instructions", value=st.session_state.curriculum_instructions)

        if uploaded_curriculum:
            saved_path = save_uploaded_file(uploaded_curriculum, CURRICULUM_UPLOAD_DIR)
            st.session_state.curriculum_file_path = str(saved_path)
            if uploaded_curriculum.name.lower().endswith((".csv", ".xlsx", ".xls")):
                try:
                    curriculum_df = load_uploaded_dataframe(uploaded_curriculum)
                    st.session_state.curriculum_df = curriculum_df
                    st.success(f"Curriculum saved to: {saved_path}")
                except Exception as e:
                    st.session_state.curriculum_df = None
                    st.error(f"Error reading curriculum file: {e}")
            else:
                st.info(f"File saved to: {saved_path}")

        if st.session_state.curriculum_file_path:
            st.info(f"Loaded curriculum file: {st.session_state.curriculum_file_path}")
        if st.session_state.curriculum_df is not None:
            st.markdown("### Curriculum Preview")
            st.dataframe(st.session_state.curriculum_df.head(10), use_container_width=True)
            st.markdown("**Curriculum Columns:** " + ", ".join(st.session_state.curriculum_df.columns))
            st.markdown("### Map Curriculum Columns")
            curriculum_fields = ["Objectives", "Contents", "Indicators", "Activities"]
            cols = list(st.session_state.curriculum_df.columns)
            new_mapping = {}
            for field in curriculum_fields:
                selection = st.selectbox(f"Column for '{field}'", ["-- None --"] + cols, index=0, key=f"map_curr_{field}")
                if selection != "-- None --":
                    new_mapping[selection] = field
            if st.button("Apply Curriculum Mapping"):
                try:
                    mapped = st.session_state.curriculum_df.rename(columns=new_mapping)
                    st.session_state.curriculum_df = mapped
                    st.session_state.curriculum_column_mapping = new_mapping
                    st.success("Curriculum mapping applied successfully.")
                    st.dataframe(st.session_state.curriculum_df.head(10), use_container_width=True)
                except Exception as e:
                    st.error(f"Error applying mapping: {e}")

        st.success("Curriculum configuration will guide Gemma recommendations.")
        st.session_state.curriculum_source = curriculum_source
        st.session_state.curriculum_grade = grade_level
        st.session_state.curriculum_subject = subject
        st.session_state.curriculum_instructions = curriculum_instructions
        
        if st.button("✅ Back to Teacher Upload", use_container_width=True, key="back_to_upload"):
            st.session_state.force_curriculum_view = False
            st.rerun()
    else:
        tab1, tab2 = st.tabs(["Teacher Upload", "Admin Curriculum"])

        with tab2:
            st.markdown("## Admin Curriculum Configuration")
            st.write("Upload MEDUCA content, national curriculum, school director guidelines, or the teacher's base lesson plan. This becomes the minimum educational framework Gemma must follow.")
            curriculum_source = st.selectbox(
                "Curriculum source",
                ["MEDUCA", "National Ministry of Education", "School Director Guidelines", "Teacher Base Plan", "Regional Curriculum"],
                index=["MEDUCA", "National Ministry of Education", "School Director Guidelines", "Teacher Base Plan", "Regional Curriculum"].index(st.session_state.curriculum_source),
                key="tab2_curriculum_source"
            )
            grade_level = st.text_input("Grade level", value=st.session_state.curriculum_grade, key="tab2_grade")
            subject = st.text_input("Subject", value=st.session_state.curriculum_subject, key="tab2_subject")
            uploaded_curriculum = st.file_uploader("Browse curriculum file", type=["xlsx", "csv", "pdf", "docx"], key="tab2_uploader")
            curriculum_instructions = st.text_area("Curriculum alignment instructions", value=st.session_state.curriculum_instructions, key="tab2_instructions")

            if uploaded_curriculum:
                saved_path = save_uploaded_file(uploaded_curriculum, CURRICULUM_UPLOAD_DIR)
                st.session_state.curriculum_file_path = str(saved_path)
                if uploaded_curriculum.name.lower().endswith((".csv", ".xlsx", ".xls")):
                    try:
                        curriculum_df = load_uploaded_dataframe(uploaded_curriculum)
                        st.session_state.curriculum_df = curriculum_df
                        st.success(f"Curriculum saved to: {saved_path}")
                    except Exception as e:
                        st.session_state.curriculum_df = None
                        st.error(f"Error reading curriculum file: {e}")
                else:
                    st.info(f"File saved to: {saved_path}")

            if st.session_state.curriculum_file_path:
                st.info(f"Loaded curriculum file: {st.session_state.curriculum_file_path}")
            if st.session_state.curriculum_df is not None:
                st.markdown("### Curriculum Preview")
                st.dataframe(st.session_state.curriculum_df.head(10), use_container_width=True)
                st.markdown("**Curriculum Columns:** " + ", ".join(st.session_state.curriculum_df.columns))
                st.markdown("### Map Curriculum Columns")
                curriculum_fields = ["Objectives", "Contents", "Indicators", "Activities"]
                cols = list(st.session_state.curriculum_df.columns)
                new_mapping = {}
                for field in curriculum_fields:
                    selection = st.selectbox(f"Column for '{field}'", ["-- None --"] + cols, index=0, key=f"tab2_map_curr_{field}")
                    if selection != "-- None --":
                        new_mapping[selection] = field
                if st.button("Apply Curriculum Mapping", key="tab2_apply_map"):
                    try:
                        mapped = st.session_state.curriculum_df.rename(columns=new_mapping)
                        st.session_state.curriculum_df = mapped
                        st.session_state.curriculum_column_mapping = new_mapping
                        st.success("Curriculum mapping applied successfully.")
                        st.dataframe(st.session_state.curriculum_df.head(10), use_container_width=True)
                    except Exception as e:
                        st.error(f"Error applying mapping: {e}")

            st.success("Curriculum configuration will guide Gemma recommendations.")
            st.session_state.curriculum_source = curriculum_source
            st.session_state.curriculum_grade = grade_level
            st.session_state.curriculum_subject = subject
            st.session_state.curriculum_instructions = curriculum_instructions

        if st.button("Logout", key="logout_index", help="Return to login"): 
            st.session_state.screen = "login"
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.password = ""
            st.rerun()

        with tab1:
            st.markdown("## Upload Student Performance Data")
            st.write("Upload an Excel or CSV file with student grades, attendance, subjects, topics, and competencies.")
            st.download_button("Download Excel Template", data=create_template(), file_name="teacher_coach_ai_template.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            uploaded_file = st.file_uploader("Browse student Excel or CSV file", type=["xlsx", "csv"])
            st.text_area("Additional teacher instructions for Gemma", value="Focus on students with low attendance and low scores. Recommend simple activities that do not require internet or expensive materials.")

            if uploaded_file:
                try:
                    saved_path = save_uploaded_file(uploaded_file, UPLOAD_DIR)
                    df = load_uploaded_dataframe(uploaded_file)
                    st.session_state.df = df
                    st.success(f"File uploaded and saved to: {saved_path}")
                    st.dataframe(df.head(10), use_container_width=True)

                    st.markdown("### Map Student File Columns")
                    cols = list(df.columns)
                    mapping = {}
                    for req in required_columns:
                        sel = st.selectbox(f"Column for '{req}'", ["-- None --"] + cols, index=0, key=f"map_student_{req}")
                        if sel != "-- None --":
                            mapping[sel] = req

                    if st.button("Apply Student Mapping"):
                        try:
                            mapped_df = df.rename(columns=mapping)
                            missing = validate_file(mapped_df)
                            if missing:
                                st.error("Missing required columns after mapping: " + ", ".join(missing))
                            else:
                                st.session_state.df = mapped_df
                                st.session_state.student_column_mapping = mapping
                                st.success("Mapping applied and data loaded successfully.")
                                st.dataframe(mapped_df.head(10), use_container_width=True)
                        except Exception as e:
                            st.error(f"Error applying student mapping: {e}")
                except Exception as e:
                    st.error(f"Error reading file: {e}")
            else:
                st.info("No file uploaded yet. The app will use sample student data for the demo.")

            st.info(f"Recommendation generation with the selected model ({st.session_state.get('selected_model')}) may take several seconds per student.")
            
            curriculum_exists = Path("data/admin_curriculum_example.csv").exists() or st.session_state.curriculum_df is not None
            can_proceed = True

            if not curriculum_exists:
                st.warning("⚠️ No attached curriculum found (admin_curriculum_example.csv).")
                st.info("An evaluation without a curriculum will be performed, limiting recommendations to general best practices.")
                can_proceed = st.checkbox("I understand, continue without a personalized curriculum", key="confirm_skip_curr")
                
                if not can_proceed:
                     if st.button("❌ Go to configure curriculum", use_container_width=True):
                         st.session_state.force_curriculum_view = True
                         st.rerun()

            if can_proceed:
                if st.button("Analyze gaps with AI", use_container_width=True):
                    missing = validate_file(st.session_state.df)
                    if missing:
                        st.error("Missing required columns before analysis: " + ", ".join(missing))
                    else:
                        try:
                            # CRITICAL ARCHITECTURAL FIX: 
                            # We build the RAG text and fetch model name on the MAIN THREAD before spawning workers
                            curr_desc = build_curriculum_description()
                            model_name = st.session_state.get("selected_model", "gemma4:e2b")
                            
                            final_df, summary = analyze_students(st.session_state.df, model_name, curr_desc)
                            
                            # Clean error tracking mapped to the correct dynamic variable
                            errors = [r for r in final_df["Gemma_4_Recommendation"] if isinstance(r, str) and r.startswith("Error generating recommendation:")]
                            if errors:
                                st.error("An error occurred during Ollama recommendation generation. Please check model availability.")
                                for err in errors[:3]:
                                    st.warning(err)
                            st.session_state.analysis = {"df": final_df, "summary": summary}
                            st.session_state.screen = "dashboard"
                            st.rerun()
                        except Exception as e:
                            st.error("Error generating recommendations: " + str(e))

elif st.session_state.screen == "dashboard":
    df = st.session_state.analysis["df"]
    summary = st.session_state.analysis["summary"]

    st.markdown("<span class='badge'>✨ AI Insights</span>", unsafe_allow_html=True)
    st.markdown("## Teacher Analytics Dashboard")
    if st.button("Logout", key="logout_dashboard", help="Return to login from dashboard"):
        st.session_state.screen = "login"
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.password = ""
        st.rerun()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric'><div class='metric-label'>Students analyzed</div><div class='metric-value'>{summary['students']}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric'><div class='metric-label'>Class average</div><div class='metric-value'>{summary['average']}%</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric'><div class='metric-label'>Students needing support</div><div class='metric-value'>{summary['at_risk']}</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric'><div class='metric-label'>Weakest subject</div><div class='metric-value' style='font-size:24px'>{summary['weakest_subject']}</div></div>", unsafe_allow_html=True)

    st.markdown("## Weak Learning Areas")
    st.bar_chart(df.groupby("Subject")["Score"].mean().sort_values())

    st.markdown("## Recommendations per Student")
    st.dataframe(df[["Student", "Grade", "Subject", "Topic", "Competency", "Score", "Attendance", "Risk_Level", "Gemma_4_Recommendation"]], use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='card'><h3>🤖 AI Recommendations</h3><div class='recommendation'>Use visual examples and classroom objects for weak topics.</div><div class='recommendation'>Create small support groups for students with similar learning gaps.</div><div class='recommendation'>Apply short weekly assessments to measure progress.</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'><h3>📅 Weekly Plan</h3><div class='recommendation'><b>Monday:</b> Guided review of weak topics.</div><div class='recommendation'><b>Wednesday:</b> Practice in small groups.</div><div class='recommendation'><b>Friday:</b> Mini assessment and feedback.</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card'><h3>🧭 Responsible AI</h3><div class='recommendation'>Recommendations are aligned with curriculum guidance.</div><div class='recommendation'>The system avoids labeling students negatively.</div><div class='recommendation'>The teacher remains in control of decisions.</div></div>", unsafe_allow_html=True)

    if st.button("Back to Index"):
        st.session_state.screen = "index"
        st.rerun()
