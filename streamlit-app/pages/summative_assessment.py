import sys
import json
import uuid

sys.path.append("../../")

from sensai.assessment import SummativeAssessment

import streamlit as st

st.session_state.update(st.session_state)

st.header("Assessment")
st.subheader("Subject: " + st.session_state["subject"])
st.subheader("Topic: " + st.session_state["topic"])
st.subheader("Learning Outcomes")
st.json(st.session_state["subject_topic_learning_outcomes"])


lo_stages = [
    lo_stage["learning_outcome_stage"]
    for lo_stage in st.session_state["subject_topic_learning_outcomes"]
]

lo_stage = st.selectbox(
    "Learning Outcome Stage",
    lo_stages,
)

lo_stage_dict = list(
    filter(
        lambda lo_stage_d: lo_stage_d["learning_outcome_stage"] == lo_stage,
        st.session_state["subject_topic_learning_outcomes"],
    )
)[0]

los = [lo["learning_outcome"] for lo in lo_stage_dict["learning_outcomes"]]

lo = st.selectbox(
    "Learning Outcome",
    los,
)

lo_dict = list(
    filter(
        lambda lo_d: lo_d["learning_outcome"] == lo,
        lo_stage_dict["learning_outcomes"],
    )
)[0]

if st.button("Start Assessment"):
    st.session_state["assessment_started"] = True

if "assessment_started" not in st.session_state:
    st.session_state["assessment_started"] = False

if st.session_state["assessment_started"]:
    if "assessment_messages" not in st.session_state:
        st.session_state["sensai_assessment"] = SummativeAssessment(
            st.session_state["subject"],
            st.session_state["topic"],
            lo_dict,
            st.session_state["subject_topic_concepts"],
        )

        st.session_state["assessment_messages"], _ = st.session_state[
            "sensai_assessment"
        ]()

    for assessment_message in st.session_state.assessment_messages[2:]:
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
        ](st.session_state["assessment_messages"])

        if end_assessment:
            evaluation = st.session_state["sensai_assessment"].evaluate_assessment(
                st.session_state["assessment_messages"]
            )
            st.session_state["assessment_messages"].append(
                {"role": "assistant", "content": evaluation}
            )
            with open(
                f"/Users/harshabommana/Work/Sensai-Research/streamlit-app/data/users/{str(uuid.uuid4())}.json",
                "w",
            ) as f:
                json.dump(st.session_state["assessment_messages"], f)

        st.experimental_rerun()
