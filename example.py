#!/usr/bin/env python3

from jinsi import *

if __name__ == '__main__':
    # print(render("""\
    #     ::let:
    #         bucket:
    #             ::object:
    #                 - ::ref: $name
    #                 - definition
    #         buckets:
    #             ::each $ as $arg:
    #                 ::call bucket:
    #                     name:
    #                         ::ref: $arg
    #     x:
    #         ::merge:
    #             ::call buckets:
    #                 - one
    #                 - two
    #                 - three
    #     y:
    #         ::call bucket:
    #             name: sweetiepie
    #
    # """))
    print(render_file("example.yaml"))
