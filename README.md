# Sensai Research Repository

## Installation
```bash
pip install -r requirements.txt
```

## Usage

### Start Streamlit App
```bash
cd streamlit-app
streamlit run subject_setup.py
```

### Subject Setup
1. Create subject folder under ```/data/subjects``` folder
2. Create content folder and keep PDFs in it
3. Create ```topics.json``` file in subject folder and add topics
4. Go into subject setup page
5. Select Subject and Topic
6. Generate Concept Hierarchy if not present
7. Generate Learning Outcomes if not present

### Assessment
1. First go to subject setup page and select subject and topic
2. Then go to either summative or formative assessment page
3. Choose learning outcome and start assessment