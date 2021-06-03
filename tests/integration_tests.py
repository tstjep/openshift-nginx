#!/usr/bin/python3
import nice_mock
import requests
import time
from multiprocessing import Process


def assert_response(path, code, *, some_header, source_ip='10.0.0.3'):
    headers = { 'X-Forwarded-For': source_ip, 'X-Forwarded-Proto': 'https' }
    r = requests.get('http://localhost:8081/{}'.format(path), allow_redirects=False, headers=headers)

    assert r.status_code == code, 'got code {} but expected {} fetching {!r} with source IP {}'.format(r.status_code, code, path, source_ip)
    assert r.headers['Some-Always-Header'] == 'some always "value"'
    assert not some_header or r.headers['Some-Header'] == 'some "value"'


# regression test for #63270:
# ensure cache isn't shared across different hostnames
def test_cache_keying():
    abc_net1 = requests.get('http://localhost:8081/cache', headers={'Host': 'abc.net', 'X-Forwarded-Proto': 'https', 'X-Forwarded-For': '10.0.0.3'})
    assert abc_net1.headers['X-Cache'] == 'MISS'

    # same schema, same host and same uri → cached
    abc_net2 = requests.get('http://localhost:8081/cache', headers={'Host': 'abc.net', 'X-Forwarded-Proto': 'https', 'X-Forwarded-For': '10.0.0.3'})
    assert abc_net2.headers['X-Cache'] == 'HIT'
    assert abc_net1.text == abc_net2.text

    # different schema → not cached
    http = requests.get('http://localhost:8081/cache', headers={'Host': 'abc.net', 'X-Forwarded-Proto': 'http', 'X-Forwarded-For': '10.0.0.3'})
    assert http.headers['X-Cache'] == 'MISS'
    assert abc_net1.text != http.text

    # different host → not cached
    xyz_net = requests.get('http://localhost:8081/cache', headers={'Host': 'xyz.net', 'X-Forwarded-Proto': 'https', 'X-Forwarded-For': '10.0.0.3'})
    assert xyz_net.headers['X-Cache'] == 'MISS'
    assert abc_net1.text != xyz_net.text



# Test if status-tocco-nginx returns 200 even if Nice isn't reachable
def test_unreachable():
    assert_response('status-tocco-nginx', 200, some_header=True)
    assert_response('bad-gateway', 502, some_header=False)


# Verify forwarding to upstream works and headers are set
def test_proxying():
    assert_response('200', 200, some_header=True)
    assert_response('404', 404, some_header=False)
    assert_response('500', 500, some_header=False)


# verify default timeout of 60s is not in effect
def test_timeout():
    assert_response('time=240', 200,  some_header=True)


def test_access_control():
    ips = [
        # IP         allowed
        ('10.0.0.2', False),
        ('10.0.0.3', True),
        ('10.0.0.4', False),

        ('10.5.7.255', False),
        ('10.5.8.0', True),
        ('10.5.8.255', True),
        ('10.5.9.0', False),

        ('22.88.88.0', False),
        ('22.88.88.1', True),
        ('22.88.88.7', True),
        ('22.88.88.8', False),

        ('81.81.81.81', False)
    ]

    for ip, allowed in ips:
        # never block status pages
        assert_response('status-tocco', 200, some_header=True, source_ip=ip)
        assert_response('status-tocco-nginx', 200, some_header=True, source_ip=ip)

        if allowed:
            assert_response('200', 200, some_header=True, source_ip=ip)
        else:
            assert_response('200', 403, some_header=False, source_ip=ip)

    # ignore 22.88.8.7 because previous address in chain, 81.81.81.81, is untrusted
    resp = requests.get('http://localhost:8081/200', headers={'Host': 'abc.net', 'X-Forwarded-Proto': 'https', 'X-Forwarded-For': '22.88.8.7, 81.81.81.81, 10.0.0.3, 10.0.0.2'})
    assert resp.status_code == 403


def test_websocket():
    # Ensure the 'Connection' and 'Upgrade' HTTP headers are properly forwarded
    # to the web server. The implementation for the /websocket route does the
    # actual testing.
    resp = requests.get(
        'http://localhost:8081/websocket',
        allow_redirects=False,
        headers={
            'Connection': 'Upgrade',
            'Upgrade': 'WebSocket',
            'X-Forwarded-For': '10.0.0.3',
            'X-Forwarded-Proto': 'https',
        }
    )
    resp.raise_for_status()


def test_no_websocket():
    # Neither the 'Connection' nor the 'Upgrade' header should be sent
    # to upstreams. The web server tests this.
    resp = requests.get(
        'http://localhost:8081/no-websocket',
        allow_redirects=False,
        headers = {
            'X-Forwarded-For': '10.0.0.3',
            'X-Forwarded-Proto': 'https',
        }
    )
    resp.raise_for_status()


class mock:
    def __init__(self):
        self.mock = None

    def __enter__(self):
        self.mock = Process(target=nice_mock.run)
        self.mock.start()

        # wait for mock to become ready
        while True:
            try:
                requests.get('http://localhost:8080/200')
            except requests.exceptions.ConnectionError:
                print('waiting for mock …')
                time.sleep(0.5)
            else:
                break

    def __exit__(self, a, b, c):
        if self.mock is not None:
            self.mock.terminate()


def main():
    test_unreachable()

    with mock():
        test_cache_keying()
        test_proxying()
        test_access_control()
        test_timeout()
        test_websocket()
        test_no_websocket()

if __name__ == '__main__':
    main()
