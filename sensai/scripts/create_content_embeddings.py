from dotenv import load_dotenv

load_dotenv()

import os
import sys

from openai import OpenAI
from pypdf import PdfReader
from tqdm import tqdm

client = OpenAI()
import json


def embed_content(content_filepath, intra_cont_progress_bar=None):
    if content_filepath.endswith(".pdf"):
        reader = PdfReader(content_filepath)
    else:
        print("Invalid Filetype")
        return None

    num_pages = len(reader.pages)

    content_embeddings = []

    for page_idx, page in enumerate(tqdm(reader.pages)):
        page_text = page.extract_text()
        if len(page_text) < 25:
            continue
        page_embedding = client.embeddings.create(
            input=[page_text], model="text-embedding-ada-002"
        )["data"][0]["embedding"]
        content_embeddings.append(
            {
                "source_content_filepath": content_filepath,
                "page_idx": page_idx,
                "page_text": page_text,
                "page_embedding": page_embedding,
            }
        )
        if intra_cont_progress_bar is not None:
            intra_cont_progress_bar.progress(
                int(100 * (page_idx + 1) / num_pages),
                text=f"Pages ({page_idx+1}/{num_pages})",
            )

    return content_embeddings


def create_content_embeddings(
    content_dir, inter_cont_progress_bar=None, intra_cont_progress_bar=None
):
    content_files = [
        os.path.join(content_dir, filename)
        for filename in os.listdir(content_dir)
        if filename.endswith(".pdf")
    ]

    content_embeddings = []

    for idx, content_file in enumerate(content_files):
        print(f"Embedding {content_file} ({idx+1}/{len(content_files)})")
        if inter_cont_progress_bar is not None:
            inter_cont_progress_bar.progress(
                int(100 * (idx + 1) / len(content_files)),
                text=f"Content Files ({idx+1}/{len(content_files)})",
            )
        content_embeddings += embed_content(content_file, intra_cont_progress_bar)

    return content_embeddings


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a content directory")
        sys.exit(1)

    content_dir = sys.argv[1]
    subject_dir = os.path.dirname(content_dir)
    content_embeddings_filepath = os.path.join(subject_dir, "content_embeddings.json")
    content_embeddings = create_content_embeddings(content_dir)

    with open(content_embeddings_filepath, "w") as f:
        json.dump(content_embeddings, f)
