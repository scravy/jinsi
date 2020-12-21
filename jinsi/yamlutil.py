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
from dezimal import Dec


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
    return Dec(value)


yaml.add_constructor('!dec', dec_constructor, Loader)


class Dumper(yaml.Dumper):

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


yaml.add_representer(Dec, Dumper.represent_dec, Dumper=Dumper)
yaml.add_representer(str, Dumper.represent_str, Dumper=Dumper)


def dumpyaml(data) -> str:
    return yaml.dump(
        data,
        Dumper=Dumper,
        default_flow_style=False,
    )
