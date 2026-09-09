#!/usr/bin/python3
"""Shim: V1.0.1.5 oracles live in test_drvs.TestV1015Patches."""
from test_drvs import TestV1015Patches  # noqa: F401

if __name__ == "__main__":
    import unittest
    unittest.main(module="test_drvs", defaultTest="TestV1015Patches", verbosity=2)
