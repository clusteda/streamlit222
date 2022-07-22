import glob
import jsonlines
import streamlit as st


from typing import Optional, Tuple, List, Set

from annotated_text import annotated_text


def _iob1_start_of_chunk(
    prev_bio_tag: Optional[str],
    prev_conll_tag: Optional[str],
    curr_bio_tag: str,
    curr_conll_tag: str,
) -> bool:
    if curr_bio_tag == "B":
        return True
    if curr_bio_tag == "I" and prev_bio_tag == "O":
        return True
    if curr_bio_tag != "O" and prev_conll_tag != curr_conll_tag:
        return True
    return False


def iob1_tags_to_spans(
    tag_sequence: List[str], classes_to_ignore: List[str] = None
) -> List[str]:
    classes_to_ignore = classes_to_ignore or []
    spans: Set[Tuple[str, Tuple[int, int]]] = set()
    span_start = 0
    span_end = 0
    active_conll_tag = None
    prev_bio_tag = None
    prev_conll_tag = None
    for index, string_tag in enumerate(tag_sequence):
        curr_bio_tag = string_tag[0]
        curr_conll_tag = string_tag[2:]

        if curr_bio_tag not in ["B", "I", "O"]:
            raise ValueError("Invalid tag sequence")
        if curr_bio_tag == "O" or curr_conll_tag in classes_to_ignore:
            # The span has ended.
            if active_conll_tag is not None:
                spans.add((active_conll_tag, (span_start, span_end)))
            active_conll_tag = None
        elif _iob1_start_of_chunk(
            prev_bio_tag, prev_conll_tag, curr_bio_tag, curr_conll_tag
        ):
            # We are entering a new span; reset indices
            # and active tag to new span.
            if active_conll_tag is not None:
                spans.add((active_conll_tag, (span_start, span_end)))
            active_conll_tag = curr_conll_tag
            span_start = index
            span_end = index
        else:
            # bio_tag == "I" and curr_conll_tag == active_conll_tag
            # We're continuing a span.
            span_end += 1

        prev_bio_tag = string_tag[0]
        prev_conll_tag = string_tag[2:]
    # Last token might have been a part of a valid span.
    if active_conll_tag is not None:
        spans.add((active_conll_tag, (span_start, span_end)))
    return list(spans)


datasets = glob.glob("data/test-002-predictions.jsonl", recursive=True)

option = st.selectbox("Choose dataset to overview", datasets)

st.markdown("------", unsafe_allow_html=False)

MAX_LINES = 400

color_mapping = {
    "P": "#ccd5ae",
    "N": "#ffdcdc",
    # "O": "#edede9",
}

with jsonlines.open(option, "r") as file:
    for i, line in enumerate(file):
        if i < 10:
            continue
        if i > MAX_LINES:
            break
        new_tokens = []
        new_tags = []
        indices = iob1_tags_to_spans(line["tags"])
        indices = sorted(indices, key=lambda x: x[1][0])
        prev = 0
        for tag, (start, stop) in indices:
            if prev != start:
                new_tokens.append(" ".join(line["initial tokens"][prev:start]))
                new_tags.append("O")
            new_tokens.append(" ".join(line["initial tokens"][start : stop + 1]))
            new_tags.append(tag)
            prev = stop + 1
        if prev != len(line["initial tokens"]):
            new_tokens.append(" ".join(line["initial tokens"][prev:]))
            new_tags.append("O")

        highlights = list(zip(new_tokens, new_tags))
        parts = [
            (token + " ", tag, color_mapping[tag]) if tag != "O" else (token)
            for token, tag in highlights
        ]
        annotated_text(*parts)
        st.markdown("------", unsafe_allow_html=False)
