def fio_comparsion(author: dict, other: list) -> bool:
    if (
        author["lastname"] != other[0].text
        or author["firstname"] != other[1].text
        or author["surname"] != other[2].text
    ):
        return False
    else:
        return True
