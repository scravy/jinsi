import re

import yaml
import yaml.composer
import yaml.constructor
import yaml.emitter
import yaml.parser
import yaml.reader
import yaml.representer
import yaml.resolver
import yaml.scanner
import yaml.serializer
from dezimal import Dezimal


class Resolver(yaml.resolver.BaseResolver):
    pass


Resolver.add_implicit_resolver(
    '!dec',
    re.compile(r'^[-+]?(?:[0-9]+)(?:\.[0-9]+)?(?:[eE][-+][0-9]+)?$'),
    list('-+0123456789')
)

for ch, vs in yaml.resolver.Resolver.yaml_implicit_resolvers.items():
    Resolver.yaml_implicit_resolvers.setdefault(ch, []).extend(
        (tag, regexp) for tag, regexp in vs
        if not tag.endswith('float') and not tag.endswith('int')
    )


class Loader(yaml.reader.Reader, yaml.scanner.Scanner, yaml.parser.Parser,
             yaml.composer.Composer, yaml.constructor.SafeConstructor, Resolver):

    def __init__(self, stream):
        yaml.reader.Reader.__init__(self, stream)
        yaml.scanner.Scanner.__init__(self)
        yaml.parser.Parser.__init__(self)
        yaml.composer.Composer.__init__(self)
        yaml.constructor.SafeConstructor.__init__(self)
        Resolver.__init__(self)


def dec_constructor(loader, node):
    value = loader.construct_scalar(node)
    return Dezimal(value)


yaml.add_constructor('!dec', dec_constructor, Loader)


def str_node(value: str) -> yaml.ScalarNode:
    return yaml.ScalarNode(tag="tag:yaml.org,2002:str", value=value)


def map_node(value) -> yaml.MappingNode:
    return yaml.MappingNode(tag="tag:yaml.org,2002:map", value=value)


def seq_node(value) -> yaml.SequenceNode:
    return yaml.SequenceNode(tag="tag:yaml.org,2002:seq", value=value)


def aws_cloudformation_intrinsic_function(loader, node):
    fn = f"Fn::{node.tag[1:]}"
    if node.tag in ('!Ref', '!Condition'):
        fn = 'Ref'
    elif node.tag == '!GetAtt' and isinstance(node.value, str):
        path = node.value.split(".", maxsplit=2)
        node = yaml.SequenceNode(
            tag="tag:yaml.org,2002:seq",
            value=[str_node(p) for p in path]
        )
    sub_node: yaml.Node
    if isinstance(node, yaml.SequenceNode):
        sub_node = seq_node(node.value)
    elif isinstance(node, yaml.MappingNode):
        sub_node = map_node(node.value)
    elif node.value is None:
        sub_node = yaml.ScalarNode('tag:yaml.org,2002:null', node.value)
    elif isinstance(node.value, str):
        sub_node = yaml.ScalarNode('tag:yaml.org,2002:str', node.value)
    elif isinstance(node.value, bool):
        sub_node = yaml.ScalarNode('tag:yaml.org,2002:bool', node.value)
    elif isinstance(node.value, int):
        sub_node = yaml.ScalarNode('tag:yaml.org,2002:int', node.value)
    elif isinstance(node.value, float):
        sub_node = yaml.ScalarNode('tag:yaml.org,2002:float', node.value)
    else:
        raise ValueError(node)
    new_node = map_node([(str_node(fn), sub_node)])
    return loader.construct_object(new_node)


aws_cloudformation_intrinsic_functions = [
    "Base64",
    "Cidr",
    "FindInMap",
    "GetAtt",
    "GetAZs",
    "ImportValue",
    "Join",
    "Select",
    "Split",
    "Sub",
    "Transform",
    "Ref",
    "And",
    "Equals",
    "If",
    "Not",
    "Or",
    "Condition",
]

for func in aws_cloudformation_intrinsic_functions:
    yaml.add_constructor(f"!{func}", aws_cloudformation_intrinsic_function, Loader)


class Dumper(yaml.Dumper):

    def __init__(self, *args, **kwargs):
        kwargs['sort_keys'] = False
        super(Dumper, self).__init__(*args, **kwargs)

    def represent_str(self, data):
        if '\n' in data:
            return self.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        else:
            return self.represent_scalar('tag:yaml.org,2002:str', data)

    def represent_dec(self, data):
        s = str(data)
        if '.' in s:
            tag = 'tag:yaml.org,2002:float'
        else:
            tag = 'tag:yaml.org,2002:int'
        return self.represent_scalar(tag, str(data))

    def ignore_aliases(self, data):
        return True


yaml.add_representer(Dezimal, Dumper.represent_dec, Dumper=Dumper)
yaml.add_representer(str, Dumper.represent_str, Dumper=Dumper)


def dumpyaml(data) -> str:
    return yaml.dump(
        data,
        Dumper=Dumper,
        default_flow_style=False,
    )


def loadyaml(stream):
    return yaml.load(stream, Loader=Loader)


def loadyaml_all(stream):
    return yaml.load_all(stream, Loader=Loader)
