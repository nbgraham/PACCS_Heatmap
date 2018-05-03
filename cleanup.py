import csv
import re

from buildings import get_building_list, get_building_by_name


def schedule():
    with open(r'/home/nick/Downloads/ClassSchedule-23_comma.csv', 'rt', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile)
        date_format = "%m/%d/%y"

        n_prev = 5
        prev_rows = [None] * n_prev
        i_prev = 0

        alphabetic_zero_regex = re.compile(r"^[A-Z]0")

        with open(r'/home/nick/Downloads/ClassSchedule-23_clean.csv', 'wt', encoding='utf8') as outfile:
            writer = csv.writer(outfile)

            for row in reader:
                if len(row) > 22:
                    term = row[0]
                    title = row[5]
                    primary_instructor = row[6]
                    instructor_id = row[7]
                    status = row[8]
                    campus = row[9]

                    # Replace ...'s with values from previous row if CRN is the same
                    cur_crn = row[4]
                    if "..." in {title, primary_instructor, instructor_id, status, campus}:
                        continue
                        for prev_row in prev_rows:
                            if prev_row is None:
                                continue
                            prev_crn = prev_row[4]
                            if prev_crn == cur_crn:
                                term = prev_row[0]
                                title = prev_row[5]
                                primary_instructor = prev_row[6]
                                instructor_id = prev_row[7]
                                status = prev_row[8]
                                campus = prev_row[9]
                    prev_rows[i_prev] = row
                    i_prev = (i_prev + 1) % n_prev

                    row[0] = term
                    row[5] = title
                    row[6] = primary_instructor
                    row[7] = instructor_id
                    row[8] = status
                    row[9] = campus

                    writer.writerow(row)


def rooms():
    buildings = get_building_list([], filename=r'/home/nick/Downloads/building_abbreviations.csv')

    with open(r'/home/nick/Downloads/centrally_scheduled_classrooms.csv', 'rt', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile)
        prev_row_empty = True
        building = None

        with open(r'/home/nick/Downloads/centrally_scheduled_classrooms_clean.csv', 'wt', encoding='utf8') as outfile:
            writer = csv.writer(outfile)

            header = next(reader, None)  # skip the header
            header[0] = 'Room'
            header.insert(0, 'Building')
            writer.writerow(header)

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
                        row.insert(0, building.code)
                        writer.writerow(row)

                if len(row[0]) == 0:
                    prev_row_empty = True


def combine():
    with open(r'/home/nick/Downloads/centrally_scheduled_classrooms_clean.csv', 'rt', encoding='utf8') as rooms_file:
        with open(r'/home/nick/Downloads/ClassSchedule-23_clean.csv', 'rt', encoding='utf8') as classes_file:
            with open(r'/home/nick/Downloads/class_rooms.csv', 'wt', encoding='utf8') as outfile:
                out = csv.writer(outfile)
                classes_reader = csv.reader(classes_file)
                rooms_reader = csv.reader(rooms_file)

                class_header = next(classes_reader)
                room_header = next(rooms_reader)
                header = class_header[:-1]
                header.extend(room_header[2:])
                out.writerow(header)

                for class_row in classes_reader:
                    building = class_row[18]
                    room = class_row[19]

                    rooms_file.seek(0)
                    for room_row in rooms_reader:
                        if building == room_row[0] and room == room_row[1]:
                            row = class_row[:-1]
                            row.extend(room_row[2:])
                            out.writerow(row)
                            break




if __name__ == "__main__":
    combine()