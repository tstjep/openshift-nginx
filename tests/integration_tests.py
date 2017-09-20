#!/usr/bin/python3
import requests
import subprocess
import time


def assert_response(path, code, *, some_header):
    r = requests.get('http://localhost:8081/{}'.format(path), allow_redirects=False)

    assert r.status_code == code, 'got code {} but expected {}'.format(r.status_code, code)
    assert r.headers['Some-Always-Header'] == 'some always "value"'
    assert not some_header or r.headers['Some-Header'] == 'some "value"'


# regression test for #63270:
# ensure cache isn't shared across different hostnames
def test_cache_keying():
    abc_net1 = requests.get('http://localhost:8081/cache', headers={'Host': 'abc.net'})
    assert abc_net1.headers['X-Cache'] == 'MISS'

    # same host, same uri → cached
    abc_net2 = requests.get('http://localhost:8081/cache', headers={'Host': 'abc.net'})
    assert abc_net2.headers['X-Cache'] == 'HIT'
    assert abc_net1.text == abc_net2.text

    # same host different uri → not cached
    xyz_net = requests.get('http://localhost:8081/cache', headers={'Host': 'xyz.net'})
    assert xyz_net.headers['X-Cache'] == 'MISS'
    assert abc_net1.text != xyz_net.text


#
# Test if status-tocco-nginx returns 200 even if Nice isn't reachable
#
assert_response('status-tocco-nginx', 200, some_header=True)
assert_response('bad-gateway', 502, some_header=False)


#
# Verify forwarding to upstream works and headers are set
#
nice_mock = subprocess.Popen('./tests/nice_mock.py')

# wait for mock to become ready
while True:
    try:
        requests.get('http://localhost:8080/200')
    except requests.exceptions.ConnectionError:
        print('waiting for mock …')
        time.sleep(0.5)
    else:
        break

assert_response('200', 200, some_header=True)
assert_response('404', 404, some_header=False)
assert_response('500', 500, some_header=False)

# verify default timeout of 60s is not in effect
assert_response('time=240', 200,  some_header=True)

test_cache_keying()

nice_mock.terminate()
