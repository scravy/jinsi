from .common import JinsiTestCase


class JinsiEach(JinsiTestCase):

    def test_each(self):
        doc = """\
            ::let:
              qux:
                - a
                - b
                - c
            foo:
              ::merge:
                ::each qux as name:
                  ::object:
                    - <<name>>_key
                    - <<name>>_value
        """

        expected = {
            'foo': {
                'a_key': 'a_value',
                'b_key': 'b_value',
                'c_key': 'c_value',
            }
        }

        self.check(expected, doc)

    def test_each_with_dynamic_loop_parameter(self):
        doc = """\
            resources:
              ::call resources_template:
                $rs:
                  - one
                  - two
            ::let:
              resource:
                ::object:
                  - <<$res.name>>_key
                  - name: <<$res.name>>_value
              resources_template:
                ::merge:
                    ::each $rs as $r:
                      - ::call resource:
                          $res:
                            name: <<$r>>
                      - ::call resource:
                          $res:
                            name: <<$r>>_foo
                      - ::call resource:
                          $res:
                            name: <<$r>>_bar
        """

        expected = {
            "resources": {
                "one_key": {
                    "name": "one_value"
                },
                "one_foo_key": {
                    "name": "one_foo_value"
                },
                "one_bar_key": {
                    "name": "one_bar_value"
                },
                "two_key": {
                    "name": "two_value"
                },
                "two_foo_key": {
                    "name": "two_foo_value"
                },
                "two_bar_key": {
                    "name": "two_bar_value"
                },
            }
        }

        self.check(expected, doc)


    def test_each_with_lexicographic_loop_parameter(self):
        doc = """\
            resources:
              ::call resources_template:
                $rs:
                  - one
                  - two
            ::let:
              resource:
                ::object:
                  - <<$res.name>>_key
                  - name: <<$res.name>>_value
              resources_template:
                ::merge:
                    ::each $rs as r:
                      - ::call resource:
                          $res:
                            name: <<r>>
                      - ::call resource:
                          $res:
                            name: <<r>>_foo
                      - ::call resource:
                          $res:
                            name: <<r>>_bar
        """

        expected = {
            "resources": {
                "one_key": {
                    "name": "one_value"
                },
                "one_foo_key": {
                    "name": "one_foo_value"
                },
                "one_bar_key": {
                    "name": "one_bar_value"
                },
                "two_key": {
                    "name": "two_value"
                },
                "two_foo_key": {
                    "name": "two_foo_value"
                },
                "two_bar_key": {
                    "name": "two_bar_value"
                },
            }
        }

        self.check(expected, doc)

