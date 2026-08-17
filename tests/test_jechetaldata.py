import echosms


def test_jechetaldata():
    """Test access to the Jech et al dataset."""

    j = echosms.JechEtAlData()

    assert j.data_directory.is_dir()
    assert len(j.data) > 0
