import json
import unittest

from jinsi import render_json


class JinsiExamples(unittest.TestCase):

    def test_simple_template(self):
        doc = """
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
