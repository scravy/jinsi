import os
import unittest
from decimal import Decimal

from .common import JinsiTestCase


class JinsiExamples(JinsiTestCase):

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

        self.check(expected, doc)

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

        self.check(expected, doc)

    def test_example_1(self):
        doc = """\
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
              - ::div:
                  - 355
                  - 113
              - ::div:
                  - 2.7
                  - 3.01
        """

        expected = {
            'docs': [
                'xml_rpc_parser_main',
                'XML_RPC_PARSER_MAIN',
                'XML-RPC-PARSER-MAIN',
                'xml-rpc-parser-main',
                'XmlRpcParserMain',
                'xmlRpcParserMain',
                'XmlRpcProcessor23',
                Decimal('0.1428571428571428571428571429'),
                Decimal('3.141592920353982300884955752'),
                Decimal('0.8970099667774086378737541528')
            ]
        }

        self.check(expected, doc, dezimal_foo=True)

    def test_example_2(self):
        doc = """\
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
        """

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

        self.check(expected, doc, args={'z': 'zzz'})

    def test_example_3(self):
        doc = """\
            ::let:
              users:
                ::each $ as $account:
                  ::object:
                    - ::get: $account
                    - Properties:
                        Some: props
            
              robousers:
                ::each $ as $account:
                  ::object:
                    - ::get: $account
                    - Properties:
                        Some: props
            
            Resources:
              ::call users:
                - jane
                - john
              ::call robousers:
                - ava
                - hal
              a: b
              c: d
        """

        expected = {
            'Resources': {
                'jane': {
                    'Properties': {
                        'Some': 'props'
                    }
                },
                'john': {
                    'Properties': {
                        'Some': 'props'
                    }
                }, 'ava': {
                    'Properties': {
                        'Some': 'props'
                    }
                }, 'hal': {
                    'Properties': {
                        'Some': 'props'
                    }
                },
                'a': 'b',
                'c': 'd',
            }
        }

        self.check(expected, doc)

    def test_example_4(self):
        doc = """\
            ::let:
              xs:
                - 1
                - 2
                - 7
                - 3
                - 2
                - 9
                - 4
                - 2
                - 5
            
            doc:
              ys:
                ::get: xs
              zs:
                ::let:
                  x:
                    ::explode:
                      - " "
                      - hello world out there
                ::get: x
              qs:
                ::let:
                  xs:
                    ::explode:
                      - " "
                      - hello out there
                ::each xs as x:
                  ::get: x
        """

        expected = {
            'doc': {
                'ys': [1, 2, 7, 3, 2, 9, 4, 2, 5],
                'zs': ['hello', 'world', 'out', 'there'],
                'qs': ['hello', 'out', 'there'],
            }
        }

        self.check(expected, doc)

    def test_example_5(self):
        doc = """\
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
        """

        expected = {
            'result': [
                0,
                1,
                1,
                2,
                3,
                5,
                8,
                13,
                21,
                34,
            ]
        }

        self.check(expected, doc)

    def test_example_6(self):
        doc = """\
            result:
              ::any:
                - ::when: false
                  ::then: 1
                - ::when: false
                  ::then: 2
                - 7
            
            result2:
              ::any:
                - []
                - {}
                - false
                - null
                - 1
                - 2
                - 3
        """

        expected = {
            'result': 7,
            'result2': 1,
        }

        self.check(expected, doc)


if __name__ == '__main__':
    unittest.main()
