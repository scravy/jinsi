import json
import textwrap
import unittest

import dezimal
import yaml
from dezimal import Dezimal

from jinsi import *
from jinsi.yamlutil import Loader

import os


class JinsiExamples(unittest.TestCase):

    def _check(self, expected, doc: str, dezimal_foo: bool = False, args: dict = None):
        rendered = render1s(doc, as_json=True, args=args)
        if dezimal_foo:
            self.assertEqual(expected, json.loads(rendered, parse_int=dezimal.Dezimal, parse_float=dezimal.Dezimal))
        else:
            self.assertEqual(expected, json.loads(rendered))

        rendered = render1s(doc, as_json=False, args=args)
        if dezimal_foo:
            self.assertEqual(expected, yaml.load(rendered, Loader=Loader))
        else:
            self.assertEqual(expected, yaml.safe_load(rendered))

        if dezimal_foo:
            loaded = load1s(doc, numtype=dezimal.Dezimal, args=args)
        else:
            loaded = load1s(doc, args=args)
        self.assertEqual(expected, loaded)

    def test_simple_template(self):
        doc = """\
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
        """

        expected = {
            "Resources": {
                "Jim": {
                    "Type": "AWS::IAM::User",
                    "Properties": {
                        "UserName": "jim",
                        "Groups": ["Administrators"],
                        "LoginProfile": {
                            "Password": "one",
                            "PasswordResetRequired": True
                        }
                    }
                },
                "Jack": {
                    "Type": "AWS::IAM::User",
                    "Properties": {
                        "UserName": "jack",
                        "Groups": ["Administrators"],
                        "LoginProfile": {
                            "Password": "two",
                            "PasswordResetRequired": True
                        }
                    }
                },
                "Johnny": {
                    "Type": "AWS::IAM::User",
                    "Properties": {
                        "UserName": "johnny",
                        "Groups": ["Administrators"],
                        "LoginProfile": {
                            "Password": "default",
                            "PasswordResetRequired": True
                        }
                    }
                }
            }
        }

        self._check(expected, doc)

    def test_example_0(self):
        doc = """\
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
        """

        expected = {
            'Resources': {
                'Jim': {
                    'Type': 'AWS::IAM::User',
                    'Properties': {
                        'UserName': 'jim', 'Groups': ['Administrators'],
                        'LoginProfile': {
                            'Password': 'one',
                            'PasswordResetRequired': True
                        }}},
                'Jack': {
                    'Type': 'AWS::IAM::User',
                    'Properties': {
                        'UserName': 'jack', 'Groups': ['Administrators'],
                        'LoginProfile': {
                            'Password': 'two',
                            'PasswordResetRequired': True
                        }}},
                'Johnny': {
                    'Type': 'AWS::IAM::User',
                    'Properties': {
                        'UserName': 'johnny', 'Groups': ['Administrators'],
                        'LoginProfile': {
                            'Password': 'default',
                            'PasswordResetRequired': True
                        }}}
            }
        }

        self._check(expected, doc)

    def test_example_1(self):
        doc = textwrap.dedent("""\
            ::let:
              name: XMLRpcParser_Main
            
            docs:
              - ::snakecase: <<name>>
              - ::uppercase:
                  ::snakecase:
                    ::get: name
              - ::uppercase:
                  ::kebabcase:
                    ::get: name
              - ::kebabcase:
                  ::get: name
              - ::titlecase:
                  ::get: name
              - ::camelcase:
                  ::get: name
              - ::titlecase: XmlRPCProcessor_23
              - ::div:
                  - 1
                  - 7
                  - null
                  - 28
              - ::div:
                  - 355
                  - 113
              - ::div:
                  - 355
                  - 113
                  - 20
              - ::div:
                  - 2.7
                  - 3.01
                  - null
                  - 17
        """)

        expected = {
            'docs': [
                'xml_rpc_parser_main',
                'XML_RPC_PARSER_MAIN',
                'XML-RPC-PARSER-MAIN',
                'xml-rpc-parser-main',
                'XmlRpcParserMain',
                'xmlRpcParserMain',
                'XmlRpcProcessor23',
                Dezimal('0.1428571428571428571428571428'),
                Dezimal('3.14159292035398230088495575221238938053097345132743362831858407'
                        '079646017699115044247787610619469026548672566371681'),
                Dezimal('3.14159292035398230088'),
                Dezimal('0.89700996677740863787375415282392026578073')
            ]
        }

        self._check(expected, doc, dezimal_foo=True)

    def test_example_2(self):
        doc = textwrap.dedent("""\
            ::let:
              x: foo
              y: bar
              $x: qux
              $y: quuz
            
              template:
                - ::get: x
                - ::get: y
                - ::get: $x
                - ::get: $y
                - ::get: $z
            
            formatted: hello <<x>> woohoo <<y>> yeah <<$x>> and <<$y>>
            
            cool:
              some-<<x>>: <<y>>
              woohoo: <<x>>/<<y>>
            
            list:
              - ::get: x
              - ::get: y
              - ::get: $x
              - ::get: $y
              - ::get: JINSI_TEST_SHELL
              - ::get: JINSI_TEST_HOSTNAME
                ::else: unknown
            
            x:
              ::let:
                something:
                  ::get: $m
              y:
                - ::get: something
                  ::let:
                    $m: 3
                  ::else:
                    ::get: $z
                - ::get: $q
                  ::else: All okay.
            
            applied:
              ::let:
                x: keyfoo
                y: keybar
                $x: keyqux
                $y: keyquuz
                $z: zeeee
            
              ::call template:
                $y: callquuz
            
            applied2:
              ::call: template
        """)

        expected = {
            'formatted': 'hello foo woohoo bar yeah qux and quuz',
            'cool': {
                'some-foo': 'bar',
                'woohoo': 'foo/bar',
            },
            'list': [
                'foo',
                'bar',
                'qux',
                'quuz',
                '/bin/hash',
                'unknown',
            ],
            'x': {
                'y': [
                    3.0,
                    'All okay.',
                ]
            },
            'applied': [
                'foo',
                'bar',
                'keyqux',
                'callquuz',
                'zeeee',
            ],
            'applied2': [
                'foo',
                'bar',
                'qux',
                'quuz',
                'zzz',
            ],
        }

        os.environ['JINSI_TEST_SHELL'] = '/bin/hash'

        self._check(expected, doc, args={'z': 'zzz'})


if __name__ == '__main__':
    unittest.main()
