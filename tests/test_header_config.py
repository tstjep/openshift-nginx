import header_config
import tempfile
import textwrap
import unittest

class Test(unittest.TestCase):
    def test_main(self):
        env = {
            'NGINX_HEADER_Strict-Transport-Security': 'max-age=86400',
            'ignored': 'ignored',
            'NGINX_HEADER_a_name': r'value in need of escaping "\"',
            'NGINX_HEADER_name-with__hyphens': 'double__underscores__not__replaced__here',
            'NGINX_ALWAYS_HEADER_Always': 'present even on error pages'
        }
        with tempfile.NamedTemporaryFile(mode='w+') as f:
            header_config.main(env, f.name)

            self.assertEqual(f.read(), textwrap.dedent(r"""
                # DO NOT EDIT MANUALLY!
                # content is generated based on NGINX_HEADER_* and NGINX_ALWAYS_HEADER_* environment variables

                add_header "Always" "present even on error pages" always;
                add_header "Strict-Transport-Security" "max-age=86400";
                add_header "a_name" "value in need of escaping \"\\\"";
                add_header "name-with-hyphens" "double__underscores__not__replaced__here";
            """).lstrip())
