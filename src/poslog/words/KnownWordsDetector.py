from enum import Enum
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.corpus import words
import nltk

from pathlib import Path

import logging
logger = logging.getLogger(__name__)

class WordKind(Enum):
    STOP_WORD = 'stopword'
    WORD_NET = 'wordnet'
    WORDS_DICTIONARY = 'words_dictionary'
    DOMAIN_WORD = 'domain_word'
    NUMBER = 'number'
    UNKNOWN = 'unknown'

class KnownWordsDetector:

    def __init__(self, case_sensitive: bool = False):
        corpora_deps = ['words', 'stopwords', 'wordnet']
        for dependency in corpora_deps:
            try:
                nltk.data.find(f'corpora/{dependency}')
            except LookupError:
                logger.info(f"Initializing {self.__class__.__name__}")
                logger.info(f"Did not found corpora '{dependency}'. Downloading...")
                nltk.download(dependency)

        self.case_sensitive = case_sensitive
        # dict lookup is faster than list lookup
        self.words_dictionary: dict[str, None] = dict.fromkeys(
            [w.lower() for w in words.words()], None)
        self.stopwords_dict: dict[str, None] = dict.fromkeys(
            stopwords.words('english'), None)
        self.domain_words: dict[str, None] = self._read_domain_words()

    ######################
    # Known Words
    ######################

    def kind_of_known_words(self, tokens: list[str]) -> list[WordKind]:
        return [self.kind_of_known_word(token) for token in tokens]
    
    def kind_of_known_word(self, token: str) -> WordKind:
        if token.lower() in self.stopwords_dict:
            return WordKind.STOP_WORD
        # since this list build from words not in wordnet, we can do it before wordnet
        if self.is_domain_word(token):
            return WordKind.DOMAIN_WORD
        if self._is_number(token):
            return WordKind.NUMBER
        if wordnet.synsets(token):
            return WordKind.WORD_NET
        if token.lower() in self.words_dictionary:
            return WordKind.WORDS_DICTIONARY
        return WordKind.UNKNOWN

    # Note: Some integer numbers are already covered by wordnet
    def is_known_word(self, token: str):
        if self.kind_of_known_word(token) != WordKind.UNKNOWN:
            return True
        return False

    def _is_number(self, token: str) -> bool:
        try:
            # Remove common thousands separators (', and ')
            clean_t = token.replace(",", "").replace("'", "").replace(" ", "")
            float(clean_t)
            return True
        except:
            return False

    ######################
    # Domain Words
    ######################

    def _read_domain_words(self):
        DOMAIN_WORDS_FILENAME = "known_domain_words.txt"
        domain_words_file = Path(__file__).parent / DOMAIN_WORDS_FILENAME
        if not domain_words_file.exists():
            raise FileNotFoundError(
                f"Domain words file {domain_words_file} does not exist.")
        # load line wise from file
        with domain_words_file.open('r') as file:
            if self.case_sensitive:
                return [line.strip() for line in file.readlines()]
            else:
                return [line.strip().lower() for line in file.readlines()]

    def is_domain_word(self, word: str) -> bool:
        if not self.case_sensitive:
            word = word.lower()
        return word in self.domain_words
    
