import glob
import json
import pandas as pd
import streamlit as st

from models import Item
from models import Sentiment
from random import shuffle
from style import get_html_items

brands_names = []
for filename in glob.glob("data/*.json"):
    brand_name = filename.rsplit("/", 1)[-1].split(".")[0]
    brands_names.append(brand_name)

brands = st.multiselect('Брэнды', brands_names, "SHEIN")

data = []
for brand in brands:
    clusters = json.load(open(f"data/{brand}.json", "r"))["clusters"]
    for cluster in clusters:
        for review in cluster["reviews"]:
            data.append([cluster["name"], review["text"], review["score"], review["highlight"], review["sentiment"]])

df = pd.DataFrame(columns=["cluster", "text", "score", "highlight", "sentiment"], data=data)
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
        for _, _, score, highlight, sentiment in df_copy.loc[ids].values[:k]:
            yield Item(highlight, score / max_score / 2, sentiment)


positive_highlights = list(get_top_k_by_sentiment(sentiment="positive", k=4))
negative_highlights = list(get_top_k_by_sentiment(sentiment="negative", k=2))

highlights = positive_highlights + negative_highlights
shuffle(highlights)

st.markdown("#### Хайлайты")

st.markdown(get_html_items(highlights), unsafe_allow_html=True)
