from models import Item
from typing import List


def get_css_red(opacity: float):
    return f"rgba(255, 59, 48, {opacity}"


def get_css_green(opacity: float):
    return f"rgba(52, 199, 89, {opacity}"


def get_html_item(item: Item):
    get_color = get_css_green if item.sentiment == "positive" else get_css_red
    return f"""<p style='background-color: {get_color(item.opacity)}); border-radius: 8px; 
    padding: 3px 5px 3px 5px; font-size: 14px; margin: 0px'>{item.text}</p> """


def get_html_items(items: List[Item]):
    return f"""
    <div style='display: flex; flex-direction: row; gap: 10px; flex-flow: wrap;'>
        {" ".join([get_html_item(item) for item in items])}
    </div>
    """
