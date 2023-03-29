from hashlib import sha256


def sha256id(i: str | bytes):
    if isinstance(i, str):
        i = i.encode("utf-8")
    return sha256(i).hexdigest()
