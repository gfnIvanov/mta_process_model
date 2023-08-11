import torch
from pathlib import Path
from pandas import DataFrame
from datasets import Dataset
from typing import Any, cast
from sklearn.model_selection import train_test_split
from transformers import (
    AutoTokenizer,
    PreTrainedModel,
    AutoModelForMaskedLM,
    DataCollatorForLanguageModeling,
    TrainingArguments,
    Trainer,
)


def _train(
    df: DataFrame, model_name: str, res_path: Path, device: torch.device
) -> None:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm_probability=0.15
    )
    model = cast(
        PreTrainedModel,
        AutoModelForMaskedLM.from_pretrained(model_name).to(device),
    )

    train, test = train_test_split(df, test_size=0.1)

    train = Dataset.from_pandas(train)
    test = Dataset.from_pandas(test)

    def tokenize(examples: Any) -> Any:
        return tokenizer(examples["text"], padding="max_length", truncation=True)

    tokenized_train = train.map(tokenize)
    tokenized_test = test.map(tokenize)

    training_args = TrainingArguments(
        output_dir="trained_biobert",
        evaluation_strategy="epoch",
        per_device_train_batch_size=6,
        per_device_eval_batch_size=6,
        num_train_epochs=5,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_test,
        data_collator=data_collator,
    )

    trainer.train()

    model.save_pretrained(res_path)
