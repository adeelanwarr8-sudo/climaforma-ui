"""Regression checks for mode transition using the exact app source block."""
from pathlib import Path
from types import SimpleNamespace

SOURCE = (Path(__file__).parent / 'app.py').read_text()
START = SOURCE.index('map_context = (site_mode, showcase_city')
END = SOURCE.index('# Changing the slider rebuilds', START)
TRANSITION_CODE = compile(SOURCE[START:END], 'app.py', 'exec')
CENTER_START = SOURCE.index('active_address = st.session_state.get("address_location")\nmap_center =')
CENTER_END = SOURCE.index('\n\ndef build_site_map', CENTER_START)
CENTER_CODE = compile(SOURCE[CENTER_START:CENTER_END], 'app.py', 'exec')


def test_address_to_draw_keeps_geocoded_location_and_geometry():
    point = {'lat': 59.314, 'lon': 18.073, 'label': 'Medborgarplatsen, Stockholm'}
    state = {'map_context': ('Address lookup', None),
             'address_location': point, 'address_matches': [point],
             'address_match_query': point['label'],
             'boundary_info': 'user_polygon', 'vector_layer': 'osm',
             'map_drawings_seen': True, 'map_generation': 5}
    env = {'site_mode': 'Draw site boundary', 'showcase_city': 'Stockholm · Södermalm',
           'st': SimpleNamespace(session_state=state),
           'showcase_boundary': lambda x: 'demo'}
    exec(TRANSITION_CODE, env)
    assert state['address_location'] == point
    assert state['boundary_info'] == 'user_polygon'
    assert state['vector_layer'] == 'osm'
    assert state['map_generation'] == 6
    env['SHOWCASE_CENTERS'] = {'Stockholm · Södermalm': (59.315, 18.075, 14)}
    env['DEFAULT_CENTER'] = (59.315, 18.075, 14)
    env['address_draft'] = ''
    exec(CENTER_CODE, env)
    assert env['map_center'] == (59.314, 18.073, 17)
    assert env['address_draft'] == point['label']


def test_showcase_transition_does_not_inherit_address():
    point = {'lat': 41.39, 'lon': 2.16, 'label': 'Barcelona'}
    state = {'map_context': ('Draw site boundary', None), 'address_location': point,
             'boundary_info': 'user_polygon', 'vector_layer': 'osm', 'map_generation': 3}
    env = {'site_mode': 'Showcase site', 'showcase_city': 'Vienna · Neubau',
           'st': SimpleNamespace(session_state=state),
           'showcase_boundary': lambda x: 'demo:' + x}
    exec(TRANSITION_CODE, env)
    assert state['address_location'] is None
    assert state['boundary_info'] == 'demo:Vienna · Neubau'
    assert state['vector_layer'] is None


def test_draw_to_address_keeps_geocoded_location():
    point = {'lat': 48.202, 'lon': 16.348, 'label': 'Vienna'}
    state = {'map_context': ('Draw site boundary', None), 'address_location': point,
             'boundary_info': 'user_polygon', 'vector_layer': None, 'map_generation': 1}
    env = {'site_mode': 'Address lookup', 'showcase_city': 'Stockholm · Södermalm',
           'st': SimpleNamespace(session_state=state), 'showcase_boundary': lambda x: None}
    exec(TRANSITION_CODE, env)
    assert state['address_location'] == point
    assert state['boundary_info'] == 'user_polygon'
