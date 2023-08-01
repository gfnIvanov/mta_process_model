import os
import re
import yaml
from typing import Any, Union
from pathlib import Path
from xml.etree.ElementTree import Element
from .types import FioFields, opt_str


def fio_comparsion(author: FioFields, other: Element) -> bool:
    if (
        author.lastname != other[0].text
        or author.firstname != other[1].text
        or author.surname != other[2].text
    ):
        return False
    else:
        return True


def get_sentences(text: str) -> list[str]:
    sent_len = 500
    text_arr = text.split(" ")
    sent = ""
    sentences = []

    def clean_symb(for_clean_str: str) -> str:
        return for_clean_str.replace("\n", " ").replace("&quot;", "")

    if len(text) <= sent_len:
        return [clean_symb(text)]

    for i, part in enumerate(text_arr):
        if len(sent) == 0:
            sent += part
        elif len(sent + " " + part) <= sent_len:
            sent = sent + " " + part
        else:
            sentences.append(clean_symb(sent))
            sent = part

        if i == len(text_arr) - 1 and sent != "":
            sentences.append(clean_symb(sent))

    return sentences


def clean_with_regexp(
    for_regexp: Union[list[str], list[opt_str]], text: str
) -> tuple[str, list[str]]:
    local_text = text
    deleted_data = []

    for regexp_word in for_regexp:
        if regexp_word is None:
            continue

        pattern = re.compile(regexp_word, flags=re.IGNORECASE)
        deleted_data.extend(re.findall(pattern, local_text))
        local_text = re.sub(pattern, "", local_text)

    return local_text, deleted_data


def save_yaml_file(
    data: Any, path: Path, file_name: str, dump_all: bool = False
) -> None:
    with open(os.path.join(path, file_name), "a") as new_file:
        if dump_all:
            yaml.dump_all(data, new_file, encoding="utf-8", allow_unicode=True)
            return
        yaml.dump(data, new_file, encoding="utf-8", allow_unicode=True)
