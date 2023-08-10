### Medical Text Autocomplete

#### In the current repository:

 - Data is being prepared for model training

 - The model is being trained

#### As part of the data preparation phase:

The necessary text data is extracted from the xml-structure of the document (for further model training and comparison during depersonalization)

The received data is depersonalized using NER-models and regular expressions

Dataset for training is formed from depersonalized data

There are two models available for depersonalization:

 - [surdan/LaBSE_ner_nerel](https://huggingface.co/surdan/LaBSE_ner_nerel)
 - [viktoroo/sberbank-rubert-base-collection3 ](https://huggingface.co/viktoroo/sberbank-rubert-base-collection3)

#### As part of the model retraining stage:

The model is retrained on the prepared data using the resources of the local computer, or on the resources of Yandex Datasphere

There are two models available for model retraining:

 - [ai-forever/rugpt3large_based_on_gpt2](https://huggingface.co/ai-forever/rugpt3large_based_on_gpt2)
 - [alexyalunin/RuBioRoBERTa](https://huggingface.co/alexyalunin/RuBioRoBERTa)

These models can also be used in their original form without additional training.
