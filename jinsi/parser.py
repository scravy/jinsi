from __future__ import annotations

import re
from datetime import date, datetime
from inspect import getattr_static

import yaml

from .exceptions import MalformedEachError, MalformedNameError, NoParseError, NoSuchFunctionError
from .functions import Functions
from .nodes import *
from .util import merge, Dec


# noinspection PyMethodMayBeStatic
class Parser:

    def __init__(self):
        self.name_regex = "^[a-z]([_-]?[a-z0-9])*$"
        self.env_var_regex = "^[0-9_]*[A-Z][_A-Z0-9]*$"
        self.path = []

    def check_name(self, name):
        if not re.match(self.name_regex, name):
            raise MalformedNameError(name=name, expected=self.name_regex)

    def parse_node(self, obj: Any, parent: Node) -> Node:
        if isinstance(obj, list):
            return self.parse_sequence(obj, parent)
        if isinstance(obj, (type(None), bool, int, float, str, Dec, date, datetime)):
            return self.parse_constant(obj, parent)
        if '::include' in obj:
            includes = obj['::include']
            if isinstance(includes, str):
                includes = [includes]
            if not isinstance(includes, list):
                raise NoParseError()
            del obj['::include']
            docs = [obj]
            for include in includes:
                with open(include) as f:
                    docs.append(yaml.safe_load(f))
            obj = merge(*docs)
        key_set = set(obj.keys())
        if key_set == {'::all'}:
            return self.parse_all(obj['::all'], parent)
        if key_set == {'::any'}:
            return self.parse_any(obj['::any'], parent)
        if key_set == {'::when', '::then'} or key_set == {'::when', '::then', '::else'}:
            return self.parse_conditional(obj, parent)
        for keyword in ['::all', '::any', '::when', '::then']:
            if keyword in key_set:
                raise NoParseError()
        if '::else' in obj:
            return self.parse_else(obj, parent)
        if '::let' in obj:
            return self.parse_let(obj, parent)
        nodes = []
        remaining = {}
        # if ::when or ::then are here then NoParse - maybe?
        if '::ref' in obj:
            ref = obj['::ref']
            if isinstance(ref, str) and re.match(self.env_var_regex, ref):
                nodes.append(self.parse_get_env_var(obj, parent))
            elif isinstance(ref, str) and ref[:1] == '$' or isinstance(ref, list) and ref[0][:1] == '$':
                nodes.append(self.parse_get_dyn(obj, parent))
            else:
                nodes.append(self.parse_get_let(obj, parent))
        for key, value in obj.items():
            if key[:8] == "::format":
                nodes.append(self.parse_format(value, parent))
            elif key[:6] == "::call":
                nodes.append(self.parse_application(key, value, parent))
            elif key[:6] == "::each":
                nodes.append(self.parse_each(key, value, parent))
            elif len(key) > 2 and key[:2] == "::":
                if key not in {"::ref", "::call", "::each", "::format"}:
                    nodes.append(self.parse_function_application(key, value, parent))
            else:
                remaining[key] = value

        if not remaining and len(nodes) == 1:
            return nodes[0]
        if not nodes:
            return self.parse_object(remaining, parent)
        nodes.append(self.parse_object(remaining, parent))
        merge_node = FunctionApplication(parent, function=Functions.merge)
        for node in nodes:
            node.parent = merge_node
        merge_node.args = nodes
        return merge_node

    def parse_constant(self, obj, parent: Node) -> Node:
        return Constant(parent, obj)

    def parse_get_let(self, obj, parent: Node) -> Node:
        path = obj['::ref']
        if isinstance(path, str):
            path = path.split(".")
        if not isinstance(path, list):
            raise NoParseError()
        self.check_name(path[0])
        return GetLet(parent, path)

    def parse_get_dyn(self, obj, parent: Node) -> Node:
        path = obj['::ref']
        if isinstance(path, str):
            path = path.split(".")
        if not isinstance(path, list):
            raise NoParseError()
        path[0] = path[0][1:]  # remove leading dollar sign
        self.check_name(path[0])
        return GetDyn(parent, path)

    def parse_get_env_var(self, obj, parent: Node) -> Node:
        path = obj['::ref']
        return GetEnvVar(parent, path)

    def parse_let(self, obj: Any, parent: Node) -> Node:
        node = Let(parent)
        remainder = {}
        for key, value in obj.items():
            if key == '::let':
                for var_key, var_value in value.items():
                    if var_key[:1] == "$":
                        var_key = var_key[1:]
                        self.check_name(var_key)
                        node.env[var_key] = self.parse_node(var_value, node)
                    else:
                        self.check_name(var_key)
                        node.let[var_key] = self.parse_node(var_value, node)
                continue
            remainder[key] = value
        node.body = self.parse_node(remainder, node)
        return node

    def parse_conditional(self, obj, parent: Node) -> Node:
        node = When(parent)
        node.when = self.parse_node(obj['::when'], node)
        node.then = self.parse_node(obj['::then'], node)
        if '::else' in obj:
            node.else_ = self.parse_node(obj['::else'], parent)
        return node

    def parse_all(self, obj, parent: Node) -> Node:
        if not isinstance(obj, list):
            raise NoParseError()
        node = All(parent)
        for item in obj:
            node.nodes.append(self.parse_node(item, node))
        return node

    def parse_any(self, obj, parent: Node) -> Node:
        if not isinstance(obj, list):
            raise NoParseError()
        node = Any(parent)
        for item in obj:
            node.nodes.append(self.parse_node(item, node))
        return node

    def parse_else(self, obj: Any, parent: Node) -> Node:
        node = Else(parent)
        remainder = {}
        for key, value in obj.items():
            if key == '::else':
                node.otherwise = self.parse_node(value, node)
                continue
            remainder[key] = value
        node.body = self.parse_node(remainder, node)
        return node

    def parse_object(self, obj, parent: Node) -> Node:
        node = Object(parent)
        for key, value in obj.items():
            node.children[key] = self.parse_node(value, node)
        return node

    def parse_sequence(self, obj, parent: Node) -> Node:
        seq = Sequence(parent)
        for item in obj:
            seq.elements.append(self.parse_node(item, seq))
        return seq

    def parse_function_application(self, key: str, args, parent: Node) -> Node:
        name = key[2:]
        if name[-1:] == "_":
            name = name[:-1]
        try:
            if not isinstance(getattr_static(Functions, name), staticmethod):
                raise NoSuchFunctionError(name)
        except AttributeError:
            raise NoSuchFunctionError(name)
        func = getattr(Functions, name)
        app = FunctionApplication(parent, func)
        if isinstance(args, list):
            for arg in args:
                app.args.append(self.parse_node(arg, app))
        else:
            if isinstance(args, str):
                app.args.append(self.parse_format(args, app))
            else:
                app.args.append(self.parse_node(args, app))
        return app

    def parse_application(self, key: str, value, parent: Node) -> Node:
        if key == "::call" and isinstance(value, str):
            name = value
        else:
            try:
                _, name = key.split(" ")
            except ValueError:
                name = ""
        self.check_name(name)
        app = Application(parent, name)
        if isinstance(value, list):
            app.kwargs[""] = self.parse_sequence(value, app)
        elif isinstance(value, dict):
            for arg_key, arg_value in value.items():
                if arg_key[:1] == "$":
                    arg_key = arg_key[1:]
                app.kwargs[arg_key] = self.parse_node(arg_value, app)
        return app

    def parse_each(self, key: str, value, parent: Node) -> Node:
        try:
            _, source, as_, target = key.split(" ")
            if as_ != "as":
                raise MalformedEachError()
        except ValueError:
            raise MalformedEachError()
        each = Each(parent, source, target)
        each.body = self.parse_node(value, each)
        return each

    def parse_format(self, value, parent: Node) -> Node:
        return Format(parent, value)
