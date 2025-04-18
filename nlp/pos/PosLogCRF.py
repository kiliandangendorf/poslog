from sklearn_crfsuite import CRF
import pickle
import os
from nlp.pos import KnownWordsDetector, RegexTokenClassMatcher
from nlp.pos import AbstractPosTagger
import logging
import re # TODO
import string # TODO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PosLogCRF(AbstractPosTagger):
    DEFAULT_MODEL_PATH='models'
    DEFAULT_MODEL='pos_log_upos_crf_63_model'

    def __init__(self, model_path:str=None):    
        self.model_path = self._get_model_path(model_path)
        self.crf = None
        self.kwdet=KnownWordsDetector()
        self.rgtcm=RegexTokenClassMatcher()

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
            features['kind_of_known_word'] = self.kwdet.kind_of_known_word(word).value

            #features['mask_type'] = get_mask_for_token(word) or 'unknown'
            #features['mask_type']=masker._determine_token_type(word).value
            features['word_class'] = self.rgtcm.token_class(word).value

            #features['upcase'] = 1 if word[0].isupper() else 0

            features['has_upper'] = 1 if re.search(r'[A-Z]',word) else 0

            #features['number'] = 1 if is_number(word) else 0
            features['number'] = 1 if word.isdigit() else 0
            #features['number'] = 1 if word.isdigit() or features['mask_type']=='Number' else 0

            features['contains_number'] = 1 if re.search(r'[0-9]',word) else 0
            
            #features['is_punct'] = 1 if re.fullmatch(r'['+string.punctuation+']',word) else 0

            features['contains_punct']=1 if re.search(r'['+string.punctuation+']',word) else 0

            #features['key_value'] = 1 if re.search(r'[=:]',word) else 0

            # ideas from: https://www.geeksforgeeks.org/conditional-random-fields-crfs-for-pos-tagging-in-nlp/

            features['is_first'] = i == 0
            features['is_last'] = i == len(words) - 1

            features['all_caps'] = 1 if word.upper() == word else 0
            features['all_lower'] = 1 if word.lower() == word else 0

            # features['prev_word']= '' if i == 0 else tagged_sent[i-1][0]
            # features['next_word']= '' if i == len(tagged_sent)-1 else tagged_sent[i+1][0]
            features['prev_char']= '' if i == 0 else words[i-1][0][-1]
            features['next_char']= '' if i == len(words)-1 else words[i+1][0][0]

            features['prefix-1'] = word[0]
            features['prefix-2'] = word[:2]
            # features['prefix-3'] = word[:3]

            features['suffix-1'] = word[-1]
            features['suffix-2'] = word[-2:]
            # features['suffix-3'] = word[-3:]

            features_list.append(features)
        
        return features_list        

    