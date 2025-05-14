# PosLog
A CRF-based Part-of-Speech (POS) Tagger for Log Messages.

## Usage
- **Use default model**  
    ```python
    from poslog import PosLogTokenizer, PosLogCRF

    tokenizer=PosLogTokenizer()
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
    pos_log=PosLogCRF(model_name="abs_path_to_my_model")
    ```
    You can give `abs_path_to_my_model` as absolute path or relative path.  
    Note: Relative paths models will stored in package directory `models/` and will be overwritten if you renew the environment.

    PosLog takes training data as tokens and tags separately:
    ```python
    train(X_train_tokens:list[list[str]], y_train_tags:list[list[str]])
    ```
    Or as token and tag pairs:
    ```python
    train_from_tagged_sents(tagged_sents:list[list[tuple[str,str]]])
    ```
    After training, the model will be saved in the path you provided in the constructor.  
    Note: Training will override existing model with the same name.

- **Use your own model**  
    Just call the constructor with the model name:
    ```python
    pos_log=PosLogCRF(model_name="my_model")
    ```

## Dependencies

PosLog relies on 
- `nltk` corpora: `words`, `stopwords`, `wordnet` and 
- `sklearn` for the CRF classifier `sklearn-crfsuite`.