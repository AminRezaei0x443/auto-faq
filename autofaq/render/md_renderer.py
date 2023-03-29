from autofaq.render.renderer import BaseRenderer


class MarkdownRenderer(BaseRenderer):
    def render(self, data: list[dict], out: str):
        document = []
        for page in data:
            title = page["title"]
            document.append(f"### {title}")
            for pair in page["pairs"]:
                q = pair["q"]
                a = pair["a"]
                aux_data = pair["aux"]
                aux_data["tag"] = page["query"]

                document.append(f"#### {q}")
                document.append(a)
                aux_data = {
                    k: v if not isinstance(v, float) else f"{v:.2f}"
                    for k, v in aux_data.items()
                }
                aux_data = ", ".join(f"{k}={v}" for k, v in aux_data.items())
                if aux_data.strip() != "":
                    document.append(f"\n```{aux_data}```")

        doc = "\n".join(document)
        pt = f"{out}.md"
        with open(pt, "w") as f:
            f.write(doc)
        return pt
