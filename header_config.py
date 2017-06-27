#!/usr/bin/python3
import functools
import os


ENV_PREFIX = 'NGINX_HEADER_'
ENV_ALWAYS_PREFIX = 'NGINX_ALWAYS_HEADER_'
QUOTE_TRANSLATION_TABLE = str.maketrans({
    "\\": r"\\",
    '"':  r'\"'
})


class Header:
    def __init__(self, name, value, *, always):
        self.name = name
        self.value = value
        self.always = always

    def line(self):
        param = ' always' if self.always else ''
        return "add_header {} {}{};".format(quote(self.name), quote(self.value), param)


def quote(value):
    return '"' + value.translate(QUOTE_TRANSLATION_TABLE) + '"'


def unescape(value):
    return value.replace('__', '-')


def extract_headers(env):
    for key, value in env.items():
        if key.startswith(ENV_PREFIX):
            yield Header(unescape(key[len(ENV_PREFIX):]), value, always=False)
        elif key.startswith(ENV_ALWAYS_PREFIX):
            yield Header(unescape(key[len(ENV_ALWAYS_PREFIX):]), value, always=True)


def write_config(stream, headers):
    write = functools.partial(print, file=stream)
    write('# DO NOT EDIT MANUALLY!')
    write('# content is generated based on NGINX_HEADER_* and NGINX_ALWAYS_HEADER_* environment variables')
    write()
    for header in sorted(headers, key=lambda i: i.name):
        write(header.line())


def main(env, path):
    headers = extract_headers(env)
    with open(path, 'w') as f:
        write_config(f, headers)


if __name__ == '__main__':
    print(os.environ)
    main(os.environ, '/etc/nginx/headers.include')

