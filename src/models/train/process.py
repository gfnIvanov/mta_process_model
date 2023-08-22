import click
import logging
import dvc.api
import traceback
import pandas as pd
from typing import Union
from . import root_dir, DEVICE
from .utils._local_train import _local_train

dvc_params = dvc.api.params_show()


@click.command()
@click.option("--datatype", type=click.Choice(["genetics"]))
@click.option("--model", type=click.Choice(["gpt", "bert"]))
@click.option("--size", type=click.Choice(["large", "medium", "small"]), default=None)
def train(datatype: str, model: str, size: Union[str, None] = None) -> None:
    try:
        logger = logging.getLogger("Function: train")
        data_path = root_dir.joinpath(dvc_params["paths"][datatype]["res"])
        res_path = root_dir.joinpath(dvc_params["path_to_trained"])

        if model == "bert":
            model_name = dvc_params["for_train"][model]
        if model == "gpt":
            if size is None:
                raise Warning(
                    "A required parameter (size) for the model (gpt) was not specified"
                )
            model_name = dvc_params["for_train"][model][size]

        df = pd.read_csv(data_path.joinpath("data.csv"))

        _local_train(df, model_name, res_path, DEVICE)

    except Warning as w:
        click.echo(click.style(str(w), fg="yellow"))
        logger.warning(w)
    except Exception as e:
        click.echo(
            click.style(
                f"An error has occurred ({e}). Check logs/data_logs.log file", fg="red"
            )
        )
        logger.error(traceback.format_exc())
