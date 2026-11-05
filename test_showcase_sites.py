"""Current showcase regression tests (real user-supplied GeoJSON)."""
import pytest
from pathlib import Path
from shapely.geometry import shape
from showcase_sites import SHOWCASE_FILES, showcase_boundary

@pytest.mark.parametrize('city', list(SHOWCASE_FILES))
def test_showcase_uses_supplied_valid_site(city):
    boundary = showcase_boundary(city)
    assert boundary.geometry['type'] == 'Polygon'
    assert shape(boundary.geometry).is_valid
    assert boundary.area_m2 > 1000
    assert boundary.perimeter_m > 100
    assert -180 <= boundary.longitude <= 180
    assert -90 <= boundary.latitude <= 90
    assert Path(__file__).with_name(SHOWCASE_FILES[city]).is_file()


def test_showcase_unknown_city_rejected():
    with pytest.raises(ValueError):
        showcase_boundary('Unknown place')


def test_barcelona_is_only_showcase():
    assert list(SHOWCASE_FILES) == ["Barcelona · Selected construction site"]
