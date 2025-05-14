import re

class NumbVar:
    def __init__(self):
        self.templates:dict[str,int]={}
        self.templates_count=0

    def parse(self, log_message:str)->tuple[str, int]:
        
        # replace all tokens containing digits
        template=re.sub(r'\S*\d+\S*', '<*>', log_message)

        # replace chains of variables
        template=re.sub(r'<\*>(.<\*>)*', '<*>', template)
        template=re.sub(r'\s+', ' ', template)

        if template not in self.templates:
            self.templates[template]=self.templates_count
            self.templates_count+=1

        template_id=self.templates[template]
        return template, template_id
    
    def get_templates_list(self)->list[str]:
        return list(self.templates.keys())

