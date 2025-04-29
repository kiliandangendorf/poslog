# PosLog

## Install Requirements in Virtual Environment
1. Create virtual environment
```
python3 -m venv .venv
```
2. Activate virtual environment
```
source .venv/bin/activate
```
3. Install requirements
```
pip install -r requirements.txt
```

If you want to use this kernel in Jupyter Notebook, you need to install the kernel as well:
```bash
python -m ipykernel install --user --name=poslog
```

# PosLog Usage
- **Use Default model**  
    ```python
    from nlp import PrometeusTokenizer
    from nlp.pos import PosLogCRF

    tokenizer=PrometeusTokenizer()
    s="Tag this sentence."
    tokens=tokenizer.tokenize(s)
    # ['Tag', 'this', 'sentence', '.']

    pos_log=PosLogCRF()
    pos_log.predict(tokens)
    # ['VERB' 'DET' 'NOUN' 'PUNCT']
    ```
- **Train your own model**  
    Define model name in constructor:
    ```python
    pos_log=PosLogCRF(model_name="my_model")
    ```

    PosLog takes training data as tokens and tags separately:
    ```python
    train(X_train_tokens:list[list[str]], y_train_tags:list[list[str]])
    ```
    Or as token and tag pairs:
    ```python
    train_from_tagged_sents(tagged_sents:list[list[tuple[str,str]]])
    ```

    Note training will override existing model with the same name.

- **Use your own model**  
    Just call the constructor with the model name:
    ```python
    pos_log=PosLogCRF(model_name="my_model")
    ```

# Reproduce Training Data 

## Datasets 
As stated in [`data/README.md`](/data/README.md) you can download the datasets from [Loghub](https://github.com/logpai/loghub).


## Data Processing
Following the numbered notebooks:
- `1_templates_collect_numb_var.ipynb`
- `2_pos_tagging_create.ipynb`
- `2-2_tag_comparison_correction.ipynb`
- `3_random_sample.ipynb`
- `4_pos_tagging_manual_adjustment.ipynb`
- `5_poslog_crf.ipynb` ??



# Tagset Mappings

in nltk stlye (see ??)

in `nlp/pos/mappings`:
- `brown_ptb.map`
- `brown_upos.map`
- `ptb_upos.map`
- `tt-ptb_ptb.map`
- `tt-ptb_upos.map`

The xlsx file on which we created the mappings you'll find in `nlp/pos/tagset_mapping.xlsx`.
