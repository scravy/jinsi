import re
import sys
import textwrap

from jinsi import __pkginfo__
from jinsi import parse_yaml, parse_file, render_json, render_yaml


def print_version():
    print(f"jinsi {__pkginfo__.version}")


def print_help():
    print(textwrap.dedent(f"""
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


def main():
    args = []
    env = {}
    fmt_json = False
    args_it = iter(sys.argv)
    next(args_it)
    opt_parsing = True
    for arg in args_it:
        if arg == "--":
            opt_parsing = False
            continue
        if opt_parsing:
            if arg in ("-v", "-version", "--version"):
                print_version()
                return
            if arg in ("-h", "-help", "--help"):
                print_help()
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
    for arg in args:
        if arg == '-':
            doc = parse_yaml(sys.stdin.read())
        else:
            doc = parse_file(arg)
        if fmt_json:
            print(render_json(doc, **env))
        else:
            print("---")
            print(render_yaml(doc, **env))
