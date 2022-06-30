import glob
import jsonlines
import streamlit as st


from typing import *
from annotated_text import annotated_text


datasets = glob.glob("data/processed/*")

option = st.selectbox('Choose dataset to overview', datasets)

st.markdown('------', unsafe_allow_html=False)

MAX_LINES = 50


@st.cache
def get_contigous(tokens: List, active_elements: List):
    """
    Given list of elements, find all contigous 
    parts of active_element
    1 0 0 1 1 1 -> (0, 0), (3, 5)
    """
    parts = []
    start = None
    for i, (token, tag) in enumerate(tokens):
        if tag in active_elements:
            if start == None:
                start = i
            else:
                # To check for contigous tokens that are in active_elements
                # for example if active_elements = [1, 2]
                # then we need to check for 1 1 2 1
                # and do not select 0-4
                # but 0-2 3-3 4-4
                if tokens[start][1] != tag:
                    parts.append([start, i - 1])
                    start = None
        else:
            if start != None:
                parts.append([start, i - 1])
                start = None
    if start != None:
        parts.append([start, i])
    return parts


with jsonlines.open(option, 'r') as file:
    for i, line in enumerate(file):
        if i > MAX_LINES:
            break
        highlights = list(zip(line['tokens'], line['tags']))
        # tuple does not support item assignment
        # add extra sapce after each token to add line breaks
        highlights = [[token + ' ', tag] for token, tag in highlights]
        # Unite B-P with I-P to Positive class and B-N with I-N to Negative class
        for i, (token, tag) in enumerate(highlights):
            if tag != 'O':
                _, _class = tag.split('-')
                if _class == 'P':
                    highlights[i][1] = 'Positive'
                elif _class == 'N':
                    highlights[i][1] = 'Negative'

        # do not highlight O tags
        contigous = get_contigous(highlights, ['Positive', 'Negative'])

        parts = []
        if contigous:
            prev = 0
            for start, end in contigous:
                end = end + 1
                if prev != start:
                    parts.append([''.join([token for token, _ in highlights[prev:start]]), 'O'])
                # All tokens in contigous must have the same tag so can take any
                parts.append([' '.join([token for token, _ in highlights[start:end]]), highlights[start][1]])
                prev = end
            parts.append([''.join([token for token, _ in highlights[end:]]), 'O'])
        else:
            parts.append([''.join([token for token, _ in highlights[:]]), 'O'])

        parts = [(token, tag) if tag != 'O' else (token) for token, tag in parts]


        annotated_text(*parts)

        st.markdown('------', unsafe_allow_html=False)