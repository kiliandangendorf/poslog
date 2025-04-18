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

## Datasets 
As stated in [`data/README.md`](/data/README.md) you can download the datasets or link them manually in file [`local_datasets.py`](local_datasets.py) to easily access them within this project.


# Data Preprocessing
Following the numbered notebooks:
- `1_templates_collect_numb_var.ipynb`
- `2_pos_tagging_create.ipynb`
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

# CRF