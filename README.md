# openshift-nginx
[![Build Status](https://travis-ci.org/tocco/openshift-nginx.svg?branch=master)](https://travis-ci.org/tocco/openshift-nginx)

##

:warning: This branch is used for Nice <2.13 due to incorrectly set caching headers. The `master` branch is what you want for current
versions of Nice.


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
