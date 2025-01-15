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
    return region, resource_group, project_name, custom_domain, dns_token

def generate_tls_certificate(custom_domain, dns_token):
    certbot_cmd = [
        "certbot", "certonly", "--dns-digitalocean", "--dns-digitalocean-credentials",
        "./digitalocean.ini", "--dns-digitalocean-propagation-seconds", "60",
        "-d", custom_domain, "--non-interactive", "--agree-tos", "-m", "your-email@example.com"
    ]

    with open("digitalocean.ini", "w") as f:
        f.write(f"dns_digitalocean_token = {dns_token}\n")
    
    os.chmod("digitalocean.ini", 0o600)
    
    subprocess.run(certbot_cmd, check=True)

    cert_path = f"/etc/letsencrypt/live/{custom_domain}/fullchain.pem"
    key_path = f"/etc/letsencrypt/live/{custom_domain}/privkey.pem"

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
    region, resource_group, project_name, custom_domain, dns_token = prompt_user_for_input()

    authenticator = IAMAuthenticator(apikey=ibmcloud_api_key)
    ce_client = CodeEngineV2(authenticator=authenticator)
    ce_client.set_service_url('https://api.'+region+'.codeengine.cloud.ibm.com/v2')

    project_id = get_project_id_by_name(ce_client, project_name)

    tls_cert, tls_key = generate_tls_certificate(custom_domain, dns_token)

    try:
        secret_id = create_code_engine_secret(ce_client, project_id, "tls-secret", tls_cert, tls_key)
        result = secret_id.get_result()
        print(f"Secret {result['name']} created successfully.")
    except ApiException as e:
        print(f"Error creating secret")
    # map_custom_domain(ce_client, project_id, custom_domain, secret_id)

    print(f"Custom domain {custom_domain} mapped successfully with TLS certificate.")

if __name__ == '__main__':
    main()
