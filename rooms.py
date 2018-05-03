import csv

from buildings import get_building_by_name
from time_dec import time_interval_name
from str_dist import str_distance


class Room:
    def __init__(self, building, number, seat_count):
        self.building = building
        self.number = number
        self.sections = {}
        self.seat_count = seat_count
        self.occupancy_matrix = None
        self.seat_occupancy_matrix = None
        self.interval_names_to_sections_dict = None

    def asdict(self):
        dict = {}
        dict['building'] = str(self.building)
        dict['number'] = self.number
        dict['sections'] = {interval: [section.asdict() for section in interval_sections] for interval, interval_sections in self.sections.items()}
        dict['seat_count'] = self.seat_count
        dict['occupancy_matrix'] = self.occupancy_matrix.tolist()
        dict['seat_occupancy_matrix'] = self.seat_occupancy_matrix.tolist()
        dict['interval_names_to_sections_dict'] = {interval: [section.asdict() for section in interval_sections] for interval, interval_sections in self.interval_names_to_sections_dict.items()}

        return dict

    def __str__(self):
        return (self.building.name if self.building else "NO_BUILDING") + " " + self.number

    def __eq__(self,other):
        return self.number == other.room_number and self.building == other.building

    def addSection(self, section, debug=False):
        time_interval = time_interval_name(section.meeting_days[0], section.start_time)
        if time_interval not in self.sections:
            self.sections[time_interval] = [section]
        else:
            # Another section in the same room at the same weekly time and day
            existing_sections = self.sections[time_interval]
            for i_existing_section in range(len(existing_sections)):
                existing_section = existing_sections[i_existing_section]
                if section.end_date < existing_section.start_date:
                    self.sections[time_interval].insert(i_existing_section,section)
                    break
                elif section.start_date > existing_section.end_date:
                    continue
                elif existing_section.instructor_id == section.instructor_id:
                    existing_section.addSubsection(section)
                    break
                elif (str_distance(existing_section.title, section.title) / len(section.title) < 0.3 or existing_section.number[1:] == section.number[1:]) and (existing_section.enrollment_cap + section.enrollment_cap) <= self.seat_count:
                    existing_section.addSubsection(section)
                    if debug:
                        print("YYY two classes in the same room at the same time during the same time of year with different teachers YYY")
                        print("YYY but they have similair titles or course numbers and the combined enrollment cap is less than the room cap YYY")
                        print("YYY ", existing_section, " YYY")
                        print("YYY ", section, " YYY")
                    break
                else:
                    if debug:
                        print("XXX two classes in the same room at the same time during the same time of year with different teachers XXX")
                        print("XXX ", existing_section, " XXX")
                        print("XXX ", section, " XXX")
                    return

            if section.start_date > existing_sections[-1].end_date:
                self.sections[time_interval].append(section)

    def getSections(self):
        sections = []
        for room_sections in self.sections.values():
            sections.extend(room_sections)
        return sections


def add_rooms_to_buildings(buildings, filename, min_room_size=None, max_room_size=None):
    with open(filename, 'rt', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile)
        prev_row_empty = True
        building = None

        next(reader, None)  # skip the header
        for row in reader:
            if prev_row_empty:
                # New building
                building_name = row[0]
                building_name = building_name.replace('\n',' ')
                building = get_building_by_name(buildings, building_name)
                prev_row_empty = False
            elif len(row[0]) > 0:
                # Same building, new room
                if building is not None:
                    number = row[0]
                    seat_count = int(row[1])

                    if (max_room_size is None or seat_count < max_room_size) and (min_room_size is None or seat_count > min_room_size):
                        room = Room(building, number, seat_count)
                        building.add_room(room)

            if len(row[0]) == 0:
                prev_row_empty = True

    return buildings


if __name__ == "__main__":
    pass




