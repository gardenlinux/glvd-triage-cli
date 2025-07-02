import pytest

from cli import parse_yaml_file, to_db_rows_v1


def test_parse_yaml_file():
    actual = parse_yaml_file("tests/unit/sample.yaml")
    assert actual[0]["is_resolved"] == False
    assert actual[0]["cves"][0] == "CVE-2024-12345"
    assert len(actual) == 14


def test_to_db_rows_v1():
    input = {
        "revision": "v1",
        "cves": ["CVE-2024-12345"],
        "dists": ["1592.10"],
        "is_resolved": False,
        "triaged": False,
    }

    expected = [
        (
            24,
            "1592.10",
            "CVE-2024-12345",
            "all",
            None,
            None,
            False,
            False,
        ),
    ]

    actual = to_db_rows_v1(input)
    assert actual == expected
