import urllib.request

from bs4 import BeautifulSoup
from bs4.element import Comment


def parent_sig(p):
    tags = []
    t = p
    while t is not None:
        tags.insert(0, t.name)
        t = t.parent
    cls = "|".join(sorted(p.attrs.get("class", [])))
    hi = ">".join(tags)
    return hi + "+" + cls


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
    r = [(t.strip(), parent_sig(t.parent)) for t in visible_texts]
    return list(filter(lambda x: x[0] != "", r))


def is_question(sentence: str) -> bool:
    return sentence.strip().endswith("؟")


def retreive_qa(html_content):
    q_list = text_from_html(html_content)
    stack = []
    cache = []
    current = None
    last = None
    for s, id_ in q_list:
        if is_question(s):
            if current:
                stack.append((current[0], cache))
                cache = []
                last = None
            current = s, id_
        else:
            if current:
                if last is None or last == id_:
                    cache.append(s)
                    last = id_
    return stack
