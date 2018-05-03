import pickle

from buildings import get_building_list
from rooms import add_rooms_to_buildings
from sections import add_sections_to_rooms
from test import test_runtime


def get_buildings_with_room_class_info(building_filename, room_filename, class_filename,
                                       intersession=False, building_codes=[], min_room_size=None, max_room_size=None,
                                       load=False, save=False, debug=False, include_all_rooms=False):
    if load:
        buildings = load_buildings()
        if len(building_codes) > 0:
            buildings = {code: buildings.get(code, None) for code in building_codes}
        return buildings
    else:
        _building_codes = building_codes[:]
        if save:
            _building_codes = []

        buildings = get_building_list(_building_codes, filename=building_filename)
        buildings = add_rooms_to_buildings(buildings, filename=room_filename, min_room_size=min_room_size, max_room_size=max_room_size)
        buildings = add_sections_to_rooms(buildings, filename=class_filename, intersession=intersession, debug=debug, include_all_rooms=include_all_rooms)

        if save:
            save_buildings(buildings)

    if save and len(building_codes) > 0:
        # If save selected, then generated all buildings, but only want requested codes
        buildings = {code: buildings.get(code, None) for code in building_codes}
    return buildings


def load_buildings(filename='buildings.pkl'):
    with open(filename, 'rb') as infile:
        buildings = pickle.load(infile)
        return buildings


def save_buildings(buildings, filename='buildings.pkl'):
    with open(filename, 'wb') as outfile:
        pickle.dump(buildings, outfile, pickle.HIGHEST_PROTOCOL)


def compare_speed():
    def f():
        get_buildings_with_room_class_info(building_codes=['DAH'], load=False, save=False)

    def s():
        get_buildings_with_room_class_info(building_codes=['DAH'], load=True)

    test_runtime(f, s)

if __name__ == "__main__":
    compare_speed()