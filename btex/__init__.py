from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import LoggingEventHandler, FileSystemEvent
import re, argparse, time, os

def eval_main_scope(c, n, b, format) -> tuple[bool, list[bool, bool, bool, str], str]:
    if format[0]:
        if format[3] == '*':
            if format[1]:
                if c == "*":
                    return True, [format[0], False, True, format[3]], "bf{"
                else:
                    return True, [format[0], False, format[2], format[3]], "it{" + c
            else:
                if c == "*":
                    if format[2]:
                        return True, [True, False, False, '*'], ""
                    else:
                        return True, [False, False, False, ' '], "}"
                else:
                    return True, [format[0], False, format[2], format[3]], c
        elif format[3] == "_":
            if c == "_":
                if format[2]:
                    return True, [True, False, False, '_'], ""
                else:
                    return True, [False, False, False, ' '], "}"
            else:
                return True, [format[0], False, format[2], format[3]], c
    if c == '*' and b != "\\":
        return True, [True, True, False, '*'], "\\text"
    elif c == '_' and b != "\\":
        return True, [True, False, False, '_'], "\\underline{"
    return False, [False, False, False, ' '], ""

vars = {
    "textwidth": "\\textwidth",
    "percent": "\\%",
    "fs": " ",
    "fn": "\\\\"
}

def resolve_scope(scope: str, isMath: bool = False):
    t = scope.replace("\n", "").replace("\t", "").replace("}", "}\\").replace("@", " \\@")
    l = []
    statement = ""
    opened = -1
    format = [False, False, False, ' ']
    for i in range(len(t)):
        c = t[i]
        n = t[i+1] if i+1 < len(t) else None
        b = t[i-1] if i-1 >= 0 else None
        isThisScope = opened == 0

        if isThisScope:
            if c == '\\' and n == '\\' and b != "}":
                statement += "\\\\"
                continue
            if isMath:
                if c == "*":
                    statement += "\\times"
                    continue
            else:
                _continue, f, toadd = eval_main_scope(c, n, b, format)
                format = f
                statement += toadd
                if _continue:
                    continue
        if (c == '\\' and n != '\\') and opened <= 0:
            if statement != "":
                l.append(statement)
            statement = ""
        elif c == '{':
            if opened != -1:
                statement += c
            opened += 1
        elif c == '}':
            if opened != 0:
                statement += c
            opened -= 1
        else:
            if statement == "" and c == ' ':
                continue
            statement += c
    if statement != "":
        l.append(statement)
    return l

def replace_macros(line: str):
    t = str(line)

    print(t)

    s = re.sub(r"{.*}", "", t)

    matches = re.findall(r"\$\$\w*\$\$", s)

    for match in matches:
        var = match[2:-2]
        if var in vars:
            t = line.replace(match, vars[var])

    return t

def eval_statement(line: str):
    t = replace_macros(line)

    statement = [item for item in t.split(" ") if item != ""]
    return statement

def exec_scope(scope):
    t = ""
    for s in scope:
        s2, newline = exec_line(s)
        t += s2
        if newline:
            t += "\n"
    return t

def documentclass(_, args):
    l = len(args)
    global docclass
    if l == 1:
        docclass = f"\\documentclass{{{args[0]}}}"
    else:
        docclass = f"\\documentclass{args[0]}{{{args[1]}}}"
    return "", True

def document(_, args):
    scope = resolve_scope(" ".join(args))
    t = exec_scope(scope)
    return f"\\begin{{document}}\n\n{t}\n\\end{{document}}", True

def enumerate(_, args):
    scope = resolve_scope(" ".join(args), True)
    t = exec_scope(scope)
    return f"\\begin{{enumerate}}\n{t}\n\\end{{enumerate}}", True

def math(_, args):
    scope = resolve_scope(" ".join(args), True)
    tryImport("amsmath")
    t = exec_scope(scope)
    return f"\\begin{{equation}}\n{t}\n\\end{{equation}}", True

def center(_, args):
    scope = resolve_scope(" ".join(args), True)
    t = exec_scope(scope)
    return f"\\begin{{center}}\n{t}\n\\end{{center}}", True

def sqrt(_, args):
    scope = resolve_scope("".join(args))
    t = exec_scope(scope)
    return f"\\sqrt{{{t[0:-1]}}}", True

def _split(_, args):
    tryImport("amsmath")
    scope = resolve_scope(" ".join(args), True)
    t = exec_scope(scope)
    return f"\\begin{{split}}\n{t}\n\\end{{split}}", True

def item(_, args):
    scope = resolve_scope(" ".join(args))
    t = exec_scope(scope)
    return f"\\item {t[0:-3]}", True

def binom(name, args):
    tryImport("amsmath")
    string = ' '.join(eval_statement(' '.join(args)))
    
    scope = resolve_scope(string.replace("\\", ""))

    if len(scope) != 2:
        print(f"Error in {name}")
        exit(1)

    first, second = scope

    f = exec_scope(resolve_scope(first))

    s = exec_scope(resolve_scope(second))
        
    return f"\\binom{{{f}}}{{{s}}}", True

def frac(name, args):
    string = ' '.join(eval_statement(' '.join(args)))
    
    scope = resolve_scope(string.replace("\\", ""))

    if len(scope) != 2:
        print(f"Error in {name}")
        exit(1)

    first, second = scope

    f = exec_scope(resolve_scope(first))

    s = exec_scope(resolve_scope(second))
        
    return f"\\frac{{{f}}}{{{s}}}", True

def section(name, args):
    string = ' '.join(eval_statement(' '.join(args)))
    match = re.match(r"\([^)]+\)", string)
    params = ""
    if match is not None:
        params = string[match.start():match.end()][1:-1]
        string = string[match.end():].strip()

    label = ""

    for param in params.split(","):
        if param == "":
            continue
        first, second = param.split("=")
        if first == "label":
            label = f"\\label{{{second}}}"

    
    return f"\\{name}{{{string}}}{label}\n", True

def figure(_, args):
    tryImport("float")
    string = ' '.join(eval_statement(' '.join(args)))
    match = re.match(r"\([^)]+\)", string)
    params = ""
    if match is not None:
        params = string[match.start():match.end()][1:-1]
        string = string[match.end():]

    #print(string)

    c = exec_scope(resolve_scope(string))

    p = ""
    if params != "":
        p = f"[{params}]"
    
    return f"\\begin{{figure}}{p}\n{c}\n\\end{{figure}}", True

def href(name, args):
    if len(args) < 2:
        print(f"Error in {name}")
        exit(1)
    first, *second = args
    second = " ".join(second)
    tryImport("hyperref")
    return f"\\href{{{first}}}{{{second}}}", False

def code(_, args):
    tryImport("xcolor")
    tryImport("listings")
    string = ' '.join(eval_statement(''.join(args)))
    match = re.match(r"\([^)]+\)", string)
    params = ""
    if match is not None:
        params = string[match.start():match.end()][1:-1]
        string = string[match.end():]

    parsed = {}

    for param in params.split(","):
        if param == "":
            continue
        first, second = param.split("=")
        if first == "label":
            second = f"{{{second}}}"
        parsed[first] = second

    p = ','.join(f"{key}={val}" for key, val in parsed.items())
    
    return f"\\lstinputlisting[{p}]{{{string}}}", True

def _import(_, args):
    if len(args) != 1:
        print("How many fucking parameters did you put?")
        exit(1)
    return f"\\usepackage{{{args[0]}}}", True

def use(_, args):
    tryImport("graphicx")
    s = ''.join(["{" + arg + "}" for arg in args])
    return f"\\graphicspath{{{s}}}", True

def usegraphics(_, args):
    string = ' '.join(eval_statement(''.join(args)))
    string = replace_macros(string)
    print(string, ''.join(args))
    match = re.match(r"\([^)]+\)", string)
    param = ""
    if match is not None:
        param = string[match.start():match.end()][1:-1]
        string = string[match.end():]

    tryImport("graphicx")

    return f"\\includegraphics[{param}]{{{string}}}", True

def itself(name, _):
    return f"\\{name}", False

def itselfnewline(name, _):
    return f"\\{name}", True

def simpleassign(name, args):
    s = ' '.join(args)
    return f"\\{name}{{{s}}}", False

def simpleassignnewline(name, args):
    s = ' '.join(args)
    return f"\\{name}{{{s}}}", True

items = {
    "class": documentclass,
    "document": document,
    "math": math,
    "center": center,
    "figure": figure,
    "paragraph": section,
    "section": section,
    "subsection": section,
    "subsubsection": section,
    "import": _import,
    "use": use,
    "graphic": usegraphics,
    "sqrt": sqrt,
    "split": _split,
    "binom": binom,
    "frac": frac,
    "tableofcontents": itselfnewline,
    "maketitle": itselfnewline,
    "newpage": itselfnewline,
    "title": simpleassignnewline,
    "author": simpleassignnewline,
    "date": simpleassignnewline,
    "list": enumerate,
    "item": item,
    "href": href,
    "code": code,
    "ref": simpleassign,
    "caption": simpleassignnewline,
    "centering": itselfnewline,
    "label": simpleassignnewline,
    # Texts
    "vspace": simpleassign,
    "tiny": itselfnewline,
    "scriptsize": itselfnewline,
    "footnotesize": itselfnewline,
    "small": itselfnewline,
    "normalsize": itselfnewline,
    "large": itselfnewline,
    "Large": itselfnewline,
    "LARGE": itselfnewline,
    "huge": itselfnewline,
    "Huge": itselfnewline
}

def exec_line(line):
    statement = [item for item in line.split(" ") if item != ""]

    #print(statement)
    
    if statement[0][0] == "@":
        ref = statement[0][1:]
        return items[ref](ref, statement[1:])
    
    return replace_macros(" ".join(statement)), True

docclass = ""

imports = []

def tryImport(module):
    if module in imports:
        return
    imports.append(module)

def eval_imports():
    final = ""
    for i in imports:
        label = f"\\usepackage{{{i}}}\n"
        if i == "hyperref":
            label += """
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,
    urlcolor=cyan,
    pdftitle={Overleaf Example},
    pdfpagemode=FullScreen,
}\n
"""
        if i == "listings":
            label += """
\definecolor{codegreen}{rgb}{0,0.6,0}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.95,0.95,0.92}

\lstdefinestyle{mystyle}{
    backgroundcolor=\color{backcolour},
    commentstyle=\color{codegreen},
    keywordstyle=\color{magenta},
    numberstyle=\\tiny\color{codegray},
    stringstyle=\color{codepurple},
    basicstyle=\\ttfamily\\footnotesize,
    breakatwhitespace=false,
    breaklines=true,
    captionpos=b,
    keepspaces=true,
    numbers=left,
    numbersep=5pt,
    showspaces=false,
    showstringspaces=false,
    showtabs=false,
    tabsize=2
}

\lstset{style=mystyle}
\n
"""
        final += label
    return final

def read(f: str):
    global text

    with open(f) as f:
        text = f.read()

    return text

def compile(text: str, to: str):
    split = resolve_scope(f"{{{text}}}")

    compiled = ""

    for i in split:
        s, newline = exec_line(i)
        compiled += s
        if newline:
            compiled += "\n"

    compiled = docclass + "\n" + eval_imports() + compiled

    with open(to, "w") as f:
        f.write(compiled)

programs = {
    "pdflatex": lambda include_dir, out_dir: f"pdflatex -file-line-error -interaction=nonstopmode -synctex=1 -output-format=pdf -quiet -include-directory={include_dir} -output-directory={out_dir}"
}

def buildPdf(_from: str, file: str, program: str):
    if not program in programs:
        print(f"Invalid program for building pdf: {program}")
        exit(1)
    include = os.path.abspath(os.path.dirname(_from))
    out = os.path.abspath(os.path.dirname(file))
    cmd = programs[program](include, out)
    os.system(f"{cmd} {file}")
    print("Built pdf")

def doWork(_from: str, to: str, toPdf: bool, program: str):
    f = read(_from)
    compile(f, to)
    if toPdf:
        buildPdf(_from, to, program)

def cli():
    parser = argparse.ArgumentParser("btex")
    
    parser.add_argument("filename", help="An integer will be increased by 1 and printed.", type=str)
    parser.add_argument("--to", help="file name output", default="out.tex", type=str)
    parser.add_argument("--watch", help="Watch file changes", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--pdf", help="Auto build tex file to pdf", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--program", help="What pdf building program to use", type=str, default="pdflatex")
    args = parser.parse_args()
    
    filename = args.filename
    to = args.to
    toPdf = args.pdf
    program = args.program

    doWork(filename, to, toPdf, program)

    if args.watch:
        event_handler = LoggingEventHandler()
        def on_modified(event: FileSystemEvent):
            if not event.src_path.endswith(filename):
                return
            doWork(filename, to, toPdf, program)
        
        event_handler.on_modified = on_modified
    

        observer = Observer()
        observer.schedule(event_handler, ".", recursive=False)
        observer.start()
        print("Started listening to changes")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == "__main__":
    cli()