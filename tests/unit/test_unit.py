import pytest

from cli import parse_yaml_file, to_db_rows_v1


def test_parse_yaml_file():
    actual = parse_yaml_file("tests/unit/sample.yaml")
    assert actual[0]["is_resolved"] == False
    assert actual[0]["cves"][0] == "CVE-2024-12345"
    assert len(actual) == 14


# Avoid dependency on the api for the unit test
def mocked_distId_resolver(v):
    if v == "today":
        return 14
    if v == "1592.5":
        return 16
    if v == "1592.10":
        return 24
    return -1


given_and_expected_to_db_rows = [
    (
        {
            "revision": "v1",
            "cves": ["CVE-2024-12345"],
            "dists": ["1592.10"],
            "is_resolved": False,
            "triaged": False,
        },
        [
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
        ],
    ),
    (
        {
            "revision": "v1",
            "cves": ["CVE-2023-50387"],
            "dists": ["today"],
            "is_resolved": True,
            "triaged": False,
            "description": "automated dummy data\n",
            "use_case": "gardener",
            "ignored": False,
        },
        [
            (
                14,
                "today",
                "CVE-2023-50387",
                "gardener",
                None,
                "automated dummy data\n",
                True,
                False,
            ),
        ],
    ),
    (
        {
            "revision": "v1",
            "cves": ["CVE-2024-12085"],
            "dists": ["1592.5", "today"],
            "is_resolved": False,
            "triaged": False,
            "description": "#### Vulnerability Description:\nA critical flaw was discovered in `rsync`...\n",
            "use_case": "gardener",
            "ignored": False,
        },
        [
            (
                16,
                "1592.5",
                "CVE-2024-12085",
                "gardener",
                None,
                "#### Vulnerability Description:\n"
                "A critical flaw was discovered in `rsync`...\n",
                False,
                False,
            ),
            (
                14,
                "today",
                "CVE-2024-12085",
                "gardener",
                None,
                "#### Vulnerability Description:\n"
                "A critical flaw was discovered in `rsync`...\n",
                False,
                False,
            ),
        ],
    ),
]


@pytest.mark.parametrize("given_and_expected_to_db_rows", given_and_expected_to_db_rows)
def test_to_db_rows_v1(given_and_expected_to_db_rows):
    given = given_and_expected_to_db_rows[0]
    expected = given_and_expected_to_db_rows[1]

    actual = to_db_rows_v1(given, mocked_distId_resolver)
    assert actual == expected
