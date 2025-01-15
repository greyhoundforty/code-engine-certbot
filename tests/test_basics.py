import subprocess
from datetime import datetime


def test_script_execution():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    custom_domain = f"test{timestamp}.gh40-dev.systems"
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
    )
    assert result.returncode == 0
    # Example of using curl to check the resulting custom domain
    curl_result = subprocess.run(
        ["curl", "-k", f"https://{custom_domain}"], capture_output=True, text=True
    )
    assert "expected content" in curl_result.stdout
