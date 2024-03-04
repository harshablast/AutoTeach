import json
import os
import sys

sys.path.append("./../")

import streamlit as st
from streamlit_agraph import Config, Edge, Node, agraph

from sensai.curriculum import concept_hierarchy, learning_outcomes

st.title("Sensai Prototype")
st.header("Concept Graph Creation Demo")
st.divider()

SUBJECTS_DIR = "./data/subjects"
SUBJECTS = os.listdir(SUBJECTS_DIR)

st.subheader("Select a Subject")
st.selectbox("Subject", SUBJECTS, key="subject")

subject_topics_filepath = os.path.join(
    SUBJECTS_DIR, st.session_state.subject, "topics.json"
)
subject_concepts_filepath = os.path.join(
    SUBJECTS_DIR, st.session_state.subject, "concepts.json"
)
subject_content_emb_filepath = os.path.join(
    SUBJECTS_DIR, st.session_state.subject, "content_embeddings.json"
)
subject_learning_outcomes_filepath = os.path.join(
    SUBJECTS_DIR, st.session_state.subject, "learning_outcomes.json"
)

if os.path.exists(subject_topics_filepath):
    st.session_state.subject_topics_file_exists = True
    st.session_state.subject_topics = json.load(open(subject_topics_filepath, "r"))
else:
    st.session_state.subject_topics_file_exists = False
    st.session_state.subject_topics = None

if os.path.exists(subject_concepts_filepath):
    st.session_state.subject_concepts_file_exists = True
    st.session_state.subject_concepts = json.load(open(subject_concepts_filepath, "r"))
else:
    st.session_state.subject_concepts_file_exists = False
    st.session_state.subject_concepts = {}

if os.path.exists(subject_learning_outcomes_filepath):
    st.session_state.subject_learning_outcomes_file_exists = True
    st.session_state.subject_learning_outcomes = json.load(
        open(subject_learning_outcomes_filepath, "r")
    )
else:
    st.session_state.subject_learning_outcomes_file_exists = False
    st.session_state.subject_learning_outcomes = {}

if st.session_state.subject_topics:
    st.subheader("Select a Topic")
    st.selectbox("Topic", st.session_state.subject_topics, key="topic")

    if st.session_state.topic in st.session_state.subject_concepts:
        st.session_state.subject_topic_concepts_exist = True
        st.session_state.subject_topic_concepts = st.session_state.subject_concepts[
            st.session_state.topic
        ]
    else:
        st.session_state.subject_topic_concepts_exist = False
        st.session_state.subject_topic_concepts = {}

    if st.session_state.subject_topic_concepts_exist:
        st.subheader("Topic Concepts (JSON)")
        st.json(st.session_state.subject_topic_concepts)
        st.subheader("Topic Concepts (Graph)")
        nodes = []
        edges = []
        for node in st.session_state.subject_topic_concepts["nodes"]:
            nodes.append(
                Node(
                    id=node["id"],
                    label=node["name"],
                    color="#FBBC05" if node["type"] == "concept" else "#575DFB",
                    shape="ellipse" if node["type"] == "concept" else "text",
                    font="24 sans-serif #000000"
                    if node["type"] == "concept"
                    else "16 sans-serif #575DFB",
                    mass=16 if node["type"] == "concept" else 4,
                )
            )
        for edge in st.session_state.subject_topic_concepts["edges"]:
            edges.append(
                Edge(
                    source=edge["source"],
                    target=edge["target"],
                    color="#FBBC05" if edge["type"] == "concept" else "#575DFB",
                    length=25 if edge["type"] == "concept" else 4,
                    width=2 if edge["type"] == "concept" else 1,
                    type="arrow",
                )
            )

        config = Config(
            directed=True,
            physics=True,
        )
        st.write(agraph(nodes=nodes, edges=edges, config=config))

    else:
        st.caption("No Concepts Found for this Topic")

    st.button(
        "Create Concepts"
        if not st.session_state.subject_topic_concepts_exist
        else "Recreate Concepts",
        key="create_concepts",
    )
    if st.session_state.create_concepts:
        progress_bar = st.progress(0, text="Creating Concept Hierarchy Graph...")
        if not os.path.exists(subject_content_emb_filepath):
            content_embeddings = None
        else:
            content_embeddings = json.load(open(subject_content_emb_filepath, "r"))

        st.session_state.subject_topic_concepts = (
            concept_hierarchy.create_concept_hierarchy(
                st.session_state.subject,
                st.session_state.topic,
                content_embeddings=content_embeddings,
                progress_bar=progress_bar,
            )
        )
        st.session_state.subject_concepts[
            st.session_state.topic
        ] = st.session_state.subject_topic_concepts

        with open(subject_concepts_filepath, "w") as f:
            json.dump(st.session_state.subject_concepts, f)

        st.experimental_rerun()

    if st.session_state.subject_topic_concepts_exist:
        if st.session_state.topic in st.session_state.subject_learning_outcomes:
            st.session_state.subject_topic_learning_outcomes_exist = True
            st.session_state.subject_topic_learning_outcomes = (
                st.session_state.subject_learning_outcomes[st.session_state.topic]
            )
        else:
            st.session_state.subject_topic_learning_outcomes_exist = False
            st.session_state.subject_topic_learning_outcomes = {}

        if st.session_state.subject_topic_learning_outcomes_exist:
            st.subheader("Topic Learning Outcomes (JSON)")
            st.json(st.session_state.subject_topic_learning_outcomes)
        else:
            st.caption("No Learning Outcomes Found for this Topic")

        st.button(
            "Create Learning Outcomes"
            if not st.session_state.subject_topic_learning_outcomes_exist
            else "Recreate Learning Outcomes",
            key="create_learning_outcomes",
        )
        if st.session_state.create_learning_outcomes:
            with st.spinner("Creating Learning Outcomes..."):
                st.session_state.subject_topic_learning_outcomes = (
                    learning_outcomes.create_learning_outcomes_stages(
                        st.session_state.subject,
                        st.session_state.topic,
                        st.session_state.subject_topic_concepts,
                    )
                )
                st.session_state.subject_learning_outcomes[
                    st.session_state.topic
                ] = st.session_state.subject_topic_learning_outcomes

                with open(subject_learning_outcomes_filepath, "w") as f:
                    json.dump(st.session_state.subject_learning_outcomes, f)

                st.experimental_rerun()
