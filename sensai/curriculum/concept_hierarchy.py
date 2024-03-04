import json
import re

from dotenv import load_dotenv

load_dotenv()

import numpy as np
from openai import OpenAI

from .prompts import (concept_hierarchy_parse_prompt,
                      concept_hierarchy_refine_content_prompt,
                      concept_hierarchy_refine_prompt,
                      concept_hierarchy_starter_prompt, system_prompt,
                      topic_summary_prompt)
from .utils import convert_linear_to_graph

client = OpenAI()
import tiktoken
from tqdm import tqdm


def create_concept_hierarchy(
    subject,
    topic,
    content_embeddings=None,
    temperature=0.6,
    refine_steps=5,
    verbose=True,
    progress_bar=None,
):
    starter_messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": concept_hierarchy_starter_prompt.format(
                subject=subject, topic=topic
            ),
        },
    ]

    starter_response = client.chat.completions.create(
        model="gpt-4", messages=starter_messages, temperature=temperature
    )

    concept_hierarchy = starter_response.choices[0].message.content
    if verbose:
        print(f"Initial Concept Hierarchy:\n\n{concept_hierarchy}")
    if progress_bar is not None:
        progress = int(100 * (1 / (refine_steps + 1)))
        progress_bar.progress(
            progress,
            text="Creating Concept Hierarchy Graph... Stage: Initial Concept Hierarchy",
        )

    if content_embeddings is not None:
        topic_summary_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": topic_summary_prompt.format(
                        subject=subject, topic=topic
                    ),
                }
            ],
            temperature=0,
        )
        topic_summary = topic_summary_response.choices[0].message.content
        query_embedding = client.embeddings.create(
            input=[topic_summary], model="text-embedding-ada-002"
        )["data"][0]["embedding"]
        content_embedding_vectors = [
            content_emb_dict["page_embedding"]
            for content_emb_dict in content_embeddings
        ]
        cosine_sims = np.dot(content_embedding_vectors, query_embedding)
        top_indices = np.argsort(cosine_sims)[::-1]

        encoding = tiktoken.get_encoding("cl100k_base")
        content_done = False
        curr_content_text = ""
        curr_content_tokens = 0
        content_chunks = []
        curr_content_idx = 0

        while not content_done:
            next_content_text = content_embeddings[top_indices[curr_content_idx]][
                "page_text"
            ]
            next_content_tokens = len(encoding.encode(next_content_text))

            if (curr_content_tokens + next_content_tokens) > 1024:
                content_chunks.append(curr_content_text)
                if len(content_chunks) >= refine_steps:
                    content_done = True
                    break
                curr_content_text = next_content_text
                curr_content_tokens = next_content_tokens
            else:
                curr_content_text += "\n" + next_content_text
                curr_content_tokens += next_content_tokens

            curr_content_idx += 1
            if curr_content_idx >= len(content_embeddings):
                content_done = True
                break

        for chunk_idx, content_chunk in enumerate(
            tqdm(content_chunks, desc="Refining the Concept Hierarchy (content)...")
        ):
            response = client.chat.completions.create(
                model="gpt-4",
                messages=starter_messages
                + [
                    {
                        "role": "user",
                        "content": concept_hierarchy_refine_content_prompt.format(
                            content=content_chunk,
                            concept_hierarchy=concept_hierarchy,
                            subject=subject,
                            topic=topic,
                        ),
                    }
                ],
                temperature=temperature,
            )

            concept_hierarchy = response.choices[0].message.content
            if verbose:
                print(
                    f"Refine Step (content): {chunk_idx}\nConcept Hierarchy:\n\n{concept_hierarchy}\n\nContent Provided:\n\n{content_chunk}"
                )
            if progress_bar is not None:
                progress = int(100 * (chunk_idx + 2) / (refine_steps + 1))
                progress_bar.progress(
                    progress,
                    text="Creating Concept Hierarchy Graph... Stage: Refining the Concept Hierarchy (content)",
                )

    else:
        for refine_idx in tqdm(
            range(refine_steps), desc="Refining the Concept Hierarchy..."
        ):
            response = client.chat.completions.create(
                model="gpt-4",
                messages=starter_messages
                + [
                    {"role": "assistant", "content": concept_hierarchy},
                    {"role": "user", "content": concept_hierarchy_refine_prompt},
                ],
                temperature=temperature,
            )

            concept_hierarchy = response.choices[0].message.content
            if verbose:
                print(
                    f"Refine Step: {refine_idx}\nConcept Hierarchy:\n\n{concept_hierarchy}"
                )

    parsed_response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
                "role": "user",
                "content": concept_hierarchy_parse_prompt.format(
                    concept_hierarchy=concept_hierarchy
                ),
            }
        ],
        temperature=0,
    )

    concept_hierarchy_linear_str = parsed_response.choices[0].message.content
    concept_hierarchy_linear = json.loads(concept_hierarchy_linear_str)
    concept_hierarchy_graph = convert_linear_to_graph(concept_hierarchy_linear)

    for edge in concept_hierarchy_graph["edges"]:
        res = re.findall(r"\(.*?\)", edge["source"])
        if len(res) > 0:
            edge["source"] = res[0][1:-1]

    return concept_hierarchy_graph
