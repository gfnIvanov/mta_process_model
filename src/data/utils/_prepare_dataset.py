import pandas as pd
from typing import Iterator
from pathlib import Path
from .types import ProcessedData
from .general import get_sentences


def _prepare_dataset(proc_files: Iterator[ProcessedData], res_path: Path) -> None:
    def join_data(data: ProcessedData) -> list[str]:
        return get_sentences(data.file.text, 128)

    def flatten(data: list[list[str]]) -> list[str]:
        result = []

        for arr in data:
            for sent in arr:
                result.append(sent)

        return result

    df = pd.DataFrame({"text": flatten(list(map(join_data, proc_files)))})

    df.to_csv(res_path.joinpath("data.csv"), index=False)
