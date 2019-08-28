from functools import partial

import argparse
import chevron
import yaml

# parser = argparse.ArgumentParser(description='Resume generator')

def process_list_strings(parent: dict):
    children = [ parent ]
    list_with_str = list()

    # Build up list of items to process
    while children:
        current = children.pop()
        if type(current) is dict:
            for v in current.values():
                if type(v) is list or type(v) is dict:
                    children.append(v)
        elif type(current) is list:
            for item in current:
                if type(item) is str:
                    list_with_str.append(current)
                    break
                elif type(item) is list or type(item) is dict:
                    children.append(item)

    for lst in list_with_str:
        for i, item in enumerate(lst):
            if type(item) is str:
                # Replace string
                lst[i] = {
                    "Item": item,
                    "Order": i,
                    "IsLast": bool(i == len(lst) - 1)
                }

def process_strings(parent: dict):
    children = [ parent ]

    # Build up list of items to process
    while children:
        current = children.pop()
        if type(current) is dict:
            for k, v in current.items():
                if type(v) is list or type(v) is dict:
                    children.append(v)
                elif type(v) is str:
                    current[k] = v.replace("--", "&ndash;")

        elif type(current) is list:
            for i, item in enumerate(current):
                if type(item) is str:
                    current[i] = item.replace("--", "&ndash;")
                elif type(item) is list or type(item) is dict:
                    children.append(item)

def macro(text: str, render, template: str):
    args = render(text)
    args = args.split("||")
    return template.format(*args)

template = ''
with open('resume.html', 'r') as infile:
    template = ''.join(infile.readlines())

resume = {}
with open('resume.yaml', 'r') as infile:
    resume = yaml.safe_load(infile)
    process_strings(resume)
    process_list_strings(resume)

config = {}
with open('config.yaml', 'r') as infile:
    config = yaml.safe_load(infile)
    for k, v in config['Lambdas'].items():
        resume[k] = partial(macro, template=v)

    print(chevron.render(template, resume, partials_dict=config['Partials']))