import sys

sys.path.append("../../")

from sensai.assessment import SensaiAssessment

import streamlit as st

st.session_state.update(st.session_state)

st.header("Assessment")
st.subheader("Subject: " + st.session_state["subject"])
st.subheader("Topic: " + st.session_state["topic"])
st.subheader("Learning Outcomes")
st.json(st.session_state["subject_topic_learning_outcomes"])

st.subheader("Select a Learning Outcome Stage")
st.selectbox(
    "Learning Outcome",
    st.session_state["subject_topic_learning_outcomes"],
    key="learning_outcome_stage",
)

st.write(st.session_state["learning_outcome_stage"]["learning_outcomes"])

if "learning_outcome_stage" in st.session_state:
    st.subheader("Select a Learning Outcome")
    st.selectbox(
        "Learning Outcome",
        st.session_state["learning_outcome_stage"]["learning_outcomes"],
        key="learning_outcome",
    )

if st.button("Start Assessment"):
    st.session_state["assessment_started"] = True

if "assessment_started" not in st.session_state:
    st.session_state["assessment_started"] = False

if st.session_state["assessment_started"]:
    if "assessment_messages" not in st.session_state:
        st.session_state["sensai_assessment"] = SensaiAssessment(
            st.session_state["subject"],
            st.session_state["topic"],
            st.session_state["learning_outcome"],
            st.session_state["subject_topic_concepts"],
        )

        st.session_state["assessment_messages"] = st.session_state[
            "sensai_assessment"
        ].start_assessment()

    for assessment_message in st.session_state.assessment_messages[1:]:
        with st.chat_message(assessment_message["role"]):
            st.markdown(assessment_message["content"])

    if user_answer := st.chat_input("Please enter your answer."):
        st.session_state["assessment_messages"].append(
            {"role": "user", "content": user_answer}
        )

        (
            st.session_state["assessment_messages"],
            end_assessment,
        ) = st.session_state[
            "sensai_assessment"
        ].handle_user_answer(st.session_state["assessment_messages"])

        if end_assessment:
            evaluation = st.session_state["sensai_assessment"].evaluate_assessment(
                st.session_state["assessment_messages"]
            )
            st.session_state["assessment_messages"].append(
                {"role": "assistant", "content": evaluation}
            )
