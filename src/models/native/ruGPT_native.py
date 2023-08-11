import click
from . import DEVICE, models_conf
from transformers import GPT2LMHeadModel, GPT2Tokenizer


@click.command()
@click.option("--size", default="small")
@click.argument("text")
def use_gpt_native(size: str, text: str) -> None:
    """
    Function to test the native gtp model

    Arguments:
    size: str - model size
    text: str - input text
    """
    try:
        if size not in list(models_conf["for_train"]["gpt"].keys()):
            raise Warning("Use these sizes: [large, medium, small]")
        model_name_or_path = models_conf["for_train"]["gpt"][size]
        tokenizer = GPT2Tokenizer.from_pretrained(model_name_or_path)
        model = GPT2LMHeadModel.from_pretrained(model_name_or_path).to(DEVICE)
        input_ids = tokenizer.encode(text, return_tensors="pt").to(DEVICE)
        outputs = model.generate(
            input_ids,
            max_new_tokens=10,
            do_sample=False,
            num_beams=5,
            no_repeat_ngram_size=2,
            num_return_sequences=3,
            early_stopping=True,
            top_k=50,
        )
        for out in outputs:
            print(tokenizer.decode(out, skip_special_tokens=True))
    except Warning as w:
        click.echo(click.style(str(w), fg="yellow"))
    except Exception as e:
        click.echo(click.style(str(e), fg="red"))
