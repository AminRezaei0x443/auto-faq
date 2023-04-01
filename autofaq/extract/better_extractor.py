from bs4 import BeautifulSoup
from bs4.element import Comment

from autofaq.extract.extractor import BaseExtractor


class BetterExtractor(BaseExtractor):
    def extract(self, content: str) -> list[dict]:
        qa = self.retreive_qa(content)
        return [{"q": q, "a": " ".join(a)} for q, a in qa]

    def parent_sig(self, p):
        tags = []
        t = p
        while t is not None:
            tags.insert(0, t.name)
            t = t.parent
        cls = "|".join(sorted(p.attrs.get("class", [])))
        hi = ">".join(tags)
        return hi + "+" + cls

    def tag_visible(self, element):
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

    def text_from_html(self, body):
        soup = BeautifulSoup(body, "html.parser")
        soup = soup.find("body")
        texts = soup.findAll(text=True)
        visible_texts = filter(self.tag_visible, texts)
        r = [(t.strip(), self.parent_sig(t.parent)) for t in visible_texts]
        return list(filter(lambda x: x[0] != "", r))

    def is_question(self, sentence: str) -> bool:
        # This supports persian and english questions
        # TODO: extend it to much better one
        return sentence.strip().endswith("؟") or sentence.strip().endswith("?")

    def retreive_qa(self, html_content):
        q_list = self.text_from_html(html_content)
        questions = list(filter(lambda t: self.is_question(t[0]), q_list))
        sigs = list(map(lambda t: t[1], questions))
        cd = {k: sigs.count(k) for k in set(sigs)}

        if len(cd) == 0:
            return []

        prob_faq = max(cd.values()) / len(sigs)

        if prob_faq < 0.3:
            return []

        da_sig = max(cd, key=cd.get)
        marker = list(map(lambda t: t[1] == da_sig, q_list))
        index = (
            len(marker) - marker[-1::-1].index(True) - 1
        )  # What the hell is even this? TODO: better solution
        q_list = q_list[:index]

        stack = []
        cache = []
        current = None
        for s, id_ in q_list:
            if self.is_question(s) and id_ == da_sig:
                if current:
                    stack.append((current[0], cache))
                    cache = []
                current = s, id_
            else:
                if current:
                    cache.append(s)
        return stack
