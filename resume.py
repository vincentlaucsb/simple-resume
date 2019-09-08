from enum import Enum
from functools import partial

import chevron
import click
import yaml

class Output(Enum):
    HTML = 1
    TEX  = 2

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

def process_strings(parent: dict, process_func):
    children = [ parent ]

    # Finds strings by performing level-order traversal of YAML
    while children:
        current = children.pop()
        if type(current) is dict:
            items = current.items()
        elif type(current) is list:
            items = enumerate(current)

        for k, v in items:
            if type(v) is str:
                current[k] = process_func(v)
            elif type(v) is list or type(v) is dict:
                children.append(v)

def macro(text: str, render, template: str):
    args = render(text)
    args = args.split("||")
    return template.format(*args)

def if_not_empty(text: str, render):
    args = render(text)
    args = args.split("||")
    if args[0]:
        return args[1]

    return ""

class Resume:
    def __init__(self, mode: Output):
        self.template = ''
        self.resume = {}
        self.partials = {}
        self.mode = mode
    
    def load(self, template: str, data: str, config=''):
        self._load_resume_template(template)
        self._load_resume_data(data)
        self._load_resume_config(config)
        self.resume["IfNotEmpty"] = if_not_empty

    def _get_process_func(self):
        def new_string_tex(s):
            return s.replace("#", "\#")

        if self.mode == Output.HTML:
            return lambda s: s.replace("--", "&ndash;")
        elif self.mode == Output.TEX:
            return new_string_tex

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
                process_strings(self.resume, self._get_process_func())
                process_list_strings(self.resume)
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

@click.command()
@click.option("--data", default="resume.yaml", help="Resume data file")
@click.option("--template", default="resume.html", help="Resume template file")
@click.option("--config", default="config.yaml", help="Generator configuration options")
def main(data, template, config):
    mode = None
    if template.split(".")[-1] == 'html':
        mode = Output.HTML
    elif template.split(".")[-1] == "tex":
        mode = Output.TEX

    generator = Resume(mode)
    generator.load(template, data, config=config)
    print(generator.render())

if __name__ == "__main__":
    main()