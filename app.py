import glob
import json
import pandas as pd
import streamlit as st

from models import Item
from models import Sentiment
from random import shuffle
from style import get_html_items
from annotated_text import annotated_text
from utils import iob1_tags_to_spans

brands_names = []
for filename in glob.glob("data/*.json"):
    brand_name = filename.rsplit("/", 1)[-1].split(".")[0].split("-")[1]
    brands_names.append(brand_name)

brands = st.multiselect('Брэнды', brands_names, "Amway")

data = []
for brand in brands:
    clusters = json.load(open(f"data/brand-{brand}-cluster.json", "r"))["clusters"]
    for cluster in clusters:
        for review in cluster["reviews"]:
            data.append([cluster["name"], review["id"], review["score"], review["highlight"], review["sentiment"],
                         review["tokens"], review["tags"]])

df = pd.DataFrame(columns=["cluster", "id", "score", "highlight", "sentiment", "tokens", "tags"], data=data)
categories = df["cluster"].unique()
clusters = st.multiselect("Категории хайлайтов", categories, default=categories)


def get_top_k_by_sentiment(sentiment: Sentiment, k: int):
    df_copy = df.copy()
    df_copy = df_copy[
        (df_copy["sentiment"] == sentiment) &
        (df_copy["cluster"].isin(clusters))
        ]
    max_score = df_copy["score"].max()
    for _, ids in df_copy.groupby("cluster").groups.items():
        for _, id, score, highlight, sentiment, tokens, tags in df_copy.loc[ids].values[:k]:
            yield Item(highlight, score / max_score / 2, sentiment)


positive_highlights = list(get_top_k_by_sentiment(sentiment="positive", k=4))
negative_highlights = list(get_top_k_by_sentiment(sentiment="negative", k=2))

highlights = positive_highlights + negative_highlights
shuffle(highlights)

st.markdown("#### Хайлайты")
st.markdown(get_html_items(highlights), unsafe_allow_html=True)

st.markdown("#### Отзывы")


def get_top_k_by_sentiment(sentiment: Sentiment, k: int):
    df_copy = df.copy()
    df_copy = df_copy[
        (df_copy["sentiment"] == sentiment) &
        (df_copy["cluster"].isin(clusters))
    ]
    for _, ids in df_copy.groupby("cluster").groups.items():
        for _, id, score, highlight, sentiment, tokens, tags in df_copy.loc[ids].values[:k]:
            color_mapping = {
                "P": "rgba(52, 199, 89, 0.2)",
                "N": "rgba(255, 59, 48, 0.2)"
            }
            new_tokens = []
            new_tags = []
            indices = iob1_tags_to_spans(tags)
            indices = sorted(indices, key=lambda x: x[1][0])
            prev = 0
            for tag, (start, stop) in indices:
                if prev != start:
                    new_tokens.append(" ".join(tokens[prev:start]))
                    new_tags.append("O")
                new_tokens.append(" ".join(tokens[start: stop + 1]))
                new_tags.append(tag)
                prev = stop + 1
            if prev != len(tokens):
                new_tokens.append(" ".join(tokens[prev:]))
                new_tags.append("O")

            highlights = list(zip(new_tokens, new_tags))
            parts = [(token + " ", tag, color_mapping[tag]) if tag != "O" else (token) for token, tag in highlights]
            annotated_text(*parts)
            st.markdown("")
            st.markdown("")


get_top_k_by_sentiment("positive", 4)
get_top_k_by_sentiment("negative", 2)