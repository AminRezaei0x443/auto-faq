import urllib.request

from bs4 import BeautifulSoup
from bs4.element import Comment


def tag_visible(element):
    if element.parent.name in [
        "style",
        "script",
        "head",
        "title",
        "meta",
        "[document]",
    ]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, "html.parser")
    soup = soup.find("body")
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    r = [t.strip() for t in visible_texts]
    return list(filter(lambda x: x != "", r))


def is_question(sentence: str) -> bool:
    return sentence.strip().endswith("؟")


def retreive_qa(html_content):
    q_list = text_from_html(html_content)
    stack = []
    cache = []
    current = None
    for s in q_list:
        if is_question(s):
            if current:
                stack.append((current, cache))
                cache = []
            current = s
        else:
            if current:
                cache.append(s)
    return stack
