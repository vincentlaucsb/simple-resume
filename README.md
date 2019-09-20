# simple-resume
A simple Python resume YAML generator using Mustache templates

## Motivation
I wanted to be able to save my resume in a readable data format but spin off multiple variants--based on different information and templates--easily.

## Usage
```
resume --help
Usage: resume.py [OPTIONS]

Options:
  --data TEXT      Resume data file
  --template TEXT  Resume template file
  --config TEXT    Generator configuration options
  --help           Show this message and exit.
```

## Set Up
This resume generator processes YAML files and [Mustache templates](http://mustache.github.io/mustache.5.html) to create your final product.

This repo contains some sample templates that you can copy and modify:
 * [HTML](/html)
 * [LaTeX](/tex)

### Iterating over lists containing strings
One issue I found with using Mustache to generate resumes was rendering lists of strings, since there was not a syntax to access the string inside the list. Furthermore, in some instances, I wanted to know if a string was the last item in a list. As a result, this resume generator processes YAML before as such:

```yaml
Responsibilities:
  - "Refactored code, fixed bugs, and created design documents"
  - Rewrote most of a key plugin to be faster and maintainable; resolved thread deadlocks
  - Designed and implemented embedded C++ software responsible for communicating between different hardware
```

```python
{
  "Responsibilities":
    [
      "Order": 0,
      "Item": "Refactored code, fixed bugs, and created design documents"
      "IsLast": false
    ],
    [ ... ],
    [
      "Order": 2,
      "Item": "Designed and implemented embedded C++ software responsible for communicating between different hardware",
      "IsLast": true
    ]
}
```

### A Simple Example
Here's a simple example of a YAML resume file and a corresponding template that pulls in data from that file.

<table>
  <thead>
    <th>YAML</th>
    <th>Template</th>
  </thead>
  <tbody>
  <tr>
  <td>
    
```yaml
Name: A. A. Ron Rodgers
Email: ...
LinkedIn: ...
Website: http://www.packers.com/
Mobile: (510) 123-4567
Experience:
    - Employer: GB Packing Corp
      Title: Software Engineer
      Date: August 2005 -- Present
Superpowers: 
    - 10x Programmer
    - Thought Leader
    - Synergy Promoter
    - Agile/SCRUM Grand Wizard
    - Rockstar Ninja
    - COBOL Programming
```

</td><td>

```html
<header>
    <h1 id="name"><a href="http://{{Website}}">{{Name}}</a></h1>
    <p>
        <span>{{Address}}</span>
        <a href="mailto:{{Email}}"><span>{{Email}}</span></a>
        <span><a href="https://{{LinkedIn}}">{{LinkedIn}}</a></span>
        <span><a href="http://{{Website}}">{{Website}}</a></span>
    </p>
</header>
<ul>
  {{#Superpowers}}
    <li>{{Item}}</li>
  {{/Superpowers}}
</ul>
```

</td></tr>
</tbody>
</table>

### `config.yaml`: Extensions to Mustache
In addition to a resume data file, you can also specify an optional configuration file (by default, is is `config.yaml`). This allows you to:
 * Define replacements for text sequences, i.e. replacing `--` with `&ndash;` for HTML documents or `%` with `\%` for Tex.
 * Define your own (partials)[http://mustache.github.io/mustache.5.html#Partials]
 * Define your own macros
 
#### Custom Macros
Macros in this resume generator are similar to macros in C and Latex. They act like Mustache partials, but allow you to specify exactly what arguments you want by separating them with two pipes. `{}` should be used as placeholders for arguments.

```yaml
Macros:
    Subsection: |
        <div class="subsection">
            <h3>{}</h3>
            <p class="subtitle">{}</p>
            {}
        </div>
    DateRange:
        <p>I worked here from {} to {}.</p>

```

```html
    {{#Subsection}}
      Argument 1 || Argument 2 || Argument 3
    {{/Subsection}}
    {{DateRange}}July 2014||August 2015{{/DateRange}}
```

## LaTeX Usage
Although HTML is used in the examples above, this resume generator can be used to create any text based document, like Latex. Since squiggly brackets are used a lot in Latex, it might make more sense to type out something like `<<variable>>` instead of `{{variable}}`.

It is possible to change the Mustache delimiter, for example:
```latex
%--------------------------------------
% Change delimiter from { to <
%--------------------------------------
{{=<< >>=}}

\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}

%...

%-----------EXPERIENCE-----------------
\section{Experience}
  \resumeSubHeadingListStart
  <<#Experience>>
    \resumeSubheading
      {<<Employer>>}{<<Location>>}
      {<<Title>>}{<<Date>>}
      \resumeItemListStart
        <<#Responsibilities>>
        \resumeItemSimple{<<Item>>}
        <</Responsibilities>>
      \resumeItemListEnd
  <</Experience>>
  \resumeSubHeadingListEnd

%...
```
