from poslog import AbstractPosTagger
from util.pos.tagset_mapping import unify_ptb_tags

import logging
logger = logging.getLogger(__name__)

######################
# NLTK
######################

import nltk
from .tagset_mapping import ptb2upos

class NLTKPosTagger(AbstractPosTagger):
    def __init__(self):
        logger.info("Initializing NLTKPosTagger")
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger_eng')
        # these resulting from lookup errors trying to pos-tag
        try:
            nltk.data.find('taggers/universal_tagset')
        except LookupError:
            nltk.download('universal_tagset')        
        logger.info("NLTKPosTagger initialized")

    def pos_tag(self,tokens:list[str], tagset='upos')->list[str]:
        tags=[tag for _, tag in nltk.pos_tag(tokens)]
        match tagset:
            case 'upos':
                return ptb2upos(tags)
            case 'ptb':
                return tags
            case _:
                raise ValueError(f"Unknown tagset: {tagset}")

######################
# Stanza
######################
# see: https://github.com/stanfordnlp/stanza

import stanza
from stanza.models.common.doc import Document, Sentence, Word
from stanza.resources.common import DEFAULT_MODEL_DIR
import os

class StanzaPosTagger(AbstractPosTagger):
    def __init__(self):
        logger.info("Initializing StanzaPosTagger")

        #if dir not exists, it downloads the models
        if not os.path.exists(DEFAULT_MODEL_DIR):
            # downloads 1.13 GB to your user directory
            stanza.download('en')

        self.nlp = stanza.Pipeline('en', processors='tokenize,pos', tokenize_pretokenized=True)#, no_ssplit=False)
        logger.info("StanzaPosTagger initialized")

    def pos_tag(self,tokens:list[str], tagset='upos')->list[str]:
        # Note to set pretokenized=True in pipeline and give then list of list of tokens;)
        doc:Document=self.nlp.process([tokens])
        sentences:list[Sentence]=doc.sentences or []
        words:list[Word]=[word for sentence in sentences for word in sentence.words]

        match tagset:
            case 'upos':
                return [word.upos for word in words]
            case 'ptb':
                return unify_ptb_tags([word.xpos for word in words])
            case _:
                raise ValueError(f"Unknown tagset: {tagset}")

######################
# Spacy
######################

import spacy
from spacy.language import Language
from spacy.tokens import Doc

class SpacyPosTagger(AbstractPosTagger):
    def __init__(self):
        logger.info("Initializing SpacyPosTagger")
        
        self.model="en_core_web_lg"
        try:
            #spacy.load("en_core_web_lg")
            # fixed version for not downloading the model again
            spacy.load(self.model)
        except (ImportError, OSError):
            #!python -m spacy download en_core_web_lg    
            spacy.cli.download(self.model)
    
        self.nlp:Language = spacy.load(self.model)
        logger.info("SpacyPosTagger initialized")

    def pos_tag(self,tokens:list[str], tagset='upos')->list[str]:
        # Note to call nlp again on the doc
        doc:Doc = self.nlp(Doc(self.nlp.vocab, words=tokens))
        match tagset:
            case 'upos':
                return [token.pos_ for token in doc]
            case 'ptb':
                return unify_ptb_tags([token.tag_ for token in doc])
            case _:
                raise ValueError(f"Unknown tagset: {tagset}")

######################
# HanTa
######################

from HanTa import HanoverTagger as ht
from .tagset_mapping import brown2upos, brown2ptb

class HanTaPosTagger(AbstractPosTagger):
    def __init__(self):
        logger.info("Initializing HanTaPosTagger")
        self.nlp = ht.HanoverTagger('morphmodel_en.pgz')
        logger.info("HanTaPosTagger initialized")

    def pos_tag(self,tokens:list[str], tagset='upos')->list[str]:
        tags = self.nlp.tag_sent(tokens, taglevel=1)
        match tagset:
            case 'upos':
                return brown2upos([tag[2] for tag in tags])
            case 'ptb':
                return brown2ptb([tag[2] for tag in tags])
            case _:
                raise ValueError(f"Unknown tagset: {tagset}")

######################
# TreeTagger
######################

import os
from treetaggerwrapper import TreeTagger
from treetaggerwrapper import Tag, NotTag, make_tags
from importlib.util import find_spec
from .tagset_mapping import tt_ptb2ptb, tt_ptb2upos

class TreeTaggerPosTagger(AbstractPosTagger):
    def __init__(self):
        logger.info("Initializing TreeTaggerPosTagger")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        lib_path="tree-tagger"
        self.treetagger_dir=os.path.join(dir_path, lib_path)
        if not os.path.exists(self.treetagger_dir):
            self.install_and_fix_treetagger()        
        self.nlp = TreeTagger(TAGLANG='en', TAGDIR=self.treetagger_dir)
        logger.info("TreeTaggerPosTagger initialized")

    def install_and_fix_treetagger(self):
        # https://www.cis.lmu.de/~schmid/tools/TreeTagger/#download
        tagger_package_url='https://www.cis.lmu.de/~schmid/tools/TreeTagger/data/tree-tagger-MacOSX-Intel-3.2.3.tar.gz'
        tagging_script_url='https://www.cis.lmu.de/~schmid/tools/TreeTagger/data/tagger-scripts.tar.gz'
        installing_script_url='https://www.cis.lmu.de/~schmid/tools/TreeTagger/data/install-tagger.sh'
        parameter_file_en_penn_url='https://www.cis.lmu.de/~schmid/tools/TreeTagger/data/english.par.gz'

        def download_file(url:str, target_dir:str=None):
            #file_name=url.split('/')[-1]
            #if target_dir:
            #    file_name=os.path.join(target_dir, file_name)
            #cmd=f'wget {url} -O {file_name}'
            cmd=f'cd {target_dir} && curl -O {url}'
            print(f"Downloading file: {cmd}")
            # !{cmd}
            os.system(cmd)
            
        cmd=f"mkdir -p {self.treetagger_dir}"
        print(f"Creating directory: {cmd}")
        #!{cmd}
        os.system(cmd)

        download_file(tagger_package_url, self.treetagger_dir)
        download_file(tagging_script_url, self.treetagger_dir)
        download_file(installing_script_url, self.treetagger_dir)
        download_file(parameter_file_en_penn_url, self.treetagger_dir)

        # install
        cmd=f'cd {self.treetagger_dir} && sh install-tagger.sh'
        print(f"Installing TreeTagger: {cmd}")
        #!{cmd}
        os.system(cmd)

        # test
        cmd=f"cd {self.treetagger_dir} && echo 'Hello world!' | cmd/tree-tagger-english"
        print(f"Testing TreeTagger: {cmd}")
        #!{cmd}
        os.system(cmd)

        ### Fix
        file=find_spec("treetaggerwrapper").origin
        backup_file=file+'.bak'
        if not os.path.exists(backup_file):
            print(f"Replacing line in file: {file}")
            # currently it’s line 544
            old_line='g_config = configparser.SafeConfigParser()'
            new_line='g_config = configparser.ConfigParser()'

            lib_lines = []
            with open(file,'r') as f:
                lib_lines = f.readlines()

            for i,line in enumerate(lib_lines):
                if line.strip() == old_line:
                    lib_lines[i] = new_line
                    break

            print(f"Creating backup file: {backup_file}")
            os.rename(file, backup_file)

            with open(file,'w') as f:
                f.writelines(lib_lines)
            print("Done.")
        else:
            print(f"File already modified: {file}")

    def pos_tag(self,tokens:list[str], tagset='upos')->list[str]:
        tags_string = self.nlp.tag_text(tokens, nosgmlsplit=True, notagurl=True, notagemail=True, notagip=True, notagdns=True, tagonly=True)
        tags:list[Tag] = make_tags(tags_string)
        # if tag is type NoTag create new tag, else copy tag
        tags = [tag if type(tag) != NotTag else Tag(tag.what, '_','_') for tag in tags]
        match tagset:
            case 'upos':
                return tt_ptb2upos([tag.pos for tag in tags])
            case 'ptb':
                return tt_ptb2ptb([tag.pos for tag in tags])
            case _:
                raise ValueError(f"Unknown tagset: {tagset}")

