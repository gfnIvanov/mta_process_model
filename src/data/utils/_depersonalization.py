import torch
from typing import Iterator
from pathlib import Path
from .types import InterimData
from .general import get_sentences, clean_with_regexp, save_yaml_file
from transformers import PreTrainedTokenizer, PreTrainedModel


def _depersonalization(
    tokenizer: PreTrainedTokenizer,
    ner_model: PreTrainedModel,
    model_tags: list[str],
    int_files: Iterator[InterimData],
    int_path: Path,
    res_path: Path,
    DEVICE: torch.device,
) -> None:
    for data in int_files:
        if data.file.text is None:
            continue

        result_text = ""
        pers_data: list[str] = []
        for_regexp = []
        deleted_data: list[str] = []

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

        for sent in get_sentences(data.file.text):
            local_sent, del_data = clean_with_regexp(for_regexp, sent)

            if len(result_text) == 0:
                result_text += local_sent
            else:
                result_text += " " + local_sent

            deleted_data.extend(del_data)

            inputs = tokenizer(
                local_sent, add_special_tokens=False, return_tensors="pt"
            ).to(DEVICE)
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

        from_model = list(filter(lambda x: len(x) > 1, from_model_with_empty))

        result_text, del_data = clean_with_regexp(from_model, result_text)

        deleted_data.extend(del_data)

        del_data_object = {"file": {"code": data.file.code, "deleted": deleted_data}}

        res_object = {"file": {"code": data.file.code, "text": result_text}}

        save_yaml_file(del_data_object, int_path, "deleted_data.yaml")

        save_yaml_file(res_object, res_path, "data.yaml")
