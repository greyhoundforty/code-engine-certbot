import pytest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ce_tls_app import generate_tls_certificate, list_domain_mappings, main


@patch("ce_tls_app.subprocess.run")
@patch("ce_tls_app.os.makedirs")
def test_generate_tls_certificate(mock_makedirs, mock_subprocess_run):
    custom_domain = "example.com"
    dns_provider = "dns-provider"
    certbot_email = "test@example.com"

    generate_tls_certificate(custom_domain, dns_provider, certbot_email)

    mock_makedirs.assert_called_once_with("certbot-output", exist_ok=True)
    assert (
        mock_subprocess_run.call_count == 3
    )  # Two openssl commands and one certbot command


@patch("ce_tls_app.CodeEngineV2")
@patch("ce_tls_app.get_project_id")
@patch("ce_tls_app.logger")
def test_list_domain_mappings_no_mappings(
    mock_logger, mock_get_project_id, mock_CodeEngineV2
):
    ce_client = MagicMock()
    ce_client.list_domain_mappings.return_value.get_result.return_value = {
        "domain_mappings": []
    }

    result = list_domain_mappings(ce_client, "app_name", "project_id")

    assert result is None
    mock_logger.info.assert_called_with(
        "No custom domain mappings found for app: app_name"
    )


@patch("ce_tls_app.CodeEngineV2")
@patch("ce_tls_app.get_project_id")
@patch("ce_tls_app.logger")
@patch("ce_tls_app.generate_tls_certificate")
@patch("ce_tls_app.create_code_engine_secret")
@patch("ce_tls_app.list_domain_mappings")
@patch("ce_tls_app.update_dns")
def test_main_func(
    mock_update_dns,
    mock_list_domain_mappings,
    mock_create_code_engine_secret,
    mock_generate_tls_certificate,
    mock_logger,
    mock_get_project_id,
    mock_CodeEngineV2,
):
    mock_generate_tls_certificate.return_value = ("cert_data", "key_data")
    mock_list_domain_mappings.return_value = None

    main(
        "test@example.com",
        "custom.example.com",
        "region",
        "app_name",
        "project_name",
        "dns_provider",
    )

    mock_CodeEngineV2.assert_called_once()
    mock_get_project_id.assert_called_once()
    mock_generate_tls_certificate.assert_called_once_with(
        "custom.example.com", "dns_provider", "test@example.com"
    )
    mock_create_code_engine_secret.assert_called_once()
    mock_update_dns.assert_called_once()
    mock_logger.info.assert_any_call(
        "Setting up a new custom domain mapping for app: app_name"
    )


if __name__ == "__main__":
    pytest.main()
