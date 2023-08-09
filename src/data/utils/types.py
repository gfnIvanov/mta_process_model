from dataclasses import dataclass, field
from typing import Union, Optional


opt_str = Union[str, None]

str_dict = dict[str, str]


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


@dataclass
class ProcessedFileFields:
    code: opt_str = ""
    text: str = ""


@dataclass
class ProcessedData:
    file: ProcessedFileFields = field(default_factory=ProcessedFileFields)
