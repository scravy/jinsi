import re
import sys

from jinsi import load_yaml, load_file, render_json, render_yaml


def main():
    args = []
    env = {}
    fmt_json = False
    args_it = iter(sys.argv)
    next(args_it)
    for arg in args_it:
        if arg in ("-j", "-json", "--json"):
            fmt_json = True
            continue
        if m := re.match(r"([^=]+)=(.*)", arg):
            key = m.group(1)
            val = m.group(2)
            env[key] = val
            continue
        args.append(arg)
    for arg in args:
        if arg == '-':
            doc = load_yaml(sys.stdin.read())
        else:
            doc = load_file(arg)
        if fmt_json:
            print(render_json(doc, **env))
        else:
            print("---")
            print(render_yaml(doc, **env))


main()
