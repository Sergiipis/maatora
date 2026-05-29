from importlib.metadata import version

import maatora


def test_version_is_exposed():
    """maatora exposes a non-empty __version__ string (PEP 396 convention)."""
    assert isinstance(maatora.__version__, str)
    assert maatora.__version__


def test_version_matches_distribution_metadata():
    """__version__ is sourced from the installed distribution, not hardcoded."""
    assert maatora.__version__ == version("maatora")
