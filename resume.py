from functools import partial

import argparse
import chevron
import yaml

# parser = argparse.ArgumentParser(description='Resume generator')

'''
Given the root of a YAML document, find all sequences 
of strings and replace the individual strings with a mapping
'''
def process_list_strings(parent: dict):
    children = [ parent ]
    list_with_str = list()

    # Find string sequences by performing an iterative
    # level-order traversal
    while children:
        current = children.pop()
        if type(current) is dict:
            for v in [_v for _v in current.values()
                      if type(_v) is list or type(_v) is dict]:
                children.append(v)
        elif type(current) is list:
            for item in current:
                if type(item) is str:
                    # We have found a sequence containing a string
                    list_with_str.append(current)
                    break
                elif type(item) is list or type(item) is dict:
                    children.append(item)

    # Process target sequences
    for lst in list_with_str:
        for i, item in enumerate(lst):
            if type(item) is str:
                lst[i] = {
                    "Item": item,
                    "Order": i,
                    "IsLast": bool(i == len(lst) - 1)
                }

def process_strings(parent: dict):
    children = [ parent ]

    # Perform string processing actions
    def new_string(s) -> str:
        return s.replace("--", "&ndash;")

    # Finds strings by performing level-order traversal of YAML
    while children:
        current = children.pop()
        if type(current) is dict:
            items = current.items()
        elif type(current) is list:
            items = enumerate(current)

        for k, v in items:
            if type(v) is str:
                current[k] = new_string(v)
            elif type(v) is list or type(v) is dict:
                children.append(v)

def macro(text: str, render, template: str):
    args = render(text)
    args = args.split("||")
    return template.format(*args)

class Resume:
    def __init__(self):
        self.template = ''
        self.resume = {}
        self.partials = {}
    
    def load(self, template: str, data: str, config=''):
        self._load_resume_template(template)
        self._load_resume_data(data)
        self._load_resume_config(config)

    def _load_resume_template(self, file: str):
        try:
            with open(file, 'r') as infile:
                self.template = ''.join(infile.readlines())
        except FileNotFoundError:
            print(f'Couldn\'t find resume template "{file}"')

    def _load_resume_data(self, file: str):
        try:
            with open(file, 'r') as infile:
                self.resume = yaml.safe_load(infile)
                process_strings(self.resume)
                process_list_strings(self.resume)
                print(self.resume)
        except FileNotFoundError:
            print(f'Couldn\'t find resume data file "{file}"')
    
    def _load_resume_config(self, file: str):
        try:
            with open(file, 'r') as infile:
                config = yaml.safe_load(infile)
                self.partials = config['Partials']

                # Load lambdas
                for k, v in config['Lambdas'].items():
                    self.resume[k] = partial(macro, template=v)
        except KeyError:
            # Configuration file is optional
            pass
        except FileNotFoundError:
            # Configuration file is optional
            pass

    def render(self) -> str:
        return chevron.render(
            self.template,
            self.resume,
            partials_dict=self.partials)

if __name__ == "__main__":
    generator = Resume()
    generator.load("resume.html", "resume.yaml", config="config.yaml")
    print(generator.render())