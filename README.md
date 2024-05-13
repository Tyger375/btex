# btex

A latex superset.

## How to install

You can simply install btex with the pip package manager
```python
pip install btex
```

## Get started

The language is very similar to latex.\
If you want to learn btex, take a look at the examples, I've also made a visual studio code extension for syntax highligthing and snippets.

## Macros

Macros are predefined variables in the btex interpreter which will be ignored by the program and instantly converted into the latex alternative.\
Macros are surrounded by double $, you can find a list of all the supported macros in the main python file of the interpreter.
\
Some examples of macros:
```
$$infinity$$ -> the infinity symbol
$$textwidth$$ -> the \textwidth unit
$$dot$$ -> the dot product symbol for math expressions
$$percent$$ -> since the % symbol is used in latex for comments, you can escape it using this macro
```

**NOTE**: if the document doesn't format as you want, you can force it to place some characters:
```
$$fs$$ -> forces a space
$$fn$$ -> forces a newline (putting \\)
```

## Env

Some latex libraries can have some variables to set for customization.
Since btex automatically imports used libraries without needing to include them manually, you can set some variables with the env.
\
You can set them in the file
```
@env {
    pdftitle = Document\
    var = value\
}
```
Or using a file
```
@env .env\
```
These are the variables you can change

| Var name    | Description |
| ----------- | ----------- |
| pdftitle    | Used in the hyperref package `\hypersetup{pdftitle={VAR}` |


## Using components not yet supported

Since this project is open source, if you want to use a component that is not available on btex, you can clone this repository and add it by yourself, or just open an issue asking me to do it. \
However, if you do really need a component, you can use the @latex attribute
```
@latex {
    your latex code
}
```
Everything you write in this block, will be ignored by the btex interpreter and will be put exactly how it is in the .tex output file.