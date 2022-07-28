import argparse

import pytest
import sys
import os

# workaround to import python module from parent folder
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import lognet


def test_argument_parser():
    assert type(lognet.get_argument_parser()) == argparse.Namespace
