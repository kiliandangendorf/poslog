# PosLog: Creating a PoS Tagger for Log Messages

This repo belongs to the work of the same name, in which a corpus of log messages was compiled and annotated in Upos. 
The PosLog classifier, a PoS tagger specifically for log messages, was then trained on this corpus.
The development process is documented in this repo.

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

## Developing PosLog

For development purposes, you can install the package in editable mode. 
(Otherwise it will be installed by `pip` from the `requirements.txt`)
```bash
pip install -e src/
```

Having trouble this way, you may try to install the package without symlinks:
```bash
pip install src/
```

# PosLog Usage
PosLog usage you may find here: [`src/README.md`](/src/README.md).


# Reproduce Training Data 

## Datasets 
As stated in [`data/README.md`](/data/README.md) you can download the datasets from [Loghub](https://github.com/logpai/loghub).


## Data Processing
Following the numbered notebooks:
- `1_templates_collect_numb_var.ipynb`:
    Collec
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
