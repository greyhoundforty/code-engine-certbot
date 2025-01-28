# Overview

This script automates the process of mapping a custom domain to an IBM Cloud Code Engine application using Certbot and Let's Encrypt DNS chaallenge.

## Prerequisites

- Python 3.x
- Required Python packages installed (see `requirements.txt`)
- IBM Cloud API Key: [Instructions](https://cloud.ibm.com/docs/account?topic=account-userapikey)
- API Key for your DNS Provider: See the list of providers and associated Environment variables [here](https://go-acme.github.io/lego/dns/)

## Usage

### Step 1: Grab the code

First grab a copy of the repository:

```shell
git clone https://github.com/greyhoundforty/code-engine-certbot.git
cd code-engine-certbot
```

> If you use [mise](https://mise.jdx.dev/) you should see that it has created the venv for you once you change into the directory. The `mise.toml` file includes a few tasks as well that you can use to install the required packages and run the script.

### Step 2: Install the required packages

Next we need to install the required python packages. I recommend a virtualenv so as not to pollute your system python. You can do this by running the following commands:

```shell
python -v venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Export the required environment variables

The script requires 2 variables to be set in the environment: `IBM_CLOUD_API_KEY` and `<DNS_PROVIDER_ENVIRONMENT_VAR>`. The IBM Cloud API Key is used to interact with the IBM Cloud Code Engine API. The `<DNS_PROVIDER_ENVIRONMENT_VAR>` is used to interact with the DNS provider's API to create the required DNS records for the Let's Encrypt DNS challenge.

> In this case `<DNS_PROVIDER_ENVIRONMENT_VAR>` is a placeholder and should be replaced with the appropriate environment variable for your DNS provider. For example, if you are using Cloudflare, you would run `export CLOUDFLARE_DNS_API_TOKEN=<your token>`, for DigitalOcean you would run `export DO_AUTH_TOKEN=<your token>`, etc.

```shell
export IBM_CLOUD_API_KEY=<ibm-cloud-api-key>
export <DNS_PROVIDER_ENVIRONMENT_VAR>=<dns-provider-api-key>
```

### Step 4: Run the script

With the environment variables set, we can now run the script. The script takes the following arguments:

- `--region`: The IBM Cloud region where your Code Engine project is located.
- `--project-name`: The name of the Code Engine project.
- `--app-name`: The name of the Code Engine application.
- `--custom-domain`: The custom domain you want to map to the Code Engine application.
- `--dns-provider`: The DNS provider you are using.
- `--certbot-email`: The email address to use for the Let's Encrypt certificate.

```shell

python ce_tls_app.py --region <ibmcloud-region> \
    --project-name <code-engine-project-name> \
    --app-name <application-name> \
    --custom-domain <custom-domain> \
    --dns-provider <dns-provider> \
    --certbot-email <certbot-email>
```

## Quick Start

If you use [mise](https://mise.jdx.dev/), you can run the following command to get started quickly:

```shell
git clone https://github.com/greyhoundforty/code-engine-certbot.git
cd code-engine-certbot
```

From here `mise` will automatically install the required python version and create a venv for you. From there you can run:

```shell
source .venv/bin/activate
uv pip install -r requirements.txt
```

Then you can run the script as shown in the usage section.
