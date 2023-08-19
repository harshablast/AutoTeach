from dotenv import load_dotenv

load_dotenv()

import json
import openai

from .prompts import (
    learning_outcomes_prompt,
    learning_outcomes_parse_prompt,
    learning_outcomes_stages_prompt,
    learning_outcomes_stages_parse_prompt,
)
from .utils import convert_graph_to_text


def create_learning_outcomes(subject, topic, concept_hierarchy_graph, temperature=0.6):
    concept_hierarchy_text = convert_graph_to_text(concept_hierarchy_graph)

    learning_outcomes_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": learning_outcomes_prompt.format(
                    subject=subject,
                    topic=topic,
                    concept_hierarchy=concept_hierarchy_text,
                ),
            },
        ],
        temperature=temperature,
    )

    learning_outcomes = learning_outcomes_response["choices"][0]["message"]["content"]

    learning_outcomes_parse_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": learning_outcomes_parse_prompt.format(
                    learning_outcomes=learning_outcomes
                ),
            },
        ],
        temperature=0,
    )

    learning_outcomes_parsed = learning_outcomes_parse_response["choices"][0][
        "message"
    ]["content"]
    learning_outcomes_parsed = json.loads(learning_outcomes_parsed)

    return learning_outcomes_parsed


def create_learning_outcomes_stages(
    subject, topic, concept_hierarchy_graph, temperature=0.6
):
    concept_hierarchy_text = convert_graph_to_text(concept_hierarchy_graph)

    learning_outcomes_stages_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": learning_outcomes_stages_prompt.format(
                    subject=subject,
                    topic=topic,
                    concept_hierarchy=concept_hierarchy_text,
                ),
            },
        ],
        temperature=temperature,
    )

    learning_outcomes_stages = learning_outcomes_stages_response["choices"][0][
        "message"
    ]["content"]

    learning_outcomes_stages_parse_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": learning_outcomes_stages_parse_prompt.format(
                    learning_outcomes_stages=learning_outcomes_stages
                ),
            },
        ],
        temperature=0,
    )

    learning_outcomes_stages_parsed = learning_outcomes_stages_parse_response[
        "choices"
    ][0]["message"]["content"]

    learning_outcomes_stages_parsed = json.loads(learning_outcomes_stages_parsed)

    return learning_outcomes_stages_parsed
