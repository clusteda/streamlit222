from enum import Enum
from dataclasses import dataclass


class Sentiment(Enum):
    positive = "positive"
    negative = "negative"


@dataclass
class Item:
    text: str
    opacity: float
    sentiment: Sentiment
