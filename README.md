# btex

A latex superset.

## How to install

You can simply install btex with the pip package manager
```python
pip install btex
```

## Macros

Macros are predefined variables in the btex interpreter which will be ignore by the program and instantly converted into the latex alternative.\
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

## Using components not yet supported

Since this project is open source, if you want to use a component that is not available on btex, you can clone this repository and add it by yourself, or just open an issue asking me to do it. \
However, if you do really need a component, you can use the @latex component
```
@latex {
    your latex code
}
```
Everything you write in this block, will be ignored by the btex interpreter and will be put exactly how it is in the .tex output file.