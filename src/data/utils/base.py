from xml.etree.ElementTree import Element
from .types import FioFields


def fio_comparsion(author: FioFields, other: Element) -> bool:
    if (
        author.lastname != other[0].text
        or author.firstname != other[1].text
        or author.surname != other[2].text
    ):
        return False
    else:
        return True
