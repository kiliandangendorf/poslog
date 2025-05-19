# PosLog
A CRF-based Part-of-Speech (POS) Tagger for Log Messages.
In comparison to SoTA PoS taggers, PosLog is trained on a corpus of log messages and achieves an accuracy of 98.27% on the test set.

**Table: Accuracy of PoS tagger in comparison.**  
*Ordered by increasing accuracy. The time is shown in seconds per 1 million tokens.*
| Tagger     | Time   | Accuracy   |
|------------|--------|------------|
| NLTK       | **28** | 77.28%     |
| HanTa      | 506    | 78.74%     |
| TreeTagger | 43     | 79.58%     |
| SpaCy      | 428    | 80.89%     |
| Stanza     | 5,376  | 90.25%     |
| poslog     | 45     | **98.27%** |



# Usage

## Use Default Model
There are three ways to use the default model:
1. Predict the PoS tags of a **list of tokens** returning a list of tags.
    ```python
    from poslog import PosLogTokenizer, PosLogCRF

    msg="Tag this sentence."

    tokenizer=PosLogTokenizer()
    tokens=tokenizer.tokenize(msg)
    # ['Tag', 'this', 'sentence', '.']

    pos_log=PosLogCRF()
    # predict(X:list[str])->list[str]
    pos_log.predict(tokens)
    # ['VERB' 'DET' 'NOUN' 'PUNCT']
    ```

2. Predict the PoS tags of a **string** returning a list of tags.
    ```python
    # predict_string(X:str)->list[str]
    pos_log.predict_string(msg)
    # ['VERB' 'DET' 'NOUN' 'PUNCT']
    ```

3. Predict the PoS tags of a **string** returning a list of tuples with token and tag.
    ```python
    # predict_string_as_tuple(X:str)->list[tuple[str,str]]
    pos_log.predict_string_as_tuple(msg)
    # [('Tag', 'VERB'), ('this', 'DET'), ('sentence', 'NOUN'), ('.', 'PUNCT')]
    ```


## Train Your Own Model
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

## Use Your Own Model
Just call the constructor with the model name:
```python
pos_log=PosLogCRF(model_name="my_model")
```


# Tokenization

Since PosLog was trained on a corpus we tokenized a specific way, we
included the tokenizer `PosLogTokenizer` in this package.

We use three preprocessing steps before tokenization to adapt to log
message specific characteristics:

1.  We escape *quotation marks* with spaces to distinguish them from
    words with tailing apostrophes.

2.  We extend NLTK's contraction list with 124 more cases where we split
    or replace contracted words.

3.  We apply NLTK's `word_tokenize` which makes a few more
    replacements and returns a token list.

The following shows an example of the three steps of
tokenization:

Example for the three steps of tokenization.
0 shows the input string and 3 the output list of tokenization.
```
0 (Input):  "Can't read 'block_x'."
1:          "Can't read 'block_x '."
2:          "Cannot read 'block_x '."
3 (Output): ["Can", "not", "read", "'", "block_x", "'", "."]
```




## Dependencies

PosLog relies on 
- `nltk` corpora: `words`, `stopwords`, `wordnet` and 
- `sklearn` for the CRF classifier `sklearn-crfsuite`.