# scanner/tests/test_utils.py

import pytest
from unittest.mock import patch
from scanner.utils.ssl_checker import check_ssl_validity, check_ssl_protocols, check_hsts_enabled

@pytest.mark.parametrize("url", [
    "https://example.com",
    "example.com",
])
def test_check_ssl_validity_success(url):
    with patch("socket.create_connection") as mock_conn, \
         patch("ssl.SSLContext.wrap_socket") as mock_wrap:
        # Mock certificate info
        mock_wrap.return_value.getpeercert.return_value = {
            'notAfter': 'Dec 31 23:59:59 2099 GMT'
        }
        result = check_ssl_validity(url)
        assert result['status'] == 'pass'
        assert "Certificate is valid" in result['details']

def test_check_ssl_protocols_some_supported():
    with patch("socket.create_connection"), patch("ssl.SSLContext.wrap_socket"):
        result = check_ssl_protocols("https://example.com")
        assert result['status'] == 'pass'
        assert 'TLSv1_2' in result['supported_protocols'] or 'TLSv1_3' in result['supported_protocols']

def test_check_hsts_enabled_present():
    with patch("requests.get") as mock_get:
        mock_get.return_value.headers = {'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'}
        mock_get.return_value.raise_for_status = lambda: None
        result = check_hsts_enabled("https://example.com")
        assert result['status'] == 'pass'
        assert 'HSTS' in result['details']

def test_check_hsts_enabled_missing():
    with patch("requests.get") as mock_get:
        mock_get.return_value.headers = {}
        mock_get.return_value.raise_for_status = lambda: None
        result = check_hsts_enabled("https://example.com")
        assert result['status'] == 'fail'
        assert 'not found' in result['details']
