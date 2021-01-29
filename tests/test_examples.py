import json
import unittest

from dezimal import Dezimal

from jinsi import *


class JinsiExamples(unittest.TestCase):

    def test_simple_template(self):
        doc = textwrap.dedent("""\
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
        """)
        rendered = render_json(doc)
        self.assertEqual({
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
        }, json.loads(rendered))

    def test_example_0(self):
        doc = textwrap.dedent("""\
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
        """)

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
        self.assertEqual(expected, evaluate(doc))

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
        self.assertEqual(expected, evaluate(doc))
