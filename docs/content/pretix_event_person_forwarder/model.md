# Table of Contents

* [model](#model)
  * [APIEndpoints](#model.APIEndpoints)
  * [RequestsMethods](#model.RequestsMethods)
  * [APIModel](#model.APIModel)

<a id="model"></a>

# model

<a id="model.APIEndpoints"></a>

## APIEndpoints Objects

```python
class APIEndpoints(Enum)
```

The class includes all necessary API endpoint strings to connect the Pretix API

<a id="model.RequestsMethods"></a>

## RequestsMethods Objects

```python
class RequestsMethods(Enum)
```

The class includes all necessary method values to establish an HTTP/ HTTPS connection to the Pretix API endpoints

<a id="model.APIModel"></a>

## APIModel Objects

```python
@dataclass
class APIModel()
```

The class includes all necessary variables to establish a connection to the Grafana API endpoints

**Arguments**:

- `host` _str_ - Specify the host of the Grafana system
- `token` _str_ - Specify the access token of the Grafana system
- `username` _str_ - Specify the username of the Grafana system
- `password` _str_ - Specify the password of the Grafana system
- `timeout` _float_ - Specify the timeout of the Grafana system
- `headers` _dict_ - Specify the headers of the Grafana system
- `http2_support` _bool_ - Specify if you want to use HTTP/2
- `ssl_context` _ssl.SSLContext_ - Specify the custom ssl context of the Grafana system
- `num_pools` _int_ - Specify the number of the connection pool
- `retries` _any_ - Specify the number of the retries. Please use False as parameter to disable the retries
- `follow_redirects` _bool_ - Specify if redirections should be followed (default True)

