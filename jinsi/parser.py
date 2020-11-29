from __future__ import annotations

import re
from datetime import date, datetime
from inspect import getattr_static

import yaml

from jinsi import MalformedNameError, NoParseError, NoSuchFunctionError, Functions, JinsiException
from .exceptions import MalformedEachError
from .nodes import *
from .util import merge


# noinspection PyMethodMayBeStatic
class Parser:

    def __init__(self):
        self.name_regex = "^[a-z]([_-]?[a-z0-9])*$"

    def check_name(self, name):
        if not re.match(self.name_regex, name):
            raise MalformedNameError(name=name, expected=self.name_regex)

    def parse_node(self, obj: Any, parent: Node) -> Node:
        if isinstance(obj, list):
            return self.parse_sequence(obj, parent)
        if isinstance(obj, (type(None), bool, int, float, str, date, datetime)):
            return self.parse_constant(obj, parent)
        if '::include' in obj:
            includes = obj['::include']
            if isinstance(includes, str):
                includes = [includes]
            del obj['::include']
            docs = [obj]
            for include in includes:
                with open(include) as f:
                    docs.append(yaml.safe_load(f))
            obj = merge(*docs)
        if '::else' in obj:
            return self.parse_else(obj, parent)
        if '::let' in obj:
            return self.parse_let(obj, parent)
        if '::ref' in obj:
            ref = obj['::ref']
            if isinstance(ref, str) and ref[:1] == '$' or isinstance(ref, list) and ref[0][:1] == '$':
                return self.parse_get_env(obj, parent)
            return self.parse_get_let(obj, parent)
        for key in obj:
            if key[:8] == "::format":
                return self.parse_format(obj, parent)
            if key[:6] == "::call":
                return self.parse_application(obj, parent)
            if key[:6] == "::each":
                return self.parse_each(obj, parent)
            if key[:2] == "::":
                return self.parse_function_application(obj, parent)
        return self.parse_object(obj, parent)

    def parse_constant(self, obj, parent: Node) -> Node:
        return Constant(parent, obj)

    def parse_get_let(self, obj, parent: Node) -> Node:
        path = obj['::ref']
        if isinstance(path, str):
            path = path.split(".")
        if not isinstance(path, list):
            raise NoParseError()
        return GetLet(parent, path)

    def parse_get_env(self, obj, parent: Node) -> Node:
        path = obj['::ref']
        if isinstance(path, str):
            path = path.split(".")
        if not isinstance(path, list):
            raise NoParseError()
        path[0] = path[0][1:]  # remove leading dollar sign
        return GetEnv(parent, path)

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

    def parse_function_application(self, obj, parent: Node) -> Node:
        for key in obj:
            if key[:2] == "::":
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
                args = obj[key]
                if isinstance(args, list):
                    for arg in args:
                        app.args.append(self.parse_node(arg, app))
                elif len(args) == 1:
                    app.args.append(self.parse_node(args, app))
                else:
                    raise NoParseError()
                return app
        raise NoParseError()

    def parse_application(self, obj, parent: Node) -> Node:
        for key, value in obj.items():
            if key[:6] == "::call":
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
        raise JinsiException()

    def parse_each(self, obj, parent: Node) -> Node:
        for key, value in obj.items():
            if key[:6] == "::each":
                try:
                    _, source, _, target = key.split(" ")
                except ValueError:
                    raise MalformedEachError()
                each = Each(parent, source, target)
                each.body = self.parse_node(value, each)
                return each
        raise NoParseError()

    def parse_format(self, obj: Any, parent: Node) -> Node:
        for key, value in obj.items():
            if key == "::format":
                return Format(parent, value)
        raise NoParseError()
