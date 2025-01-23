<a id="utils"></a>

# utils

<a id="ce-tls-app"></a>

# ce-tls-app

<a id="ce-tls-app.code_engine_client"></a>

#### code\_engine\_client

```python
def code_engine_client(region)
```

Create a Code Engine client in the specified IBM Cloud region.
See https://cloud.ibm.com/apidocs/codeengine/v2?code=python#endpointurls

<a id="ce-tls-app.digitalocean_client"></a>

#### digitalocean\_client

```python
def digitalocean_client()
```

Create a Digital Ocean client.

<a id="ce-tls-app.generate_tls_certificate"></a>

#### generate\_tls\_certificate

```python
def generate_tls_certificate(custom_domain, dns_token, certbot_email)
```

Generate a TLS certificate for the custom domain using certbot and DNS challenge.

<a id="ce-tls-app.get_project_id"></a>

#### get\_project\_id

```python
def get_project_id(ce_client, project_name)
```

Get the Code Engine project ID from the project name.
Used by custom_domain mapping function

<a id="ce-tls-app.create_code_engine_secret"></a>

#### create\_code\_engine\_secret

```python
def create_code_engine_secret(ce_client, project_id, secret_name, tls_cert,
                              tls_key)
```

Create a secret in the specified Code Engine project.

<a id="ce-tls-app.update_dns"></a>

#### update\_dns

```python
def update_dns(custom_domain, code_engine_cname)
```

We need to get the canonical domain name from the custom_domain.
This is required to update the DNS records in Digital Ocean.

<a id="ce-tls-app.main"></a>

#### main

```python
@click.command()
@click.option("--region",
              prompt="Enter the IBM Cloud region",
              help="IBM Cloud region")
@click.option(
    "--project-name",
    prompt="Enter the IBM Cloud Code Engine project name",
    help="IBM Cloud Code Engine project name",
)
@click.option(
    "--app-name",
    prompt="Enter the IBM Cloud Code Engine application name",
    help="IBM Cloud Code Engine app name",
)
@click.option("--custom-domain",
              prompt="Enter the custom domain",
              help="Custom domain")
@click.option(
    "--certbot-email",
    prompt="Enter your email address for certbot request",
    help="Email address for certbot request",
)
def main(region, project_name, app_name, custom_domain, certbot_email)
```

This script automates the process of mapping a custom domain to an IBM Cloud Code Engine application.
