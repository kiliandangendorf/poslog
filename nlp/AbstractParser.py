from abc import ABC, abstractmethod
from typing import NamedTuple

class EventTemplate(NamedTuple):
    template:str
    revision:int # revision means the version of the template, so we can keep track of the changes, when finding a better template

class LogCluster(NamedTuple):
    cluster_id:int
    #n_grams:set[str]
    log_line_ids:list[int]
    event_templates:list[EventTemplate]


class AbstractParser(ABC):
    @abstractmethod
    def add_log_message(self,log_line:str)->LogCluster:
        pass

    @abstractmethod
    def train(self, log_messages:list[str])->None:
        pass
    
    @abstractmethod
    def get_parameter_list(self, log_template:str, log_message:str)->list[str]:
        pass

    @abstractmethod
    def get_log_clusters(self)->list[LogCluster]:
        pass

    @abstractmethod
    def get_escape_chars(self)->tuple[str,str]:
        pass
