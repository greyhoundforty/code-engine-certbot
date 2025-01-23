import subprocess
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def test_script_execution():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    custom_domain = f"test{timestamp}.gh40-dev.systems"

    # Get the current environment variables
    env = os.environ.copy()

    # Ensure the required environment variables are set
    assert "DO_TOKEN" in env, "DO_TOKEN environment variable is not set"
    assert "IBMCLOUD_API_KEY" in env, "IBMCLOUD_API_KEY environment variable is not set"

    result = subprocess.run(
        [
            "python",
            "ce-tls-app.py",
            "--region",
            "us-south",
            "--project-name",
            "rst-ce-dev",
            "--app-name",
            "application-35",
            "--custom-domain",
            custom_domain,
            "--certbot-email",
            "ryantiffany@gmail.com",
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, f"Script failed with error: {result.stderr}"

    # Example of using curl to check the resulting custom domain
    http_result = subprocess.run(
        [
            "/opt/homebrew/bin/http",
            "--default-scheme=http/https",
            f"https://{custom_domain}",
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert "200 OK" in http_result.stdout
