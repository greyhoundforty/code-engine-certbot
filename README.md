# Overview

This script automates the process of mapping a custom domain to an IBM Cloud Code Engine application using Certbot and Let's Encrypt DNS chaallenge.

## Prerequisites

- Python 3.x
- Required Python packages installed (see `requirements.txt`)
- IBM Cloud API Key
- DigitalOcean API Key

## Usage

```shell
python ce-tls-app.py --region <ibmcloud-region> \
    --project-name <code-engine-project-name> \
    --app-name <application-name> \
    --custom-domain <custom-domain> \
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
