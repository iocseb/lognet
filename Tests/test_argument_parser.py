import argparse

from lognet import get_argument_parser


def test_get_argument_parser():
    """ Test for get_argument_parser """

    assert type(get_argument_parser()) == argparse.Namespace
