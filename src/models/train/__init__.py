import os
import yaml
import torch
import logging
from pathlib import Path
from yaml.loader import SafeLoader

root_dir = Path(__file__).resolve().parents[3]

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

with open(root_dir.joinpath("params/logs.yaml")) as file:
    logs_conf = yaml.load(file, Loader=SafeLoader)

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
log_level = logging.INFO if os.getenv("MODE") == "dev" else logging.ERROR
logging.basicConfig(
    level=log_level, filename=logs_conf["models_log_file"], format=log_fmt
)
