# app.py

import streamlit as st
from pipeline import run_checkpoint
from content import generate_feynman_for_mcq
from llm import get_content_llm

st.set_page_config(page_title="Learning Agent", layout="wide")

st.title("📘 Learning Agent")

# ---------- Topic Selection ----------
topic = st.text_input("Enter a topic to learn")

if "res" not in st.session_state:
    st.session_state.res = None

if st.button("Start Learning") and topic:
    st.session_state.res = run_checkpoint(topic)

# ---------- Display Content ----------
if st.session_state.res:
    res = st.session_state.res

    st.header(f"📖 Topic: {res['topic']}")
    st.write(res["content"])

    st.divider()
    st.header("🧠 MCQs")

    user_answers = []

    # ---------- MCQs ----------
    for i, mcq in enumerate(res["mcqs"]):
        st.subheader(f"Q{i + 1}. {mcq['question']}")

        choice = st.radio(
            label="Select an option",
            options=mcq["options"],
            index=None,
            key=f"mcq_{i}",
        )

        user_answers.append(choice)

    # ---------- Submit Button ----------
    if st.button("Submit Answers"):
        st.divider()
        st.header("📊 Results")

        content_llm = get_content_llm()
        correct_count = 0
        total = len(res["mcqs"])

        for i, mcq in enumerate(res["mcqs"]):
            correct_option = mcq["options"][mcq["correct_index"]]
            user_choice = user_answers[i]

            st.subheader(f"Q{i + 1}. {mcq['question']}")

            if user_choice == correct_option:
                correct_count += 1
                st.success("✅ Correct")
            else:
                st.error(f"❌ Incorrect — Correct answer: {correct_option}")

                # -------- FEYNMAN TECHNIQUE --------
                feynman = generate_feynman_for_mcq(
                    question=mcq["question"],
                    correct_answer=correct_option,
                    context=res["content"],
                    llm=content_llm,
                )

                st.markdown("**🧠 Let’s understand it simply:**")
                st.write(feynman)

        # ---------- Relevance Score ----------
        relevance_score = round((correct_count / total) * 100, 2)

        st.divider()
        st.header("🎯 Relevance Score")
        st.metric(
            label="Understanding Score",
            value=f"{relevance_score}%",
            help="Based on how many MCQs you answered correctly"
        )
