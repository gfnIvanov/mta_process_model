import os
import yaml
import logging
from pathlib import Path
from yaml.loader import SafeLoader

root_dir = Path(__file__).resolve().parents[2]

with open(root_dir.joinpath("conf.yaml")) as file:
    main_conf = yaml.load(file, Loader=SafeLoader)

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
log_level = logging.INFO if os.getenv("MODE") == "dev" else logging.ERROR
logging.basicConfig(
    level=log_level, filename=main_conf["data_log_file"], format=log_fmt
)