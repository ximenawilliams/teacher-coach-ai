import streamlit as st
import pandas as pd
import ollama

st.set_page_config(
    page_title="Teacher Coach AI",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Teacher Coach AI - Powered by Gemma 4")
st.write("Offline AI assistant for rural teachers to analyze student performance and generate improvement plans.")

st.sidebar.header("Upload CSV Files")

student_file = st.sidebar.file_uploader(
    "Upload student_performance.csv",
    type=["csv"]
)

content_file = st.sidebar.file_uploader(
    "Upload teaching_content.csv",
    type=["csv"]
)

def analyze_data(student_df, content_df):
    merged_df = pd.merge(
        student_df,
        content_df,
        on=["Subject", "Topic"],
        how="left"
    )

    topic_summary = merged_df.groupby(
        ["Subject", "Topic", "Competency", "Objective", "Teaching_Method"]
    ).agg(
        Average_Score=("Score", "mean"),
        Average_Attendance=("Attendance", "mean"),
        Students_Count=("Student", "count")
    ).reset_index()

    weak_topics = topic_summary[topic_summary["Average_Score"] < 70]

    students_at_risk = merged_df[
        (merged_df["Score"] < 70) | (merged_df["Attendance"] < 85)
    ]

    return merged_df, topic_summary, weak_topics, students_at_risk

def build_prompt(topic_summary, weak_topics, students_at_risk):
    prompt = f"""
You are an educational advisor helping teachers in rural and underserved communities.

Analyze the following classroom performance data and teaching content.

Topic Summary:
{topic_summary.to_string(index=False)}

Weak Topics:
{weak_topics.to_string(index=False)}

Students at Risk:
{students_at_risk[["Student", "Grade", "Subject", "Topic", "Score", "Attendance"]].to_string(index=False)}

Please generate:
1. A clear classroom diagnosis.
2. The main learning gaps.
3. Teaching recommendations.
4. Low-cost classroom activities.
5. A one-week improvement plan.
6. Suggestions for students who need additional support.

Use simple language for a teacher with limited resources.
"""
    return prompt

def get_gemma_recommendations(prompt):
    response = ollama.chat(
        model="gemma3",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response["message"]["content"]

if student_file and content_file:
    student_df = pd.read_csv(student_file)
    content_df = pd.read_csv(content_file)

    st.subheader("Student Performance Data")
    st.dataframe(student_df)

    st.subheader("Teaching Content Data")
    st.dataframe(content_df)

    merged_df, topic_summary, weak_topics, students_at_risk = analyze_data(
        student_df,
        content_df
    )

    st.subheader("Academic Analysis Summary")
    st.dataframe(topic_summary)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Students Records", len(student_df))
    col2.metric("Weak Topics", len(weak_topics))
    col3.metric("Students at Risk", len(students_at_risk))

    st.subheader("Weak Learning Topics")
    st.dataframe(weak_topics)

    st.subheader("Students Requiring Support")
    st.dataframe(students_at_risk)

    if st.button("Generate Recommendations with Gemma 4"):
        with st.spinner("Gemma 4 is generating educational recommendations..."):
            prompt = build_prompt(topic_summary, weak_topics, students_at_risk)
            recommendations = get_gemma_recommendations(prompt)

        st.subheader("Gemma 4 Educational Recommendations")
        st.write(recommendations)

else:
    st.info("Please upload both CSV files to start the analysis.")