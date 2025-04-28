from sklearn_crfsuite import CRF
import pickle
import os
from nlp.pos import KnownWordsDetector, RegexTokenClassMatcher, WordKind, TokenClass
from nlp.pos import AbstractPosTagger
import logging
import re # TODO
import string # TODO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PosLogCRF(AbstractPosTagger):
    DEFAULT_MODEL_PATH='models'
    DEFAULT_MODEL='pos_log_upos_crf_63_model'

    def __init__(self, model_path:str=None, make_features=None):    
        self.model_path = self._get_model_path(model_path)
        self.crf = None
        self.kwdet=KnownWordsDetector()
        self.rgtcm=RegexTokenClassMatcher()

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
    
    #def predict(self, X:list[dict[str,str]]):
    def predict(self, X:list[str])->list[str]:
        if self.crf is None:
            self.load_model()
        feat=self.make_features(X)
        return self.crf.predict([feat])[0]

    # def sent2features(self,tagged_sent:list[tuple[str,str]])->list[dict[str,str]]:
    #     return self.make_features([word for word,_ in tagged_sent])
    
    # def sent2labels(self,tagged_sent:list[tuple[str,str]])->list[str]:
    #     return [label for _, label in tagged_sent]

    def make_features(self, words:list[str])->list[dict[str,str]]:
        features_list=[]
        for i, word in enumerate(words):

            features = {}

            features['word']=word

            #features['kind_of_known_word'] = kind_of_known_word(word) or 'unknown'
            kind_of_known_word = self.kwdet.kind_of_known_word(word)
            #features['kind_of_known_word'] = self.kwdet.kind_of_known_word(word).value
            features['is_stopword'] = 1 if kind_of_known_word == WordKind.STOP_WORD else 0
            features['is_wordnet'] = 1 if kind_of_known_word == WordKind.WORD_NET else 0
            features['is_wordnet'] = 1 if kind_of_known_word == WordKind.WORD_NET or kind_of_known_word == WordKind.WORDS_DICTIONARY else 0
            #features['is_words_dictionary'] = 1 if kind_of_known_word == WordKind.WORDS_DICTIONARY else 0
            features['is_domain_word'] = 1 if kind_of_known_word == WordKind.DOMAIN_WORD else 0
            features['is_number'] = 1 if kind_of_known_word == WordKind.NUMBER else 0
            features['is_unknown'] = 1 if kind_of_known_word == WordKind.UNKNOWN else 0



            #features['mask_type'] = get_mask_for_token(word) or 'unknown'
            #features['mask_type']=masker._determine_token_type(word).value
            token_class = self.rgtcm.token_class(word)
            features['word_class'] = token_class.value
            # features['tc_number'] = 1 if token_class == TokenClass.NUMBER else 0
            # features['tc_identifier'] = 1 if token_class == TokenClass.IDENTIFIER else 0
            # features['tc_key_value_pair'] = 1 if token_class == TokenClass.KEY_VALUE_PAIR else 0
            # features['tc_date_time'] = 1 if token_class == TokenClass.DATE_TIME else 0
            # features['tc_location'] = 1 if token_class == TokenClass.LOCATION else 0
            # features['tc_variable'] = 1 if token_class == TokenClass.VARIABLE else 0
            # features['tc_symbol'] = 1 if token_class == TokenClass.SYMBOL else 0
            # features['tc_punctuation'] = 1 if token_class == TokenClass.PUNCTUATION else 0
            # features['tc_misc'] = 1 if token_class == TokenClass.MISC else 0
            # features['tc_unknown'] = 1 if token_class == TokenClass.UNKNOWN else 0


            #features['upcase'] = 1 if word[0].isupper() else 0

            features['has_upper'] = 1 if re.search(r'[A-Z]',word) else 0

            # camel_case=re.compile(r'_*[a-zA-Z]+[a-z]([A-Z][a-z]+)+\d*')
            # snake_case=re.compile(r'_*[a-zA-Z]+(_[a-zA-Z]+)+\d*')
            # kebap_case=re.compile(r'[a-zA-Z]+(-[a-zA-Z]+)+\d*')
            # word_digit_mix=re.compile(r'(.*[a-zA-Z_\-/]+[0-9]+.*)|(.*[0-9]+[a-zA-Z_\-/]+.*)')
            # features['is-var']=1 if camel_case.fullmatch(word) or snake_case.fullmatch(word) or kebap_case.fullmatch(word) or word_digit_mix.fullmatch(word) else 0

            path_regex=re.compile(r'\w*:?([\.\/\\]+[\w\-:]+)+')
            features['is-path']=1 if path_regex.fullmatch(word) else 0

            # For better distinguish between 'to' as ADP and PART
            features['is_to']=1 if word.lower() == 'to' else 0

            #features['has_equal_sign'] = 1 if re.search(r'=',word) else 0


            #features['number'] = 1 if is_number(word) else 0
            #features['number'] = 1 if word.isdigit() else 0
            #features['number'] = 1 if word.isdigit() or features['mask_type']=='Number' else 0

            features['contains_number'] = 1 if re.search(r'[0-9]',word) else 0
            
            #features['is_punct'] = 1 if re.fullmatch(r'['+string.punctuation+']',word) else 0

            features['contains_punct']=1 if re.search(r'['+string.punctuation+']',word) else 0

            punct_chars=re.escape(r""".,;:!?()[]{}_…“”‘’"'/\|·«»`~¿¡•""")
            #features['is_punct'] = 1 if re.fullmatch(r'['+punct_chars+']',word) else 0
            sym_chars=re.escape(r"""+-=*^%$&§¤#@<>©®™°±×÷√∞∑∏∫∆µπΩ≠≈∈∩∪⊂⊃∅∇⊕⊗⇒⇔""")
            #features['is_sym'] = 1 if re.fullmatch(r'['+sym_chars+']',word) else 0
            #features['is_dash']=1 if re.fullmatch(r'[-]',word) else 0

            #features['key_value'] = 1 if re.search(r'[=:]',word) else 0

            # ideas from: https://www.geeksforgeeks.org/conditional-random-fields-crfs-for-pos-tagging-in-nlp/

            features['is_first'] = i == 0
            features['is_last'] = i == len(words) - 1

            features['all_caps'] = 1 if word.upper() == word else 0
            features['all_lower'] = 1 if word.lower() == word else 0

            #features['prev_word']= '' if i == 0 else tagged_sent[i-1][0]

            # Next word to better distinguish between 'to' as ADP and PART
            features['next_word']= '' if i == len(words)-1 else words[i+1]
            
            features['prev_char']= '' if i == 0 else words[i-1][-1]
            features['next_char']= '' if i == len(words)-1 else words[i+1][0]

            features['prefix-1'] = word[0]
            features['prefix-2'] = word[:2]
            # features['prefix-3'] = word[:3]

            features['suffix-1'] = word[-1]
            features['suffix-2'] = word[-2:]
            features['suffix-3'] = word[-3:]
            #features['suffix-4'] = word[-4:]
            
            
            word_lower = word.lower()
            # features['word'] = word
            features['word.lower'] = word_lower
            # features['word.isupper'] = str(word.isupper())
            # features['word.istitle'] = str(word.istitle())
            # features['word.isdigit'] = str(word.isdigit())

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
            # else:
            #     features['BOS'] = 'True'  # Beginning of sentence

            if i < len(words) - 1:
                # features['next_word'] = words[i + 1].lower()
                features['next_is_upper'] = str(words[i + 1].isupper())
            # else:
            #     features['EOS'] = 'True'  # End of sentence

            # Shape-based features
            features['word_shape'] = get_shape(word)

            # features['has_hyphen'] = str('-' in word)
            # features['has_digit'] = str(any(char.isdigit() for char in word))
            # # features['has_alpha'] = str(any(char.isalpha() for char in word))
            # features['is_short'] = str(len(word) <= 3)  # Often INTJ/PART
            # features['is_long'] = str(len(word) >= 10)  # Often ADJ

            # particles = {'not', 'off', 'up', 'down'}
            # interjections = {'oh', 'ah', 'wow', 'hey', 'oops', 'ouch', 'ok', 'bye', 'yes'}
            adjective_suffixes = ('ous', 'ful', 'ive', 'able', 'al', 'ic', 'less', 'ish')

            # features['is_particle'] = str(word_lower in particles)
            # features['is_interjection'] = str(word_lower in interjections)
            features['adj_suffix_match'] = str(any(word_lower.endswith(suf) for suf in adjective_suffixes))

            noun_suffixes = ('tion', 'ment', 'ness', 'ity', 'ship', 'age', 'ism', 'ence', 'ance', 'hood', 'dom')
            features['noun_suffix'] = str(any(word_lower.endswith(suf) for suf in noun_suffixes))

            # e.g., "the big ___" → likely NOUN
            determiners = {'the', 'a', 'an', 'this', 'that', 'these', 'those'}
            features['prev_is_determiner'] = str(i > 0 and words[i-1].lower() in determiners)

            # if i > 1:
            #     features['prev2_word'] = words[i-2].lower()
            # if i < len(words) - 2:
            #     features['next2_word'] = words[i+2].lower()
            
            #features['shape_affix'] = get_shape_affix(word)
            
            #features['word.no_digits'] = re.sub(r'\d', '0', word.lower())
            #features['digit_count'] = str(sum(c.isdigit() for c in word))
            #features['starts_with_digit'] = str(word[0].isdigit())
            #features['digit_pattern'] = re.sub(r'\d+', '0', word.lower())  # collapses "2023rd" to "0rd"
            #features['word.nodigits'] = re.sub(r'\d+', '', word.lower())  # "R2D2" → "rd"

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

# def get_shape_affix(word: str) -> str:
#     shape = ''
#     for char in word:
#         if char.isupper():
#             shape += 'X'
#         elif char.islower():
#             shape += 'x'
#         elif char.isdigit():
#             shape += 'd'
#         else:
#             shape += '_'
    
#     # Combine with prefix/suffix
#     suffix = word[-3:].lower() if len(word) > 3 else word.lower()
#     prefix = word[:3].lower() if len(word) > 3 else word.lower()
    
#     return f"{shape}_{prefix}_{suffix}"