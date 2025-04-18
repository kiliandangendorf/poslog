from abc import ABC, abstractmethod

import logging
logger = logging.getLogger(__name__)

class AbstractPosTagger(ABC):
    @abstractmethod
    def pos_tag(self,tokens:list[str], tagset='upos')->list[str]:
        pass

    def pos_tag_upos(self,tokens:list[str])->list[str]:
        return self.pos_tag(tokens, tagset='upos')

    def pos_tag_ptb(self,tokens:list[str])->list[str]:
        return self.pos_tag(tokens, tagset='ptb')