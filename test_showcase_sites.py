import pytest
from showcase_sites import showcase_boundary
from site_mapping import SHOWCASE_CENTERS, boundary_from_drawings

@pytest.mark.parametrize('city', list(SHOWCASE_CENTERS))
def test_demonstration_bounds_are_valid(city):
    boundary = showcase_boundary(city)
    lat, lon, _ = SHOWCASE_CENTERS[city]
    assert 14_200 < boundary.area_m2 < 14_600
    assert 470 < boundary.perimeter_m < 490
    assert abs(boundary.latitude - lat) < 0.0001
    assert abs(boundary.longitude - lon) < 0.0001
    assert boundary_from_drawings([{'type':'Feature','geometry':boundary.geometry}]) is not None

def test_unknown_showcase_is_rejected():
    with pytest.raises(ValueError):
        showcase_boundary('Unknown city')

def test_showcase_does_not_make_remote_calls(monkeypatch):
    import requests
    def forbidden(*args,**kwargs):
        raise AssertionError('No network calls allowed')
    monkeypatch.setattr(requests,'get',forbidden)
    monkeypatch.setattr(requests,'post',forbidden)
    assert showcase_boundary('Stockholm · Södermalm').area_m2 > 0
