import os
import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import cast
from .base import fio_comparsion
from .types import InterimData, FioFields, str_dict


def _parse_xml(
    file: str,
    data: InterimData,
    ns: str_dict,
    raw_path: Path,
    res_path: Path,
) -> None:
    data.file.code = Path(file).stem
    tree = ET.parse(raw_path.joinpath(file))
    root = tree.getroot()
    patient = cast(ET.Element, root.find(".//hl7:patient/hl7:name", ns))
    data.file.patient.lastname = patient[0].text
    data.file.patient.firstname = patient[1].text
    data.file.patient.surname = patient[2].text
    author = cast(
        ET.Element, root.find(".//hl7:author//hl7:assignedPerson/hl7:name", ns)
    )
    data.file.author.lastname = author[0].text
    data.file.author.firstname = author[1].text
    data.file.author.surname = author[2].text
    authentif = cast(
        ET.Element,
        root.find(".//hl7:legalAuthenticator//hl7:assignedPerson/hl7:name", ns),
    )
    if authentif is not None and not fio_comparsion(data.file.author, authentif):
        data.file.authentif = FioFields()
        data.file.authentif.lastname = authentif[0].text
        data.file.authentif.firstname = authentif[1].text
        data.file.authentif.surname = authentif[2].text
    docof = cast(
        ET.Element,
        root.find(".//hl7:documentationOf//hl7:assignedPerson/hl7:name", ns),
    )
    if docof is not None and not fio_comparsion(data.file.author, docof):
        data.file.docof = FioFields()
        data.file.docof.lastname = docof[0].text
        data.file.docof.firstname = docof[1].text
        data.file.docof.surname = docof[2].text
    obs_fields = root.findall(".//hl7:observation", ns)
    for obs in obs_fields:
        if obs[0].attrib["code"] in ["805", "806", "1805", "1806"]:
            data.file.text = (
                str(data.file.text)
                + "\n"
                + cast(str, cast(ET.Element, obs.find("hl7:value", ns)).text)
            )
    with open(os.path.join(res_path, "data.yaml"), "a") as new_file:
        yaml.dump(data, new_file, encoding="utf-8", allow_unicode=True)
