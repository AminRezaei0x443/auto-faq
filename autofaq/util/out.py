import re

from click import echo, style


def sprint(msg, fg=None, **kwargs):
    # Structure -> Here is message @msg_number
    pattern = "(@[A-Za-z0-9_]+)"
    msg_split = re.split(pattern, msg)
    styled = {}
    for k, v in kwargs.items():
        if len(v) == 3:
            value, color, st = v
            styled[f"@{k}"] = style(value, fg=color, bold=st == "bold")
        elif len(v) == 2:
            value, color = v
            styled[f"@{k}"] = style(value, fg=color)
        else:
            styled[f"@{k}"] = f"{v}"
    new_msg = []
    for m in msg_split:
        if m in styled:
            new_msg.append(styled[m])
        else:
            if fg:
                new_msg.append(style(m, fg=fg))
            else:
                new_msg.append(m)
    print("".join(new_msg))
