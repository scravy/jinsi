#!/usr/bin/env python3

from jinsi import *

if __name__ == '__main__':
    print(render_file("test2.yaml"))
    print(load_file("test2.yaml").requires_env())
