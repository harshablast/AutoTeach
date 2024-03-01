import os
import json
from abc import (
    ABC,
    abstractmethod,
)
from typing import Any

from openai import OpenAI
from langchain import PromptTemplate

from .prompts import (
    summative_assessment_start_prompt,
    summative_assessment_evaluation_prompt,
    summative_assessment_evaluation_parse_prompt,
    formative_assessment_start_prompt,
    formative_assessment_evaluation_prompt,
    formative_assessment_evaluation_parse_prompt,
    assessment_system_prompt,
)

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


class SensaiAssessment(ABC):
    def __init__(self, subject, topic, learning_outcome, concept_hierarchy_graph):
        self.subject = subject
        self.topic = topic
        self.learning_outcome = learning_outcome
        self.concept_hierarchy_graph = concept_hierarchy_graph

        self.concept_nodes = self.get_concept_nodes()
        self.concept_nodes_text = self.get_concept_nodes_text(self.concept_nodes)
        self.user_state_text = self.get_user_state_text(self.concept_nodes)

    def get_concept_nodes(self):
        concept_ids = self.learning_outcome["concept_ids"]
        concept_nodes = list(
            filter(
                lambda node: node["id"] in concept_ids,
                self.concept_hierarchy_graph["nodes"],
            )
        )

        for concept_node in concept_nodes:
            feature_ids = [
                edge_d["target"]
                for edge_d in list(
                    filter(
                        lambda edge: edge["source"] == concept_node["id"]
                        and edge["type"] == "feature",
                        self.concept_hierarchy_graph["edges"],
                    )
                )
            ]
            feature_nodes = list(
                filter(
                    lambda node: node["id"] in feature_ids,
                    self.concept_hierarchy_graph["nodes"],
                )
            )

            concept_node["feature_nodes"] = feature_nodes

        return concept_nodes

    def get_concept_nodes_text(self, concept_nodes):
        concept_nodes_text = ""

        for concept_node in concept_nodes:
            concept_nodes_text += f"Concept ID: {concept_node['id']}\n"
            concept_nodes_text += f"Concept: {concept_node['name']}\n"
            for feature_node in concept_node["feature_nodes"]:
                concept_nodes_text += (
                    f"\t{feature_node['id']} - {feature_node['name']}\n"
                )
            concept_nodes_text += "\n"

        return concept_nodes_text

    def get_user_state_text(self, concept_nodes):
        user_state_text = ""

        for concept_node in concept_nodes:
            user_state_text += f"Concept ID: {concept_node['id']}\n"
            user_state_text += f"Concept: {concept_node['name']}\n"
            for feature_node in concept_node["feature_nodes"]:
                user_state_text += f"\t{feature_node['id']} - None\n"
            user_state_text += "\n"

        return user_state_text

    def __call__(self, assessment_messages=None):
        if assessment_messages is None:
            assessment_messages = self.start_assessment()
            end_assessment = False
        else:
            assessment_messages = self.handle_user_answer(assessment_messages)
            end_assessment = self.end_assessment(assessment_messages[-1])

        return assessment_messages, end_assessment

    @abstractmethod
    def start_assessment(self):
        pass

    @abstractmethod
    def handle_user_answer(self, assessment_messages):
        pass

    @abstractmethod
    def end_assessment(self):
        pass

    @abstractmethod
    def evaluate_assessment(self, assessment_messages):
        pass


class SummativeAssessment(SensaiAssessment):
    def __init__(self, subject, topic, learning_outcome, concept_hierarchy_graph):
        super().__init__(subject, topic, learning_outcome, concept_hierarchy_graph)

    def start_assessment(self):
        assessment_messages = [
            {"role": "system", "content": assessment_system_prompt},
            {
                "role": "user",
                "content": summative_assessment_start_prompt.format(
                    subject=self.subject,
                    topic=self.topic,
                    learning_outcome=self.learning_outcome["learning_outcome"],
                    concepts=self.concept_nodes_text,
                ),
            },
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=assessment_messages,
        )

        response_message = response["choices"][0]["message"]
        assessment_messages.append(response_message)

        return assessment_messages

    def handle_user_answer(self, assessment_messages):
        print(assessment_messages)
        assessment_messages[-1]["content"] = (
            "User Answer: " + assessment_messages[-1]["content"]
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=assessment_messages,
        )
        response_message = response["choices"][0]["message"]
        assessment_messages.append(response_message)

        return assessment_messages

    def end_assessment(self, response_message):
        return "[END]" in response_message["content"]

    def evaluate_assessment(self, assessment_messages):
        assessment_messages.append(
            {
                "role": "user",
                "content": summative_assessment_evaluation_prompt.format(
                    concepts=self.concept_nodes_text, user_state=self.user_state_text
                ),
            }
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=assessment_messages,
        )

        response_text = response["choices"][0]["message"]["content"]
        eval_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": summative_assessment_evaluation_parse_prompt.format(
                        assessment_evaluation=response_text
                    ),
                }
            ],
        )
        eval_text = eval_response["choices"][0]["message"]["content"]
        eval = json.loads(eval_text)

        return eval


class FormativeAssessment(SensaiAssessment):
    def __init__(self, subject, topic, learning_outcome, concept_hierarchy_graph):
        super().__init__(subject, topic, learning_outcome, concept_hierarchy_graph)

    def start_assessment(self):
        assessment_messages = [
            {"role": "system", "content": assessment_system_prompt},
            {
                "role": "user",
                "content": formative_assessment_start_prompt.format(
                    subject=self.subject,
                    topic=self.topic,
                    learning_outcome=self.learning_outcome["learning_outcome"],
                    concepts=self.concept_nodes_text,
                ),
            },
        ]
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=assessment_messages,
        )

        # response_message = response["choices"][0]["message"]
        response_message = response.choices[0].message
        assessment_messages.append(response_message)

        return assessment_messages

    def handle_user_answer(self, assessment_messages):
        print(assessment_messages)
        assessment_messages[-1]["content"] = (
            "User Answer: " + assessment_messages[-1]["content"]
        )
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=assessment_messages,
        )
        # response_message = response["choices"][0]["message"]
        response_message = response.choices[0].message
        assessment_messages.append(response_message)

        return assessment_messages

    def end_assessment(self, response_message):
        return "[END]" in response_message.content

    def evaluate_assessment(self, assessment_messages):
        assessment_messages.append(
            {
                "role": "user",
                "content": formative_assessment_evaluation_prompt.format(
                    concepts=self.concept_nodes_text, user_state=self.user_state_text
                ),
            }
        )

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=assessment_messages,
        )

        # response_text = response["choices"][0]["message"]["content"]
        response_text = response.choices[0].message.content
        eval_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": formative_assessment_evaluation_parse_prompt.format(
                        assessment_evaluation=response_text
                    ),
                }
            ],
        )
        # eval_text = eval_response["choices"][0]["message"]["content"]
        eval_text = eval_response.choices[0].message
        eval = json.loads(eval_text)

        return eval
