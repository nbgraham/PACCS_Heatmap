import numpy as np

from plot import plot_room_efficiency, plot_heat_map, plot_avg_seat_utilization_by_room
from analysis import get_room_occ
from campus import get_buildings_with_room_class_info
from analysis import get_buildings_with_sections_for_time

def average_seat_utilization_per_class_by_room(intersession=False, building_codes=[]):
    buildings = get_buildings_with_room_class_info(intersession, building_codes)

    rooms = []
    for code, building in buildings.items():
        rooms.extend(building.get_rooms())

    avg_seat_utilizations = []
    for i in range(len(rooms)):
        room = rooms[i]
        seat_utilizations = [section.actual_enrollment / room.seat_count for section in room.getSections()]
        avg_seat_utilization = np.mean(seat_utilizations)
        avg_seat_utilizations.append(avg_seat_utilization)

    plot_avg_seat_utilization_by_room(rooms, avg_seat_utilizations)


def main(debug=False):
    # average_seat_utilization_per_class_by_room(building_codes=['DAH'])

    seat_utilization = True
    buildings, intervals_dec = get_buildings_with_sections_for_time(seat_utilization=seat_utilization, debug=debug)

    def _get_room_occ(room, intervals_dec):
        return get_room_occ(room, intervals_dec, seat_utilization=seat_utilization, seat_utilization_by_room_occ=True)

    plot_room_efficiency(buildings, intervals_dec, _get_room_occ)
    plot_heat_map(buildings, intervals_dec)


if __name__ == "__main__":
    main()