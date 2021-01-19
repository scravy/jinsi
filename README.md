# JSON/YAML homoiconic templating language

[![Github Actions](https://github.com/scravy/jinsi/workflows/Python%20application/badge.svg)](https://github.com/scravy/jinsi/actions)
[![Downloads](https://static.pepy.tech/personalized-badge/jinsi?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads)](https://pepy.tech/project/jinsi)
[![PyPI version](https://badge.fury.io/py/jinsi.svg)](https://pypi.org/project/jinsi/)

```shell script
python3 -m pip install jinsi
```

## Usage via CLI

```shell script
python3 -m jinsi -  # read from stdin
```

```shell script
python3 -m jinsi -j -  # read from stdin, render as json
```

```shell script
python3 -m jinsi file1.yaml file2.yaml
```

## Usage via API

```python
from jinsi import render_json, render_yaml, render_file_json, render_file_yaml

print(render_file_yaml("file.yaml"))
# -> prints YAML

print(render_file_json("file.yaml"))
# -> prints minified JSON

print(render_yaml("""
    a: 3
    b:
      ::get: $arg1
    """, arg1="bar"))
# -> prints YAML

print(render_json("""
    a: 3
    b:
      ::get: $arg1
    """, arg1="foo"))
# -> prints JSON
```

## Examples

### Cloudformation Template

YAML input:

```yaml
::let:
  user:
    ::object:
      - ::titlecase:
          ::get: $user.username
      - Type: AWS::IAM::User
        Properties:
          UserName:
            ::get: $user.username
          Groups:
            - Administrators
          LoginProfile:
            Password:
              ::get: $user.password
              ::else: default
            PasswordResetRequired: Yes
  users:
    ::merge:
      ::each $ as $user:
        ::call user:

Resources:
  ::call users:
    - username: jim
      password: one
    - username: jack
      password: two
    - username: johnny
```

Rendered output:

```yaml
Resources:
  Jack:
    Properties:
      Groups:
      - Administrators
      LoginProfile:
        Password: two
        PasswordResetRequired: true
      UserName: jack
    Type: AWS::IAM::User
  Jim:
    Properties:
      Groups:
      - Administrators
      LoginProfile:
        Password: one
        PasswordResetRequired: true
      UserName: jim
    Type: AWS::IAM::User
  Johnny:
    Properties:
      Groups:
      - Administrators
      LoginProfile:
        Password: default
        PasswordResetRequired: true
      UserName: johnny
    Type: AWS::IAM::User
```

### Fibonacci

This is just an example to show how complex a template can be.
Also note: The fibonacci function is defined recursively. This
would blow up and values upto 50 could not be computed. Since
Jinsi is purely functional, functions are mappings and can be
cached. This is why the computation returns quickly (at all).

```shell script
python3 -m jinsi max=50 -
```

YAML input:

```yaml
::let:
  fib:
    ::when:
      ::get: $n == 0 or $n == 1
    ::then:
      ::get: $n
    ::else:
      ::add:
        - ::call fib:
            $n:
              ::get: $n - 1
        - ::call fib:
            $n:
              ::get: $n - 2
  fibs:
    ::range_exclusive:
      - 0
      - ::get: $max
        ::else: 10

result:
  ::each fibs as $n:
    ::call: fib
```

Rendered output:

```yaml
result:
- 0
- 1
- 1
- 2
- 3
- 5
- 8
- 13
- 21
- 34
- 55
- 89
- 144
- 233
- 377
- 610
- 987
- 1597
- 2584
- 4181
- 6765
- 10946
- 17711
- 28657
- 46368
- 75025
- 121393
- 196418
- 317811
- 514229
- 832040
- 1346269
- 2178309
- 3524578
- 5702887
- 9227465
- 14930352
- 24157817
- 39088169
- 63245986
- 102334155
- 165580141
- 267914296
- 433494437
- 701408733
- 1134903170
- 1836311903
- 2971215073
- 4807526976
- 7778742049
```
