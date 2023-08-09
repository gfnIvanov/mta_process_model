import torch
import yaml
from pathlib import Path
from yaml.loader import SafeLoader

root_dir = Path(__file__).resolve().parents[3]

with open(root_dir.joinpath("params/models.yaml")) as file:
    models_conf = yaml.load(file, Loader=SafeLoader)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
