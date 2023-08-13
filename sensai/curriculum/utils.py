import networkx as nx
import numpy as np
import openai


def get_best_matches(content_embeddings, query_text, top_k):
    query_embedding = openai.Embedding.create(
        input=[query_text], model="text-embedding-ada-002"
    )["data"][0]["embedding"]
    content_embedding_vectors = [
        content_emb_dict["page_embedding"] for content_emb_dict in content_embeddings
    ]

    cosine_sims = np.dot(content_embedding_vectors, query_embedding)
    top_k_indices = np.argsort(cosine_sims)[-top_k:]

    top_k_pages = []

    for idx in top_k_indices:
        top_k_pages.append(content_embeddings[idx]["page_text"])

    return top_k_pages


def convert_linear_to_graph(concept_hierarchy_linear):
    concept_hierarchy_graph = {
        "nodes": [],
        "edges": [],
    }

    for concept in concept_hierarchy_linear:
        concept_id = concept["concept_id"]
        features = concept["distinctive_features"]
        parent_concept_id = concept["common_concept"]

        concept_hierarchy_graph["nodes"].append(
            {"id": concept_id, "name": concept["concept_name"], "type": "concept"}
        )

        for feature_idx, feature in enumerate(features):
            feature_id = concept_id + "_F_" + format(feature_idx, "02d")
            concept_hierarchy_graph["nodes"].append(
                {"id": feature_id, "name": feature, "type": "feature"}
            )
            concept_hierarchy_graph["edges"].append(
                {"source": concept_id, "target": feature_id, "type": "feature"}
            )

        if parent_concept_id.lower() not in ["none", "n/a", "na"]:
            concept_hierarchy_graph["edges"].append(
                {"source": parent_concept_id, "target": concept_id, "type": "concept"}
            )

    return concept_hierarchy_graph


def convert_graph_to_text(concept_hierarchy_graph):
    G = nx.DiGraph()
    node_text_map = {}
    concept_hierarchy_text = ""

    for node in concept_hierarchy_graph["nodes"]:
        if node["type"] != "concept":
            continue
        feature_ids = [
            edge["target"]
            for edge in list(
                filter(
                    lambda edge: edge["source"] == node["id"]
                    and edge["type"] == "feature",
                    concept_hierarchy_graph["edges"],
                )
            )
        ]
        node_text = (
            "Concept ID: "
            + node["id"]
            + "\nConcept Name: "
            + node["name"]
            + "\nConcept Features:"
        )
        for feature_id in feature_ids:
            node_text += (
                "\n- "
                + list(
                    filter(
                        lambda node: node["id"] == feature_id,
                        concept_hierarchy_graph["nodes"],
                    )
                )[0]["name"]
            )
        node_text_map[node["id"]] = node_text
        G.add_node(node_text)

    for edge in concept_hierarchy_graph["edges"]:
        if edge["type"] != "concept":
            continue
        G.add_edge(node_text_map[edge["source"]], node_text_map[edge["target"]])

    root_nodes = [node[0] for node in list(G.in_degree()) if node[1] == 0]

    for node_text in list(nx.generate_network_text(G, sources=root_nodes)):
        node_text = node_text.replace("│", " ")
        node_text = node_text.replace("╙", " ")
        node_text = node_text.replace("├", " ")
        node_text = node_text.replace("└", " ")
        node_text = node_text.replace("──", " ")
        node_text = node_text.replace("─╼", " ")

        indent_level = (len(node_text) - len(node_text.lstrip())) // 4

        for line_idx, line in enumerate(node_text.split("\n")):
            if line_idx <= 0:
                concept_hierarchy_text += (
                    "\n" + "\t" * indent_level + "-- " + line.strip()
                )
            else:
                concept_hierarchy_text += "\n" + "\t" * indent_level + line.strip()

    return concept_hierarchy_text
