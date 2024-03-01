import os
import sys
import json

sys.path.append("./../")

import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

from sensai.curriculum import concept_hierarchy, learning_outcomes
from sensai.scripts.create_content_embeddings import create_content_embeddings

st.title("Sensai Prototype")
st.header("Concept Graph Creation Demo")
st.divider()

SUBJECTS_DIR = "./data/subjects"
SUBJECTS = os.listdir(SUBJECTS_DIR)

st.subheader("Select a Subject")
st.selectbox("Subject", SUBJECTS, key="subject")

subject_content_dir = os.path.join(SUBJECTS_DIR, st.session_state.subject, "content")
subject_content_emb_filepath = os.path.join(
    SUBJECTS_DIR, st.session_state.subject, "content_embeddings.json"
)

content_files = os.listdir(subject_content_dir)
content_filepaths = [
    os.path.join(subject_content_dir, content_file) for content_file in content_files
]

if os.path.exists(subject_content_emb_filepath):
    st.session_state.subject_content_emb_file_exists = True
    st.session_state.subject_content_emb = json.load(
        open(subject_content_emb_filepath, "r")
    )
else:
    st.session_state.subject_content_emb_file_exists = False
    st.session_state.subject_content_emb = {}

if st.session_state.subject_content_emb_file_exists:
    st.write("Content Embeddings Exist")
else:
    st.write("Content Embeddings Do Not Exist")

st.write("Existing Content Files:")
st.write(content_files)

st.button(
    "Create Content Embeddings"
    if not st.session_state.subject_content_emb_file_exists
    else "Update Content Embeddings",
    key="create_content_embeddings",
)

if st.session_state["create_content_embeddings"]:
    inter_cont_progress_bar = st.progress(0, text="Content Files")
    intra_cont_progress_bar = st.progress(0, text="Pages")
    st.session_state.subject_content_emb = create_content_embeddings(
        subject_content_dir,
        inter_cont_progress_bar=inter_cont_progress_bar,
        intra_cont_progress_bar=intra_cont_progress_bar,
    )

    st.session_state.subject_content_emb_file_exists = True
    with open(subject_content_emb_filepath, "w") as f:
        json.dump(st.session_state.subject_content_emb, f)

    st.experimental_rerun()
