import torch
import click
from . import DEVICE
from transformers import AutoTokenizer, AutoModelForMaskedLM


@click.command()
@click.argument("text")
def use_bert_native(text: str):
    try:
        tokenizer = AutoTokenizer.from_pretrained("alexyalunin/RuBioRoBERTa")
        text_with_mask = text + tokenizer.mask_token + "."
        model = AutoModelForMaskedLM.from_pretrained("alexyalunin/RuBioRoBERTa")
        input_ids = tokenizer.encode(text_with_mask, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            logits = model(input_ids).logits
        mask_token_index = torch.where(input_ids == tokenizer.mask_token_id)[1]
        masked_token_logits = logits[0, mask_token_index, :]
        top_3_tokens = torch.topk(masked_token_logits, 3, dim=1).indices[0].tolist()
        for token in top_3_tokens:
            print(tokenizer.decode([token]))
    except Exception as e:
        click.echo(click.style(e, fg="red"))
