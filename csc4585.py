from IPython.core.magic import register_cell_magic, register_line_magic
from IPython.display import clear_output
from termcolor import colored
from pathlib import Path

javac_flags = ["-Xlint:unchecked"]

@register_cell_magic
def bash(line, cell): get_ipython().system(cell)
    
import re
import os
from subprocess import call as call_

def call(args):
    print(colored(" ".join(args),"blue"))
    return call_(args)

fnames = []

@register_cell_magic
def flour(line, cell):
    home = Path.home()
    fname=f"{home}/.flour.tmp.mj"
    new_cell = ''
    pos = 0
    for g in re.finditer(r'\$\{input\("([^"]+)"\)\}', cell):
        val = input(g.group(1)+": ")
        new_cell += cell[pos:g.start()] + '"' + re.sub(r'"',r'\\"',re.sub(r'\\',r'\\\\',val)) + '"'
        pos = g.end()
    new_cell += cell[pos:]
    with open(fname,"w") as fd:
        print(new_cell, file=fd)
    clear_output()
    r = call(["java"] + ["-jar","/usr/local/flouri.jar",fname])

@register_cell_magic
def java(line, cell):
    global fnames
    home = Path.home()
    classes_dir = os.path.join(home, "classes")
    g = re.search(r'public\s+(?:abstract\s+|)(?:class|interface)\s+(\w+)', cell)
    assert g, "The cell must have a public class/interface"
    class_name = g.group(1)
    f_name = f"{class_name}.java"
    with open(f_name, "w") as fd:
        print(file=fd)
        print(cell,file=fd,end='')

    # Get rid of stuff that doesn't exist
    new_fnames = []
    for f in fnames:
        if os.path.exists(f):
            new_fnames += [f]
    fnames = new_fnames

    if f_name in fnames:
        r = call(["javac"] + javac_flags + ["-cp",classes_dir,"-d",classes_dir]+fnames)
    else:
        r = call(["javac"] + javac_flags + ["-cp",classes_dir,"-d",classes_dir,f_name]+fnames)
    if r != 0 and len(fnames) > 0 and fnames != [f_name]:
        print(colored("Trying again...","blue"))
        r = call(["javac"] + javac_flags + ["-cp",classes_dir,"-d",classes_dir,f_name])
    if r != 0:
        if f_name not in fnames:
            fnames += [f_name]
        return
    fnames = []
    p = re.search(r'^\s*package\s+(\S+);', cell)
    if p:
        package = p.group(1)+"."
    else:
        package = ""
    g = re.search(r'public\s+static\s+void\s+main', cell)
    if g:
        call(["java","-ea","-cp",classes_dir,package+class_name])

@register_line_magic
def edit_file(fname):
    from IPython.core.getipython import get_ipython
    shell = get_ipython()
    
    try:
        contents = "%%writefile "+fname+"\n"+re.sub(r'\n$','',open(fname, "r").read())
    except FileNotFoundError as e:
        pass
        #print("Creating file '%s'" % fname)
        #contents = "%%writefile "+fname

    payload = dict(
        source='set_next_input',
        text=contents,
        replace=True,
    )
    shell.payload_manager.write_payload(payload, single=True)

@register_cell_magic
def writec(line, cell):
    fname = line.strip()
    g = re.match(r'(.*/)?(.*)\.(cc|cpp|C|c|cxx)', fname)
    if g:
        dirname = g.group(1)
        if dirname is not None:
            os.makedirs(dirname, exist_ok=True)
        with open(fname, "w") as fd:
            print(cell.strip(), file=fd)
        fbase = g.group(2)
        suffix = g.group(3)
        if suffix == "c":
            r = call(["gcc","-o",fbase,fname,"-lpthread"])
        else:
            r = call(["g++","-std=c++17","-o",fbase,fname,"-lpthread"])
        if r == 0:
            call(["./"+fbase])
    else:
        print(colored("Bad suffix: line","red"))
