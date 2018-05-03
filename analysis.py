import pickle
import numpy as np

from campus import get_buildings_with_room_class_info
from time_dec import get_intervals_dec, dec_to_time, time_interval_name


def analyze(bldg_abbr_file_path, central_rooms_file_path, class_list_file_path, debug=False):
    print("Loading room and seat utilization...")
    buildings, intervals_dec = get_buildings_with_sections_for_time(
                    building_filename=bldg_abbr_file_path,
                    room_filename=central_rooms_file_path,
                    class_filename=class_list_file_path,
                    both=True,
                    debug=debug)

    print("Loading centrally scheduled building codes...")
    building_codes = [code for code, building in buildings.items() if len(building.rooms) > 0]

    print("Done!")

    return intervals_dec, buildings, building_codes


def get_buildings_with_sections_for_time(building_filename=r'C:\Users\nickb\Google Drive\Career\PACCS\building_abbreviations.csv',
                                         room_filename=r'C:\Users\nickb\Google Drive\Career\PACCS\centrally_scheduled_classrooms.csv',
                                         class_filename=r'C:\Users\nickb\Google Drive\Career\PACCS\ClassSchedule-23_comma.csv',
                                         start_time=800, end_time=1600, interval=30,
                                         load=False, save=False,
                                         seat_utilization=False, both=False, seat_utilization_by_room_occ=True,
                                         building_codes=[],
                                         min_room_size=None,
                                         max_room_size=None,
                                         debug=False,
                                         include_all_rooms=False):
    intervals_dec = get_intervals_dec(start_time, end_time, interval)
    if debug: print(intervals_dec)

    if load:
        buildings = load_buildings()
    else:
        buildings = get_buildings_with_room_class_info(building_filename, room_filename, class_filename, intersession=False,
                                                       building_codes=building_codes, max_room_size=max_room_size, min_room_size=min_room_size,
                                                       debug=debug, include_all_rooms=include_all_rooms)

        buildings = add_section_by_time_to_rooms(buildings, intervals_dec, seat_utilization=seat_utilization,
                                                 seat_utilization_by_room_occ=seat_utilization_by_room_occ,
                                                 debug=debug, both=both)
        if save:
            save_buildings(buildings)

    return buildings, intervals_dec


def load_buildings(filename='buildings_occupancy.pkl'):
    with open(filename, 'rb') as infile:
        buildings = pickle.load(infile)
        return buildings


def save_buildings(buildings, filename='buildings_occupancy.pkl'):
    with open(filename, 'wb') as outfile:
        pickle.dump(buildings, outfile, pickle.HIGHEST_PROTOCOL)


def add_section_by_time_to_rooms(buildings, intervals_dec, seat_utilization=False, seat_utilization_by_room_occ=True, debug=False, both=False):
    for code, building in buildings.items():
        building_rooms = building.get_sorted_rooms()
        for room in building_rooms:
            if debug: print(room)
            for section in room.getSections():
                if debug: print("-- ", section)

            room_occ_by_time_by_day, interval_name_to_sections_dict, seat_room_occ_by_time_by_day = get_room_occ(room, intervals_dec, seat_utilization, seat_utilization_by_room_occ, both=both)

            room.occupancy_matrix = room_occ_by_time_by_day.T
            if both:
                room.seat_occupancy_matrix = seat_room_occ_by_time_by_day.T
            room.interval_names_to_sections_dict = interval_name_to_sections_dict

    return buildings


def get_room_occ(room, intervals_dec, seat_utilization=False, seat_utilization_by_room_occ=True, debug=False, both=False):
    room_occ_by_time_by_day = np.full((len(intervals_dec), 5), 0.0)
    interval_name_to_sections_dict = {}

    seat_room_occ_by_time_by_day = None
    if both:
        seat_room_occ_by_time_by_day = np.full((len(intervals_dec), 5), 0.0)

    for i_interval in range(len(intervals_dec)-1):
        interval_start = dec_to_time(intervals_dec[i_interval])
        interval_end = dec_to_time(intervals_dec[i_interval+1])

        for section in room.getSections():
            if len(section.end_time) == 0 or len(section.start_time) == 0:
                if not ("Research" in section.title or
                                "Independent Study" in section.title or
                                "Internship" in section.title or
                                "Thesis" in section.title or
                                "Practicum" in section.title):
                    if debug:
                        print("Section has no start and end time for unknown reason:")
                        print(section)
                continue

            section_is_during_interval = int(section.start_time) < interval_end and int(section.end_time) > interval_start

            if section_is_during_interval:
                for day in section.meeting_days:
                    time_interval = time_interval_name(day, interval_start)
                    if time_interval not in interval_name_to_sections_dict:
                        interval_name_to_sections_dict[time_interval] = []
                    interval_name_to_sections_dict[time_interval].append(section)

            if seat_utilization:
                section_is_during_interval = scale_to_seat_utilization(section_is_during_interval, section, seat_utilization_by_room_occ, room)

            section_during_interval_across_days = np.full((1, 5), section_is_during_interval) * section.get_section_days()
            room_occ_by_time_by_day[i_interval] = room_occ_by_time_by_day[i_interval] + section_during_interval_across_days
            room_occ_by_time_by_day[room_occ_by_time_by_day > 1] = 1

            if both:
                seat_section_is_during_interval = scale_to_seat_utilization(section_is_during_interval, section, seat_utilization_by_room_occ, room)
                seat_section_during_interval_across_days = np.full((1, 5),
                                                              seat_section_is_during_interval) * section.get_section_days()
                seat_room_occ_by_time_by_day[i_interval] = seat_room_occ_by_time_by_day[
                                                          i_interval] + seat_section_during_interval_across_days
                seat_room_occ_by_time_by_day[seat_room_occ_by_time_by_day > 1] = 1

    return room_occ_by_time_by_day, interval_name_to_sections_dict, seat_room_occ_by_time_by_day


def scale_to_seat_utilization(section_during_interval, section, seat_utilization_by_room_occ=True, room=None):
    if seat_utilization_by_room_occ:
        section_during_interval *= section.actual_enrollment / room.seat_count
    else:
        section_during_interval *= section.actual_enrollment / section.enrollment_cap

    return section_during_interval