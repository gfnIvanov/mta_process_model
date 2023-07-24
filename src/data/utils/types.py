from dataclasses import dataclass, field
from typing import Literal, Union, Optional


opt_str = Union[str, None]

str_dict = dict[str, str]

fio_fields = dict[Literal["firstname", "surname", "lastname"], opt_str]


@dataclass
class FioFields:
    firstname: opt_str = ""
    surname: opt_str = ""
    lastname: opt_str = ""


@dataclass
class FileFields:
    patient: FioFields = field(default_factory=FioFields)
    author: FioFields = field(default_factory=FioFields)
    code: opt_str = ""
    text: opt_str = ""
    authentif: Optional[FioFields] = None
    docof: Optional[FioFields] = None


@dataclass
class InterimData:
    file: FileFields = field(default_factory=FileFields)
