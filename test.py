#!/usr/bin/env python3

import jinsi

if __name__ == '__main__':
    print(jinsi.render_yaml("""g
        ::let:
            x: seven
        ::format: <<x>> <<x>> <<x>>
    """))