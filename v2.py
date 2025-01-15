import os
import subprocess
import json
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException
from ibm_code_engine_sdk.code_engine_v2 import CodeEngineV2, ProjectsPager
from getpass import getpass

ibmcloud_api_key = os.environ.get('IBMCLOUD_API_KEY')
if not ibmcloud_api_key:
    raise ValueError("IBMCLOUD_API_KEY environment variable not found")

def prompt_user_for_input():
    region = input("Enter the IBM Cloud region: ")
    resource_group = input("Enter the IBM Cloud resource group: ")
    project_name = input("Enter the IBM Cloud Code Engine project name: ")
    custom_domain = input("Enter the custom domain: ")
    dns_token = getpass("Enter your DNS provider API token: ")
    certbot_email = input("Enter your email address for certbot request: ")
    return region, resource_group, project_name, custom_domain, dns_token, certbot_email

def generate_tls_certificate(custom_domain, dns_token, certbot_email):
    cert_dir = f"certbot-{custom_domain}"
    os.makedirs(cert_dir, exist_ok=True)
    certbot_cmd = [
        "certbot", "certonly", "--dns-digitalocean", "--dns-digitalocean-credentials",
        "./digitalocean.ini", "--dns-digitalocean-propagation-seconds", "120",
        "-d", custom_domain, "--non-interactive", "--agree-tos", "-m", certbot_email,
        "--config-dir", cert_dir, "--work-dir", cert_dir, "--logs-dir", cert_dir
    ]

## certbot certonly --dns-digitalocean --dns-digitalocean-credentials  ./digitalocean.ini --dns-digitalocean-propagation-seconds 180 -d gh40-dev.systems --non-interactive --agree-tos  -m ryantiffany@fastmail.com --config-dir ./  --logs-dir ./ --work-dir ./

    with open("digitalocean.ini", "w") as f:
        f.write(f"dns_digitalocean_token = {dns_token}\n")
    
    os.chmod("digitalocean.ini", 0o600)
    
    subprocess.run(certbot_cmd, check=True)
    # certbot-lab.gh40-dev.systems/live/lab.gh40-dev.systems/fullchain.pem
    cert_path = f"{cert_dir}/live/{custom_domain}/fullchain.pem"
    key_path = f"{cert_dir}/live/{custom_domain}/privkey.pem"

    with open(cert_path, "r") as cert_file:
        tls_cert = cert_file.read()

    with open(key_path, "r") as key_file:
        tls_key = key_file.read()

    return tls_cert, tls_key

def get_project_id_by_name(ce_client, project_name):
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
        if project['name'] == project_name:
            return project['id']
    
    raise Exception(f"Project with name {project_name} not found.")

def create_code_engine_secret(ce_client, project_id, secret_name, tls_cert, tls_key):
    secret_data = {
        'tls.crt': tls_cert,
        'tls.key': tls_key,
    }

    response = ce_client.create_secret(
        project_id=project_id,
        format='tls',
        name=secret_name,
        data=secret_data
    ).get_result()

    return response['id']

def map_custom_domain(ce_client, project_id, custom_domain, secret_id):
    response = ce_client.create_ingress_secret_mapping(
        project_id=project_id,
        domain=custom_domain,
        secret_name=secret_id
    ).get_result()

    return response

def main():
    # region, resource_group, project_name, custom_domain, dns_token, certbot_email = prompt_user_for_input()
    region = "us-south"
    resource_group = "CDE"
    project_name = "rst-ce-dev"
    custom_domain = "demo.gh40-dev.systems"
    dns_token = os.environ.get('DO_TOKEN')
    certbot_email = "ryantiffany@fastmail.com"
    authenticator = IAMAuthenticator(apikey=ibmcloud_api_key)
    ce_client = CodeEngineV2(authenticator=authenticator)
    ce_client.set_service_url('https://api.'+region+'.codeengine.cloud.ibm.com/v2')

    project_id = get_project_id_by_name(ce_client, project_name)

    tls_cert, tls_key = generate_tls_certificate(custom_domain, dns_token, certbot_email)

    try:
        secret_id = create_code_engine_secret(ce_client, project_id, "tls-secret", tls_cert, tls_key)
        # print(f"Secret {secret_id['name']} created successfully.")
    except ApiException as e:
        print(f"Error creating secret")
    
    # map_custom_domain(ce_client, project_id, custom_domain, secret_id)

    print(f"Check if secret is created correctly.")

if __name__ == '__main__':
    main()
