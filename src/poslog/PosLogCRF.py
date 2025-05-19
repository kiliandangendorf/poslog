from sklearn_crfsuite import CRF
import pickle
import os
from poslog.words import KnownWordsDetector, RegexTokenClassMatcher, WordKind, TokenClass
from poslog.AbstractPosTagger import AbstractPosTagger
from poslog.PosLogTokenizer import PosLogTokenizer
import logging
import re
import string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PosLogCRF(AbstractPosTagger):
    DEFAULT_MODEL_PATH='models'
    DEFAULT_MODEL='pos_log_upos_crf_10k_model'

    def __init__(self, model_path:str=None, make_features=None):    
        self.model_path = self._get_model_path(model_path)
        self.crf = None
        self.kwdet=KnownWordsDetector()
        self.rgtcm=RegexTokenClassMatcher()
        self.tokenizer:PosLogTokenizer=None

        #TODO
        if make_features is not None:
            self.make_features=make_features

    def train(self, X_train_tokens:list[list[str]], y_train_tags:list[list[str]])->None:
        self.crf = CRF(algorithm='lbfgs', 
                       c1=0.1, 
                       c2=0.1, 
                       max_iterations=30, #More iterations takes too long#100, 
                       all_possible_transitions=True)
        feat=[self.make_features(s) for s in X_train_tokens]
        self.crf.fit(feat, y_train_tags)
        self.save_model(self.model_path)

    def train_from_tagged_sents(self, tagged_sents:list[list[tuple[str,str]]])->None:
        X_train_tokens=[[word for word,_ in tagged_sent] for tagged_sent in tagged_sents]
        y_train_tags=[[tag for _,tag in tagged_sent] for tagged_sent in tagged_sents]
        self.train(X_train_tokens, y_train_tags)

    def _get_model_path(self, model:str=None):
        """ Returns absolute path to model file. If model_path is not given, the default model is used. """
        def rel_model_path(model:str):
            model_path=os.path.join(os.path.dirname(__file__), self.DEFAULT_MODEL_PATH)
            # make sure directory exists
            os.makedirs(model_path, exist_ok=True)
            return os.path.join(model_path, model+'.pkl')
        if model is not None:
            if os.path.isabs(model):
                return model
            else:
                return rel_model_path(model)
        else:
            # choose default model
            return rel_model_path(self.DEFAULT_MODEL)

    def save_model(self, model:str=None):
        model_path=self._get_model_path(model)
        if model_path==self._get_model_path(self.DEFAULT_MODEL):
            logger.warning("Default model path is used. Won't save it. If you want to save the model to a different location, provide a model path.")
            return
        with open(model_path, 'wb') as f:
            pickle.dump(self.crf, f)
        self.model_path=model_path
        logger.info(f"Saved model to '{model_path}'")

    def load_model(self):
        with open(self.model_path, 'rb') as f:
            self.crf = pickle.load(f)

    def pos_tag(self,tokens:list[str], tagset='upos')->list[str]:
        match tagset:
            case 'upos':
                return self.predict(tokens)
            case 'ptb':
                raise NotImplementedError("PTB tagset is not implemented yet")
            case _:
                raise ValueError(f"Unknown tagset: {tagset}")
    
    def predict(self, X:list[str])->list[str]:
        if self.crf is None:
            self.load_model()
        feat=self.make_features(X)
        return list(self.crf.predict([feat])[0])

    def predict_string(self, X:str)->list[str]:
        if self.tokenizer is None:
            self.tokenizer=PosLogTokenizer()
        tokens=self.tokenizer.tokenize(X)
        return self.predict(tokens)

    def predict_string_as_tuple(self, X:str)->list[tuple[str,str]]:
        if self.tokenizer is None:
            self.tokenizer=PosLogTokenizer()
        tokens=self.tokenizer.tokenize(X)
        tags=self.predict(tokens)
        return list(zip(tokens, tags))


    def make_features(self, words:list[str])->list[dict[str,str]]:
        features_list=[]
        for i, word in enumerate(words):

            features = {}

            features['word']=word

            kind_of_known_word = self.kwdet.kind_of_known_word(word)
            features['is_stopword'] = 1 if kind_of_known_word == WordKind.STOP_WORD else 0
            features['is_wordnet'] = 1 if kind_of_known_word == WordKind.WORD_NET else 0
            features['is_wordnet'] = 1 if kind_of_known_word == WordKind.WORD_NET or kind_of_known_word == WordKind.WORDS_DICTIONARY else 0
            features['is_domain_word'] = 1 if kind_of_known_word == WordKind.DOMAIN_WORD else 0
            features['is_number'] = 1 if kind_of_known_word == WordKind.NUMBER else 0
            features['is_unknown'] = 1 if kind_of_known_word == WordKind.UNKNOWN else 0

            token_class:TokenClass = self.rgtcm.token_class(word)
            features['word_class'] = token_class.value

            features['has_upper'] = 1 if re.search(r'[A-Z]',word) else 0

            path_regex=re.compile(r'\w*:?([\.\/\\]+[\w\-:]+)+')
            features['is-path']=1 if path_regex.fullmatch(word) else 0

            # For better distinguish between 'to' as ADP and PART
            features['is_to']=1 if word.lower() == 'to' else 0

            features['contains_number'] = 1 if re.search(r'[0-9]',word) else 0
            
            features['contains_punct']=1 if re.search(r'['+string.punctuation+']',word) else 0

            # ideas from: https://www.geeksforgeeks.org/conditional-random-fields-crfs-for-pos-tagging-in-nlp/
            features['is_first'] = i == 0
            features['is_last'] = i == len(words) - 1

            features['all_caps'] = 1 if word.upper() == word else 0
            features['all_lower'] = 1 if word.lower() == word else 0

            # Next word to better distinguish between 'to' as ADP and PART
            features['next_word']= '' if i == len(words)-1 else words[i+1]
            
            features['prev_char']= '' if i == 0 else words[i-1][-1]
            features['next_char']= '' if i == len(words)-1 else words[i+1][0]

            features['prefix-1'] = word[0]
            features['prefix-2'] = word[:2]

            features['suffix-1'] = word[-1]
            features['suffix-2'] = word[-2:]
            features['suffix-3'] = word[-3:]
            
            
            word_lower = word.lower()
            features['word.lower'] = word_lower

            # Prefixes and suffixes — useful for ADJ
            features['suffix3'] = word_lower[-3:]
            features['suffix2'] = word_lower[-2:]
            features['prefix2'] = word_lower[:2]
            features['prefix3'] = word_lower[:3]

            # Punctuation — useful to catch INTJ
            features['is_punct'] = str(word in "!?.;,")

            # Position-aware features
            if i > 0:
                features['prev_word'] = words[i - 1].lower()
                features['prev_is_upper'] = str(words[i - 1].isupper())
            if i < len(words) - 1:
                # features['next_word'] = words[i + 1].lower()
                features['next_is_upper'] = str(words[i + 1].isupper())

            # Shape-based features
            features['word_shape'] = get_shape(word)

            # particles = {'not', 'off', 'up', 'down'}
            # interjections = {'oh', 'ah', 'wow', 'hey', 'oops', 'ouch', 'ok', 'bye', 'yes'}
            adjective_suffixes = ('ous', 'ful', 'ive', 'able', 'al', 'ic', 'less', 'ish')

            features['adj_suffix_match'] = str(any(word_lower.endswith(suf) for suf in adjective_suffixes))

            noun_suffixes = ('tion', 'ment', 'ness', 'ity', 'ship', 'age', 'ism', 'ence', 'ance', 'hood', 'dom')
            features['noun_suffix'] = str(any(word_lower.endswith(suf) for suf in noun_suffixes))

            # e.g., "the big ___" → likely NOUN
            determiners = {'the', 'a', 'an', 'this', 'that', 'these', 'those'}
            features['prev_is_determiner'] = str(i > 0 and words[i-1].lower() in determiners)

            features_list.append(features)
        
        return features_list        

def get_shape(word: str) -> str:
    shape = ''
    for char in word:
        if char.isupper():
            shape += 'X'
        elif char.islower():
            shape += 'x'
        elif char.isdigit():
            shape += 'd'
        else:
            #shape += '_'
            shape += char
    return shape
