# JSON/YAML homoiconic templating language

[![Github Actions](https://github.com/scravy/jinsi/workflows/Python%20application/badge.svg)](https://github.com/scravy/jinsi/actions)
[![Downloads](https://static.pepy.tech/personalized-badge/jinsi?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads)](https://pepy.tech/project/jinsi)
[![PyPI version](https://badge.fury.io/py/jinsi.svg)](https://pypi.org/project/jinsi/)

```shell script
python3 -m pip install jinsi
```

Jinsi is a templating engine that uses YAML/JSON syntax, i.e. it is homoiconic. Never mess with indentation again.

Most template engines are a poor choice for templating YAML/JSON, which is why Jinsi is embedded in the document as
native YAML/JSON syntax.

Example:

```yaml
::let:
  foo: Hello
  bar: World
value: <<foo>> <<bar>>
```

Yields:

```
value: Hello World
```

Since Jinsi is basically independent from the syntax it works natively in JSON (or any other dialect which uses the
same data model) too:

```
{
  "::let": {
    "foo": "Hello",
    "bar": "World"
  },
  "value": "<<foo>> <<bar>>"
}
```

Jinsi was inspired by AWS Cloudformation templates, which are also homoiconic and feature builtin functions
(with more limited scope though). As I am using it to ease my DevOps woes it supports Cloudformation's
Bang-Syntax (`!Sub`) natively.

Jinsi comes as a command line tool, but you can use it as a library for reading/writing YAML/JSON files too.

Usage:

```bash
jinsi template.yaml foo=bar qux=quuz
```

The above invocation will set `$foo` to `Jane` and `$qux` to `Jim`:

```
value: Hello <<$foo>>
```

...would result in `value: Hello Jane`.

I am also using it to template Kubernetes YAML files. Both `kustomize` as well as `helm` (which uses Go
Templates 😖) do not cut it for me. My developer life has been happier ever since. I could imagine using it with salt, too
(Jinja templates + YAML is just a PITA). Here's an example which configures
an [ingress resource using aws load balancer controller](https://github.com/kubernetes-sigs/aws-load-balancer-controller)

```yaml
::let:
  $name: web-application
  $subdomain: dashboard
  $domain: example.com
  $services:
    - users
    - messages
    - backoffice

apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: <<$subdomain>>
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/group.name: <<$domain>>
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/listen-ports:
      ::json_serialize:
        - HTTPS: 443
        - HTTP: 80
    alb.ingress.kubernetes.io/actions.ssl-redirect:
      ::json_serialize:
        Type: redirect
        RedirectConfig:
          Protocol: HTTPS
          Port: '443'
          StatusCode: HTTP_301
spec:
  rules:
    - host: <<$subdomain>>.<<$domain>>
      http:
        paths:
          ::concat:
            - - path: /*
                backend:
                  serviceName: ssl-redirect
                  servicePort: use-annotation
            - ::each $services as $service:
                path: '/<<$service>>/*'
                backend:
                  serviceName: <<$service>>-service
                  servicePort: 80
            - - path: '/*'
                backend:
                  serviceName: <<$name>>
                  servicePort: 80
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

### Some fancy shit, too 🥸

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
