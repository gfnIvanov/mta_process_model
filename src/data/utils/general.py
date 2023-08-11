import os
import re
import yaml
from typing import Any, Union
from pathlib import Path
from xml.etree.ElementTree import Element
from .types import FioFields, opt_str


def fio_comparsion(author: FioFields, other: Element) -> bool:
    """
    Full name match check

    Arguments:
    author: FioFields - author full name
    other: Element - fields that are checked for a match
    """
    if (
        author.lastname != other[0].text
        or author.firstname != other[1].text
        or author.surname != other[2].text
    ):
        return False
    else:
        return True


def get_sentences(text: str, sent_len: int, simple: bool = False) -> list[str]:
    """
    Dividing text into sentences

    Arguments:
    text: str - text
    sent_len: int - sentence length
    simple: bool = False - if True then do not clean up the text
    """
    text_arr = text.split(" ")
    sent = ""
    sentences = []

    def clean_symb(for_clean_str: str) -> str:
        for_clean_str = re.sub(r"\s+", " ", for_clean_str)
        for_clean_str = re.sub(r"_+", "", for_clean_str)
        return for_clean_str.replace("\n", " ").replace("&quot;", "")

    if len(text) <= sent_len:
        return [clean_symb(text)]

    for i, part in enumerate(text_arr):
        if len(sent) == 0:
            sent += part
        elif len(sent + " " + part) <= sent_len:
            sent = sent + " " + part
        else:
            sentences.append(sent if simple else clean_symb(sent))
            sent = part

        if i == len(text_arr) - 1 and sent != "":
            sentences.append(sent if simple else clean_symb(sent))

    sentences = list(filter(lambda x: len(re.findall(r"\S", x)) > 0, sentences))

    return sentences


def clean_with_regexp(
    for_regexp: Union[list[str], list[opt_str]], text: str
) -> tuple[str, list[str]]:
    """
    Finding and removing personal data from offers using regexp

    Arguments:
    for_regexp: Union[list[str], list[opt_str]] - list of expressions to match
    text: str - text
    """
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
    """
    Saving the yaml-file to a local directory

    Arguments:
    data: Any - object to store
    path: Path - path to local directory
    file_name: str - file name
    dump_all: bool = False - if True then save multiple files into one
    """
    with open(os.path.join(path, file_name), "a") as new_file:
        if dump_all:
            yaml.dump_all(data, new_file, encoding="utf-8", allow_unicode=True)
            return
        yaml.dump(data, new_file, encoding="utf-8", allow_unicode=True)


def count_files_in_yaml(file_path: Path) -> int:
    """
    Counting files in yaml file

    Arguments:
    file_path: Path - path to yaml-file
    """
    filescount = 0

    with open(file_path, "r") as file:
        count_int_files = yaml.load_all(file, Loader=yaml.Loader)

        for _ in count_int_files:
            filescount += 1

    return filescount
