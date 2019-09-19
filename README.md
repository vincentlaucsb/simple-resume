# simple-resume
A simple Python resume YAML generator using Mustache templates

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

### A Simple Example
That means given

```yaml
Name: Vincent La
Email: vincela9@gmail.com
LinkedIn: www.linkedin.com/in/vincent-la-sb
Website: www.vincela.com
Mobile: (510) 123-4567
Experience:
    - Employer: XYZ Corp
      Title: Software Engineer
      Date: January 2019
```

and

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{Name}}'s Resume</title>
</head>
<body>
    <header>
        <h1 id="name"><a href="http://{{Website}}">{{Name}}</a></h1>
        <p>
            <span>{{Address}}</span>
            <a href="mailto:{{Email}}"><span>{{Email}}</span></a>
            <span><a href="https://{{LinkedIn}}">{{LinkedIn}}</a></span>
            <span><a href="http://{{Website}}">{{Website}}</a></span>
        </p>
    </header>
</body>
</html>
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
