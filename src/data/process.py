import os
import random
import traceback
from typing import Union
import click
import logging
import dvc.api
from . import root_dir
from .utils._parse_xml import _parse_xml
from .utils.types import InterimData

dvc_params = dvc.api.params_show()


@click.command()
@click.option("--type", type=click.Choice(["genetics"]))
@click.argument("index", type=int, required=False)
def parse_xml(type: str, index: Union[int, None] = None) -> None:
    try:
        logger = logging.getLogger("Function: parse_xml")
        raw_path = root_dir.joinpath(dvc_params["paths"][type]["raw"])
        res_path = root_dir.joinpath(dvc_params["paths"][type]["int"])
        files_list = os.listdir(raw_path)
        ns = {"hl7": "urn:hl7-org:v3"}

        if index is not None:
            files_list = random.sample(files_list, index)

        for file in files_list:
            data = InterimData()
            _parse_xml(file, data, ns, raw_path, res_path)
    except Exception as e:
        click.echo(
            click.style(
                f"An error has occurred ({e}). Check logs/data_logs.log file", fg="red"
            )
        )
        logger.error(traceback.format_exc())
