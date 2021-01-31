import os
import re
import sys
import textwrap

from jinsi import *

import jinsi


def print_version(*, _print=print):
    _print(f"jinsi {jinsi.__version__}")


def print_help(*, _print=print):
    _print(textwrap.dedent(f"""
        {sys.argv[0]} [-j] [args...]
    
        ...where each argument may be:
        
          - a filename
          - a dash (to denote reading from standard input)
          - a variable binding of the form "key=value"
    
        The following options are recognized:
        
          -j  --json      Format output as JSON lines
        
        Standalone options:
    
          -v  --version   Print version information
          -h  --help      Print this help screen
        
    """))


def main(*argv, _print=print, _open=open, _stdin=sys.stdin):
    args = []
    env = {}
    fmt_json = False
    if argv:
        args_it = iter(argv)
    else:
        args_it = iter(sys.argv)
        next(args_it)
    opt_parsing = True
    for arg in args_it:
        if arg == "--":
            opt_parsing = False
            continue
        if opt_parsing:
            if arg in ("help", "version") and not os.path.exists(arg):
                arg = f"--{arg}"
            if arg in ("-v", "-version", "--version"):
                print_version(_print=_print)
                return
            if arg in ("-h", "-help", "--help"):
                print_help(_print=_print)
                return
            if arg in ("-j", "-json", "--json"):
                fmt_json = True
                continue
            m = re.match(r"([^=]+)=(.*)", arg)
            if m:
                key = m.group(1)
                val = m.group(2)
                env[key] = val
                continue
        args.append(arg)
    if not args:
        args = ["-"]
    count = 0
    for arg in args:
        if arg == '-':
            docs = render_string(_stdin.read(), args=env, as_json=fmt_json)
        else:
            docs = render_file(arg, args=env, as_json=fmt_json, _open=_open)
        for doc in docs:
            count += 1
            if fmt_json:
                _print(doc)
            else:
                if count > 1:
                    _print("---")
                if doc[-1] == '\n':
                    _print(doc, end='')
                else:
                    _print(doc)
