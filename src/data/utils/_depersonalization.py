import torch
from tqdm import tqdm
from typing import Iterator, cast
from pathlib import Path
from .types import InterimData, ProcessedData, ProcessedFileFields
from .general import get_sentences, clean_with_regexp, save_yaml_file
from transformers import AutoTokenizer, PreTrainedModel, AutoModelForTokenClassification


def _depersonalization(
    model_name: str,
    model_tags: list[str],
    int_files: Iterator[InterimData],
    filescount: int,
    int_path: Path,
    device: torch.device,
) -> Iterator[ProcessedData]:
    """
    Data depersonalization function

    Performs data depersonalization using regular expressions and NER-model
    Returns an iterable object with depersonalized data to be saved to a yaml-file

    Arguments:
    model_name: str - model name
    model_tags: list[str] - pers data tags in the model
    int_files: Iterator[InterimData] - files from raw yaml-file
    filescount: int - files quant in yaml-file
    int_path: Path - path to interim data
    device: torch.device - cuda or cpu
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    ner_model = cast(
        PreTrainedModel,
        AutoModelForTokenClassification.from_pretrained(model_name).to(device),
    )

    for data in tqdm(int_files, total=filescount, ncols=100, desc="Depersonalization"):
        if data.file.text is None:
            continue

        result_text = ""
        pers_data: list[str] = []
        for_regexp = []
        deleted_data: list[str] = []
        res_object = ProcessedData()
        res_object_fields = ProcessedFileFields()

        if data.file.authentif is not None:
            for_regexp.extend(
                [
                    data.file.authentif.firstname,
                    data.file.authentif.surname,
                    data.file.authentif.lastname,
                ]
            )
        if data.file.docof is not None:
            for_regexp.extend(
                [
                    data.file.docof.firstname,
                    data.file.docof.surname,
                    data.file.docof.lastname,
                ]
            )
        for_regexp.extend(
            [
                data.file.author.firstname,
                data.file.author.surname,
                data.file.author.lastname,
            ]
        )
        for_regexp.extend(
            [
                data.file.patient.firstname,
                data.file.patient.surname,
                data.file.patient.lastname,
            ]
        )

        for sent in get_sentences(data.file.text, 512):
            local_sent, del_data = clean_with_regexp(for_regexp, sent)

            if len(result_text) == 0:
                result_text += local_sent
            else:
                result_text += " " + local_sent

            deleted_data.extend(del_data)

            inputs = tokenizer(
                local_sent, add_special_tokens=False, return_tensors="pt"
            ).to(device)
            with torch.no_grad():
                logits = ner_model(**inputs).logits

            predicted_token_class_ids = logits.argmax(-1)

            predicted_tokens_classes = [
                ner_model.config.id2label[t.item()]
                for t in predicted_token_class_ids[0]
            ]

            for i, token in enumerate(inputs["input_ids"][0]):
                if predicted_tokens_classes[i] in model_tags:
                    word_part = tokenizer.decode([token], skip_special_tokens=True)
                    if word_part.find("#") != 0 and len(pers_data) != 0:
                        pers_data.append(" ")
                    pers_data.append(word_part.replace("#", ""))

        from_model_with_empty = ("").join(pers_data).split(" ")

        from_model = list(filter(lambda x: len(x) > 2, from_model_with_empty))

        result_text, del_data = clean_with_regexp(from_model, result_text)

        deleted_data.extend(del_data)

        del_data_object = {"file": {"code": data.file.code, "deleted": deleted_data}}

        res_object_fields.code = data.file.code
        res_object_fields.text = result_text
        res_object.file = res_object_fields

        save_yaml_file(del_data_object, int_path, "deleted_data.yaml")

        yield res_object
