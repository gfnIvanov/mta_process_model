import os
import random
import traceback
import click
import yaml
import logging
import dvc.api
from typing import Union, Iterator, cast
from . import root_dir, DEVICE
from .utils.general import save_yaml_file, count_files_in_yaml
from .utils._parse_xml import _parse_xml
from .utils._depersonalization import _depersonalization
from .utils._prepare_dataset import _prepare_dataset
from .utils._to_s3 import _to_s3
from .utils.types import InterimData, ProcessedData

dvc_params = dvc.api.params_show()


@click.command()
@click.option("--datatype", type=click.Choice(["genetics"]))
@click.argument("index", type=int, required=False)
def parse_xml(datatype: str, index: Union[int, None] = None) -> None:
    """
    Wrapper for xml-file parsing function

    Performs variable preparation, calls the parsing function, saves the result

    Arguments:
    datatype: str - data type
    index: Union[int, None] = None - limit on the number of processed files
    """
    try:
        logger = logging.getLogger("Function: parse_xml")
        raw_path = root_dir.joinpath(dvc_params["paths"][datatype]["raw"])
        res_path = root_dir.joinpath(dvc_params["paths"][datatype]["int"])
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
@click.option("--datatype", type=click.Choice(["genetics"]))
@click.option("--model", type=click.Choice(["sber", "labse"]))
def depersonalization(datatype: str, model: str) -> None:
    """
    Wrapper for data depersonalization function

    Performs variable preparation, loads raw data from a file,
    calls the depersonalization function, saves the result

    Arguments:
    datatype: str - data type
    model: str - model used to solve the NER-task
    """
    try:
        logger = logging.getLogger("Function: depersonalization")
        int_path = root_dir.joinpath(dvc_params["paths"][datatype]["int"])
        res_path = root_dir.joinpath(dvc_params["paths"][datatype]["res"])
        model_name = dvc_params["depers"][model]["name"]
        model_tags = dvc_params["depers"][model]["tags"]
        filescount = count_files_in_yaml(int_path.joinpath("data.yaml"))

        with open(int_path.joinpath("data.yaml"), "r") as file:
            int_files = cast(
                Iterator[InterimData], yaml.load_all(file, Loader=yaml.Loader)
            )

            res_data = _depersonalization(
                model_name,
                model_tags,
                int_files,
                filescount,
                int_path,
                DEVICE,
            )

            save_yaml_file(res_data, res_path, "data.yaml", True)
    except Exception as e:
        click.echo(
            click.style(
                f"An error has occurred ({e}). Check logs/data_logs.log file", fg="red"
            )
        )
        logger.error(traceback.format_exc())


@click.command()
@click.option("--datatype", type=click.Choice(["genetics"]))
@click.option("--to_s3", type=bool)
def prepare_dataset(datatype: str, to_s3: bool) -> None:
    """
    Wrapper for dataset preparation function

    Performs variable preparation, loads raw data from a file,
    calls the dataset preparation function
    sends the finished dataset to remote s3-storage

    Arguments:
    datatype: str - data type
    """
    try:
        logger = logging.getLogger("Function: prepare_dataset")
        data_path = root_dir.joinpath(dvc_params["paths"][datatype]["res"])

        with open(data_path.joinpath("data.yaml"), "r") as file:
            proc_files = cast(
                Iterator[ProcessedData], yaml.load_all(file, Loader=yaml.Loader)
            )

            _prepare_dataset(proc_files, data_path)

            if to_s3:
                s3_bucket = dvc_params["s3_storage"]["bucket"]
                s3_url = dvc_params["s3_storage"]["url"]

                _to_s3(data_path, s3_bucket, s3_url)

    except Exception as e:
        click.echo(
            click.style(
                f"An error has occurred ({e}). Check logs/data_logs.log file", fg="red"
            )
        )
        logger.error(traceback.format_exc())
