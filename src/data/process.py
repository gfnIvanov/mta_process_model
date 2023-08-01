import os
import random
import traceback
import click
import yaml
import logging
import dvc.api
from typing import Union, Iterator, cast
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    PreTrainedTokenizer,
    PreTrainedModel,
)
from . import root_dir, DEVICE
from .utils.general import save_yaml_file
from .utils._parse_xml import _parse_xml
from .utils._depersonalization import _depersonalization
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

        parsed_data = _parse_xml(files_list, ns, raw_path)

        save_yaml_file(parsed_data, res_path, "data.yaml", True)
    except Exception as e:
        click.echo(
            click.style(
                f"An error has occurred ({e}). Check logs/data_logs.log file", fg="red"
            )
        )
        logger.error(traceback.format_exc())


@click.command()
@click.option("--type", type=click.Choice(["genetics"]))
@click.option("--model", type=click.Choice(["sber", "labse"]))
def depersonalization(type: str, model: str) -> None:
    try:
        logger = logging.getLogger("Function: depersonalization")
        int_path = root_dir.joinpath(dvc_params["paths"][type]["int"])
        res_path = root_dir.joinpath(dvc_params["paths"][type]["res"])
        model_name = dvc_params["depers"][model]["name"]
        model_tags = dvc_params["depers"][model]["tags"]

        with open(int_path.joinpath("data.yaml"), "r") as file:
            int_files = cast(
                Iterator[InterimData], yaml.load_all(file, Loader=yaml.Loader)
            )
            tokenizer = cast(
                PreTrainedTokenizer,
                AutoTokenizer.from_pretrained(model_name),
            )
            ner_model = cast(
                PreTrainedModel,
                AutoModelForTokenClassification.from_pretrained(model_name).to(DEVICE),
            )

            _depersonalization(
                tokenizer, ner_model, model_tags, int_files, int_path, res_path, DEVICE
            )
    except Exception as e:
        click.echo(
            click.style(
                f"An error has occurred ({e}). Check logs/data_logs.log file", fg="red"
            )
        )
        logger.error(traceback.format_exc())
