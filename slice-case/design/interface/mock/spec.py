from partspec import Part, openscad


def mock_all() -> Part:
    return Part('slot-mock-all', openscad('slot_mock.scad', show='all'))


def mock_backplane() -> Part:
    return Part('slot-mock-backplane', openscad('slot_mock.scad', show='backplane'))
