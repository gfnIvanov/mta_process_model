import os
import random
import traceback
import click
import yaml
import logging
import dvc.api
from pathlib import Path
import xml.etree.ElementTree as ET
from . import root_dir
from .utils import fio_comparsion

dvc_params = dvc.api.params_show()


@click.command()
@click.option("--type", type=click.Choice(["genetics"]))
@click.argument("index", type=int, required=False)
def parse_xml(type: str, index: int = None):
    try:
        logger = logging.getLogger("Function: parse_xml")
        raw_path = root_dir.joinpath(dvc_params["paths"][type]["raw"])
        res_path = root_dir.joinpath(dvc_params["paths"][type]["int"])
        files_list = os.listdir(raw_path)
        ns = {"hl7": "urn:hl7-org:v3"}
        data = dict.fromkeys(["file"])
        data["file"] = dict.fromkeys(["code", "patient", "author", "text"])
        data["file"]["patient"] = dict.fromkeys(["lastname", "firstname", "surname"])
        data["file"]["author"] = dict.fromkeys(["lastname", "firstname", "surname"])

        if index is not None:
            files_list = random.sample(files_list, index)

        for file in files_list:
            data["file"]["code"] = Path(file).stem
            tree = ET.parse(raw_path.joinpath(file))
            root = tree.getroot()
            patient = root.find(".//hl7:patient/hl7:name", ns)
            data["file"]["patient"]["lastname"] = patient[0].text
            data["file"]["patient"]["firstname"] = patient[1].text
            data["file"]["patient"]["surname"] = patient[2].text
            author = root.find(".//hl7:author//hl7:assignedPerson/hl7:name", ns)
            data["file"]["author"]["lastname"] = author[0].text
            data["file"]["author"]["firstname"] = author[1].text
            data["file"]["author"]["surname"] = author[2].text
            authentif = root.find(
                ".//hl7:legalAuthenticator//hl7:assignedPerson/hl7:name", ns
            )
            if not fio_comparsion(data["file"]["author"], authentif):
                data["file"]["authentif"] = {}
                data["file"]["authentif"] = dict.fromkeys(
                    ["lastname", "firstname", "surname"]
                )
                data["file"]["authentif"]["lastname"] = authentif[0].text
                data["file"]["authentif"]["firstname"] = authentif[1].text
                data["file"]["authentif"]["surname"] = authentif[2].text
            docof = root.find(".//hl7:documentationOf//hl7:assignedPerson/hl7:name", ns)
            if not fio_comparsion(data["file"]["author"], docof):
                data["file"]["docof"] = {}
                data["file"]["docof"] = dict.fromkeys(
                    ["lastname", "firstname", "surname"]
                )
                data["file"]["docof"]["lastname"] = docof[0].text
                data["file"]["docof"]["firstname"] = docof[1].text
                data["file"]["docof"]["surname"] = docof[2].text
            obs_fields = root.findall(".//hl7:observation", ns)
            for obs in obs_fields:
                if obs[0].attrib["code"] in ["805", "806", "1805", "1806"]:
                    data["file"]["text"] = (
                        str(data["file"]["text"])
                        + "\n"
                        + obs.find("hl7:value", ns).text
                    )
            with open(os.path.join(res_path, "data.yaml"), "a") as new_file:
                yaml.dump(data, new_file, encoding="utf-8", allow_unicode=True)
    except Exception as e:
        click.echo(
            click.style(
                f"An error has occurred ({e}). Check logs/data_logs.log file", fg="red"
            )
        )
        logger.error(traceback.format_exc())
