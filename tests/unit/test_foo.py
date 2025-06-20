import pytest

from cli import parse_yaml

def test_placeholder():
    assert len(parse_yaml("tests/unit/sample.yaml")) == 14
