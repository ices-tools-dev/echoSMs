from collections.abc import Iterable

import echosms


def test_create_spheroid():
    rv_pos, rv_tan, a = echosms.create_dwba_spheroid(0.010, 0.050)

    # TODO: actually check the returned data values!
    assert isinstance(rv_pos, Iterable)
    assert isinstance(rv_tan, Iterable)
    assert isinstance(a, Iterable)


def test_create_cylinder():
    rv_pos, rv_tan, a = echosms.create_dwba_cylinder(0.005, 0.010)

    # TODO: actually check the returned data values!
    assert isinstance(rv_pos, Iterable)
    assert isinstance(rv_tan, Iterable)
    assert isinstance(a, Iterable)


def test_create_xyza():
    x = [1, 2, 3, 4, 5]
    y = [0, 0, 0, 0, 0]
    z = [0, 0, 0, 0, 0]
    a = [.1, .1, .1, .1, .1]
    d = echosms.create_dwba_from_xyza(x, y, z, a, 'test')
    # TODO: actually check the returned data values!
    assert isinstance(d, echosms.DWBAorganism)


def test_dwbadata():

    d = echosms.DWBAdata()

    assert len(d.names()) > 0
    assert isinstance(d.as_dict(), dict)
    n = d.names()[0]
    assert isinstance(d.model(n), echosms.DWBAorganism)
    assert d.model('test name') is None

    d.model(n).plot(block=False)
