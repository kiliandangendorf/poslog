from collections import defaultdict
from typing import Literal
from typing import Any

######################
# Tagset Mapping
# 
# Implementing own mappings since the nltk mappings only use 12 universal tags (instead of 17)
######################

class TagDict(defaultdict):
    def __missing__(self, key):
        return "UNK-- "+key

_MAPPINGS=None

#_MAPPINGS = defaultdict(lambda: defaultdict(lambda: "UNK"))
_MAPPINGS:dict[TagDict]={}


from pathlib import Path
def _load_map(map_id):
    map_file = Path(__file__).parent / 'mappings' / (map_id+".map")
    with open(map_file, "r") as f:
        contents = f.read()
        
        _MAPPINGS[map_id]=TagDict()

        for line in contents.splitlines():
            line = line.strip()
            if line == "":
                continue
            fine, coarse = line.split("\t")

            assert fine not in _MAPPINGS[map_id], f"Tag already in map: {fine}->{coarse} (map_id: {map_id}, map: {_MAPPINGS[map_id][fine]})"

            _MAPPINGS[map_id][fine] = coarse

def get_tagset_mapping(map_id:Literal['ptb_upos', 'brown_upos', 'brown_ptb', 'tt-ptb_upos', 'tt-ptb_ptb']) -> defaultdict[Any, str]:
    if map_id not in _MAPPINGS:
        _load_map(map_id)
    return _MAPPINGS[map_id]

def ptb2upos(tagged_words: list[str]) -> list[str]:
    # translates Penn Treebank tags to Universal tags
    return [get_tagset_mapping('ptb_upos')[tagged_word] for tagged_word in tagged_words]

def brown2upos(tagged_words: list[str]) -> list[str]:
    # translates Brown tags to Universal tags
    return [get_tagset_mapping('brown_upos')[tagged_word] for tagged_word in tagged_words]

def brown2ptb(tagged_words: list[str]) -> list[str]:
    # translates Brown tags to Penn Treebank tags
    return [get_tagset_mapping('brown_ptb')[tagged_word] for tagged_word in tagged_words]

######################
# TreeTagger
######################

def tt_ptb2upos(tagged_words: list[str]) -> list[str]:
    # translates TreeTagger Penn Treebank tags to Universal tags
    return [get_tagset_mapping('tt-ptb_upos')[tagged_word] for tagged_word in tagged_words]

def tt_ptb2ptb(tagged_words: list[str]) -> list[str]:
    # translates TreeTagger Penn Treebank tags to Penn Treebank tags
    return [get_tagset_mapping('tt-ptb_ptb')[tagged_word] for tagged_word in tagged_words]


######################
# Unify Tags
#
# For not own mappings, especially for SpaCy and Stanzas extended PTB tags
#
# ( ) [ ] { } become, in parsed files: -LRB- -RRB- -LSB- -RSB- -LCB- -RCB- 
# (The acronyms stand for (Left|Right) (Round|Square|Curly) Bracket.)
######################

UNIFY_PTB_MAP={
    '-LRB-':'(',
    '-RRB-':')',
    '-LSB-':'(',
    '-RSB-':')',
    '-LCB-':'(',
    '-RCB-':')'
}

def unify_ptb_tags(tags:list[str])->list[str]:
    # unify tags such as '-RBR-' to ')'
    for i,tag in enumerate(tags):
        if tag in UNIFY_PTB_MAP:
            tags[i]=UNIFY_PTB_MAP[tag]
    return tags