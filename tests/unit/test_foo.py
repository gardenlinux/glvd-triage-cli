import pytest

from cli import parse_yaml_file

def test_placeholder():
    actual = parse_yaml_file("tests/unit/sample.yaml")
    assert actual[0]['is_resolved'] == False
    assert actual[0]['cves'][0] == 'CVE-2024-12345'
    assert len(actual) == 14
