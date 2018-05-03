import csv
import numpy as np
import re

from datetime import datetime
from buildings import get_building_by_code
from time_dec import DAYS
from rooms import Room

class Section:
    def __init__(self, subject, number, title, instructor_id, building, room, start_time, end_time, meeting_days, campus, enrollment_cap, actual_enrollment, start_date, end_date):
        self.subject = subject
        self.number = number
        self.title = title
        self.instructor_id = instructor_id
        self.building = building
        self.room = room
        self.start_time = start_time
        self.end_time = end_time
        self.meeting_days = meeting_days
        self.campus = campus
        self.enrollment_cap = enrollment_cap
        self.actual_enrollment = actual_enrollment
        self.start_date = start_date
        self.end_date = end_date
        self.subsections = []

    def asdict(self):
        dict = {}

        dict['subject'] = self.subject
        dict['number'] = self.number
        dict['title'] = self.title
        dict['instructor_id'] = self.instructor_id
        dict['building'] = str(self.building)
        dict['room'] = str(self.room)
        dict['start_time'] = self.start_time
        dict['end_time'] = self.end_time
        dict['meeting_days'] = self.meeting_days
        dict['campus'] = self.campus
        dict['enrollment_cap'] = self.enrollment_cap
        dict['actual_enrollment'] = self.actual_enrollment
        dict['start_date'] = None
        dict['end_date'] = None
        dict['subsections'] = [section.asdict() for section in self.subsections]

        return dict

    def __str__(self):
        name = self.subject + self.number + " " + self.title
        room = "in " + str(self.room)
        time = "from " + self.start_time + " to " + self.end_time
        days = '/'.join(self.meeting_days)
        enrollment_utilization = "Enrollment: " + str(round(100 * self.actual_enrollment/(self.enrollment_cap if self.enrollment_cap != 0 else 10**10), 1)) + "%"
        seat_utilization = "Seats: " + str(round(100 * self.actual_enrollment/self.room.seat_count, 1)) + "%"

        section_s = ' '.join([name, room, time, days, enrollment_utilization, seat_utilization])
        subsections = ('\n\t - ' if len(self.subsections) > 0 else '') + '\n\t - '.join([str(subsection) for subsection in self.subsections if subsection is not self])

        return section_s + subsections

    def get_section_days(self):
        section_days = np.full((1, 5), 0)

        for i in range(len(DAYS)):
            if DAYS[i] in self.meeting_days:
                section_days[0,i] = 1

        return section_days

    def addSubsection(self, section):
        self.subsections.append(section)
        self.enrollment_cap += section.enrollment_cap
        self.actual_enrollment += section.actual_enrollment


def add_sections_to_rooms(buildings, filename, intersession=False, only_active=True, debug=False, include_all_rooms=False):
    with open(filename, 'rt', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # skip the header

        date_format = "%m/%d/%y"

        n_prev = 5
        prev_rows = [None]*n_prev
        i_prev = 0

        alphabetic_zero_regex = re.compile(r"^[A-Z]0")
        for row in reader:
            if len(row) > 22:
                subject = row[1]
                number = row[2]
                title = row[5]
                primary_instructor = row[6]
                instructor_id = row[7]
                status = row[8]
                campus = row[9]
                start_date_str = row[16]
                end_date_str = row[17]
                building_code = row[18]
                room_number = row[19]
                meeting_days = row[20].split('/')
                start_time = row[21]
                end_time = row[22]

                if ~intersession and campus == "Intersession":
                    if debug: print("Intersession class excluded", row)
                    continue

                if only_active and status != "Active":
                    if debug: print("Not Active class excluded", row)
                    continue

                if len(start_date_str) < 1:
                    if debug: print("ERROR: Start date invalid XXXX ", row)

                end_date = datetime.strptime(end_date_str, date_format)
                start_date = datetime.strptime(start_date_str, date_format)

                enrollment_cap = int('0' + row[11]) # default to zero
                actual_enrollment = int('0' + row[12]) # default to zero

                # Replace ...'s with values from previous row if CRN is the same
                cur_crn = row[4]
                if "..." in {title, primary_instructor, instructor_id, status, campus}:
                    for prev_row in prev_rows:
                        if prev_row is None:
                            continue
                        prev_crn = prev_row[4]
                        if prev_crn == cur_crn:
                            title = prev_row[5]
                            primary_instructor = prev_row[6]
                            instructor_id = prev_row[7]
                            status = prev_row[8]
                            campus = prev_row[9]
                prev_rows[i_prev] = row
                i_prev = (i_prev + 1) % n_prev

                building = get_building_by_code(buildings, building_code)
                if building is not None:
                    if building_code == "SEC":
                        # For sarkeys numbering, remove padded zero
                        # M0204 -> M204
                        if alphabetic_zero_regex.match(room_number) is not None:
                            room_number = room_number[0] + room_number[2:]
                    room = building.get_room(room_number)
                    if room is None and include_all_rooms:
                        room = Room(building, room_number, 1)
                        building.add_room(room)
                    if room is not None:
                            section = Section(subject, number, title, instructor_id, building, room, start_time, end_time, meeting_days, campus, enrollment_cap, actual_enrollment, start_date, end_date)
                            room.addSection(section, debug=debug)
                    else:
                        if debug: print("Building {} Room {} not found in centrally scheduled rooms".format(building_code, room_number))
                else:
                    if debug: print("Building {} not found in centrally scheduled rooms".format(building_code))

    return buildings


if __name__ == "__main__":
    add_sections_to_rooms(load=False, save=True,
                          filename=r'C:\Users\nickb\Google Drive\Career\PACCS\ClassSchedule-23_comma.csv')
