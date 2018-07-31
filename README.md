# openshift-nginx
[![Build Status](https://travis-ci.org/tocco/openshift-nginx.svg?branch=master)](https://travis-ci.org/tocco/openshift-nginx)

:warning: Because of incorrectly set caching headers (bug #66771), Nice <2.13 uses the config in branch `limited-caching`.


## Setting Headers

IMPORTANT:

OpenShift does not currently allow hyphens (`-`) to appear as keys of environment variables, you need to use double underscores (`__`)
instead. (See examples below.)

Set header for responses with 2XX status codes:

```
    NGINX_HEADER_My__Header=header-content
```

This creates a header called `My-Header` with the value `header-content`.


Set header regardless of status code:

```
    NGINX_ALWAYS_HEADER_My__Header=header-content
```

This creates a header called `My-Header` with the value `header-content`.


## Limit Access to IP addresses

IP addresses can be whitelisted using the `IP_WHITELIST` env. variable:

```
    IP_WHITELIST='81.55.33.3 40.22.0.0/16 1.5.5.5-1.5.5.7'
```

IP addresses, CIDR or IP ranges can be specified separated by space. If `IP_WHITELIST` is unset
or empty, all addresses is granted access.
