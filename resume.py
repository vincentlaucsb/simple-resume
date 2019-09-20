from enum import Enum
from functools import partial

import chevron
import click
import yaml

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

# A helper function which allows user-defined macros to be
# turned into Mustache lambdas
def macro(text: str, render, template: str):
    # Process Mustache syntax
    args = render(text)

    # Split rendered tax by "||" and treat each
    # individual item as a macro argument
    args = args.split("||")

    # print("Processing", args)

    # Pass arguments into user-defined macro
    return template.format(*args)

class Resume:
    def __init__(self, mode: str):
        self.template = ''
        self.replace = {}
        self.resume = {}
        self.partials = {}
        self.mode = mode
    
    def load(self, template: str, data: str, config=''):
        self._load_resume_template(template)
        self._load_resume_config(config)
        self._load_resume_data(data)

    def _load_resume_template(self, file: str):
        try:
            with open(file, 'r') as infile:
                self.template = ''.join(infile.readlines())
        except FileNotFoundError:
            print(f'Couldn\'t find resume template "{file}"')

    def _load_resume_data(self, file: str):
        try:
            with open(file, 'r') as infile:
                # Copy resume macros
                temp = self.resume
                self.resume = yaml.safe_load(infile)
                for k, v in temp.items():
                    self.resume[k] = temp[k]

                self._process_strings(self.resume)
                process_list_strings(self.resume)
        except FileNotFoundError:
            print(f'Couldn\'t find resume data file "{file}"')
    
    def _load_resume_config(self, file: str):
        try:
            with open(file, 'r') as infile:
                config = yaml.safe_load(infile)
                self.partials = config['Partials']

                # Load macros
                for k, v in config['Macros'].items():
                    # print(f"Loaded macro {k}", v)
                    self.resume[k] = partial(macro, template=v)

                # Load string replacements
                for k, v in config.items():

                    # File extensions are case-insensitive
                    if self.mode.lower() == k.lower():
                        self.replace = config[k]['Replace']

        except KeyError:
            # Configuration file is optional
            pass
        except FileNotFoundError:
            # Configuration file is optional
            pass

    ''' Performs string processing '''
    def _process_strings(self, parent: dict):
        children = [ parent ]

        # Function which processes an individual string
        def process(value: str) -> str:
            for k, v in self.replace.items():
                value = value.replace(k, v)

            return value

        # Finds strings by performing level-order traversal of YAML
        while children:
            current = children.pop()
            if type(current) is dict:
                items = current.items()
            elif type(current) is list:
                items = enumerate(current)

            for k, v in items:
                if type(v) is str:
                    current[k] = process(v) # Process the string
                elif type(v) is list or type(v) is dict:
                    children.append(v)
    
    ''' Render the resume '''
    def render(self) -> str:
        # print(self.resume)

        return chevron.render(
            self.template,
            self.resume,
            partials_dict=self.partials)

@click.command()
@click.option("--data", default="resume.yaml", help="Resume data file (default: 'resume.yaml')")
@click.option("--template", default="resume.html", help="Resume template file (default: 'resume.html')")
@click.option("--config", default="config.yaml", help="Optional configuration options (default: 'config.yaml')")
def main(data, template, config):
    file_ext = template.split(".")[-1]

    generator = Resume(file_ext)
    generator.load(template, data, config=config)
    print(generator.render())

if __name__ == "__main__":
    main()