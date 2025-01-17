import os
import subprocess
import click
import tldextract
from datetime import datetime
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException
from ibm_code_engine_sdk.code_engine_v2 import CodeEngineV2, ProjectsPager
from pydo import Client


ibmcloud_api_key = os.environ.get("IBMCLOUD_API_KEY")
if not ibmcloud_api_key:
    raise ValueError("IBMCLOUD_API_KEY environment variable not found")

dns_token = os.environ.get("DO_TOKEN")
if not dns_token:
    raise ValueError("DO_TOKEN environment variable not found")


def code_engine_client(region):
    authenticator = IAMAuthenticator(apikey=ibmcloud_api_key)
    ce_client = CodeEngineV2(authenticator=authenticator)
    ce_client.set_service_url("https://api." + region + ".codeengine.cloud.ibm.com/v2")
    return ce_client


def generate_tls_certificate(custom_domain, dns_token, certbot_email):
    cert_dir = f"certbot-{custom_domain}"
    os.makedirs(cert_dir, exist_ok=True)
    certbot_cmd = [
        "certbot",
        "certonly",
        "--dns-digitalocean",
        "--dns-digitalocean-credentials",
        "./digitalocean.ini",
        "--dns-digitalocean-propagation-seconds",
        "120",
        "-d",
        custom_domain,
        "--non-interactive",
        "--agree-tos",
        "-m",
        certbot_email,
        "--config-dir",
        cert_dir,
        "--work-dir",
        cert_dir,
        "--logs-dir",
        cert_dir,
    ]

    with open("digitalocean.ini", "w") as f:
        f.write(f"dns_digitalocean_token = {dns_token}\n")

    os.chmod("digitalocean.ini", 0o600)

    subprocess.run(certbot_cmd, check=True)
    cert_path = f"{cert_dir}/live/{custom_domain}/fullchain.pem"
    key_path = f"{cert_dir}/live/{custom_domain}/privkey.pem"

    with open(cert_path, "r") as cert_file:
        tls_cert = cert_file.read()

    with open(key_path, "r") as key_file:
        tls_key = key_file.read()

    return tls_cert, tls_key


def get_project_id(ce_client, project_name):
    all_results = []
    pager = ProjectsPager(
        client=ce_client,
        limit=100,
    )
    while pager.has_next():
        next_page = pager.get_next()
        assert next_page is not None
        all_results.extend(next_page)
    for project in all_results:
        if project["name"] == project_name:
            return project["id"]
    raise Exception(f"Project with name {project_name} not found.")


def create_code_engine_secret(ce_client, project_id, secret_name, tls_cert, tls_key):
    """
    Create a secret in the specified Code Engine project.
    """
    secret_data = {
        "tls.crt": tls_cert,
        "tls.key": tls_key,
    }

    response = ce_client.create_secret(
        project_id=project_id, format="tls", name=secret_name, data=secret_data
    ).get_result()

    return response["id"]


def update_dns(custom_domain, code_engine_cname):
    """
    We need to get the canonical domain name from the custom_domain.
    This is required to update the DNS records in Digital Ocean.
    """

    extracted = tldextract.extract(custom_domain)
    canonical_domain = extracted.domain + "." + extracted.suffix
    do_client = Client(token=dns_token)
    if not code_engine_cname.endswith("."):
        code_engine_cname += "."
    body = {"type": "CNAME", "name": extracted.subdomain, "data": code_engine_cname}
    do_client.domains.create_record(canonical_domain, body=body)
    print(f"Updating DNS for {canonical_domain} to point to {code_engine_cname}")


def map_custom_domain(ce_client, app_name, project_id, custom_domain, secret_name):
    component_ref_model = {
        "name": app_name,
        "resource_type": "app_v2",
    }

    response = ce_client.create_domain_mapping(
        project_id=project_id,
        component=component_ref_model,
        name=custom_domain,
        tls_secret=secret_name,
    )
    domain_mapping = response.get_result()
    print(f"Domain mapping {domain_mapping['name']} created successfully.")
    return domain_mapping


@click.command()
@click.option("--region", prompt="Enter the IBM Cloud region", help="IBM Cloud region")
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
@click.option("--custom-domain", prompt="Enter the custom domain", help="Custom domain")
@click.option(
    "--certbot-email",
    prompt="Enter your email address for certbot request",
    help="Email address for certbot request",
)
def main(region, project_name, app_name, custom_domain, certbot_email):
    ## Flow should be:
    # 1. Pull code engine project id from name
    ce_client = code_engine_client(region)
    project_id = get_project_id(ce_client, project_name)
    print(f"Working on Project ID: {project_id}")

    # 2. Pull application id from project and app name
    response = ce_client.get_app(
        project_id=project_id,
        name=app_name,
    )
    app = response.get_result()

    code_engine_app_endpoint = app.get("endpoint")
    code_engine_cname = code_engine_app_endpoint.replace("https://", "")
    print(f"Code Engine App Endpoint: {code_engine_cname}")

    # 3. Update DO DNS to point custom_domain to code engine cname
    update_dns(custom_domain, code_engine_cname)

    # # 4. Generate TLS certificate for custom_domain
    tls_cert, tls_key = generate_tls_certificate(
        custom_domain, dns_token, certbot_email
    )

    # # 5. Create secret in code engine project
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    secret_name = f"tls-secret-{timestamp}-{app_name}"
    create_code_engine_secret(ce_client, project_id, secret_name, tls_cert, tls_key)

    # 6. Map custom domain to code engine project
    map_custom_domain(ce_client, app_name, project_id, custom_domain, secret_name)


if __name__ == "__main__":
    main()
