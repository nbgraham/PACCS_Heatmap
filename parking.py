import csv

from matplotlib import pyplot as plt
import numpy as np

from run import get_buildings_with_sections_for_time
from str_dist import str_distance
from time_dec import get_intervals_dec, DAYS


def get_int_enrollment(debug=False, building_codes=None, grid=None, max_dist=None, scale_by_dist=False):
    interval_to_enrollment, intervals_with_days, intervals_dec = get_interval_enrollment(debug=debug,
                                                                                         building_codes=building_codes, grid=grid, max_dist=max_dist, scale_by_dist=scale_by_dist)

    enrollment_matrix = to_matrix(interval_to_enrollment, intervals_with_days)

    plot_enrollment_matrix(enrollment_matrix, intervals_dec)


def add_days(intervals_dec):
    intervals_with_days = []

    for day in DAYS:
        for interval in intervals_dec:
            intervals_with_days.append(day + " " + str(interval))

    return intervals_with_days


def plot_enrollment_matrix(enrollment_matrix, intervals_dec):
    im = plt.imshow(enrollment_matrix)
    plt.grid(color='w', linestyle='-', linewidth=1)
    
    plt.title("# of enrolled students per time slot")

    max = np.max(enrollment_matrix)
    for i_day in range(len(enrollment_matrix)):
        for i_interval in range(len(enrollment_matrix[i_day])):
            val = int(enrollment_matrix[i_day,i_interval])
            perc_text = str(val)
            if val > .75*max:
                plt.text(i_interval,i_day, perc_text, va='center', ha='center', color="black")
            else:
                plt.text(i_interval, i_day, perc_text, va='center', ha='center', color="white")

    plt.yticks(np.arange(-.55, len(DAYS) - .55), DAYS)
    plt.xticks(np.arange(-.5, len(intervals_dec) - .5), intervals_dec)
    plt.xticks(rotation=90)

    plt.show()


def to_matrix(interval_to_enrollment, intervals_with_days):
    enrollment = [interval_to_enrollment[interval] for interval in intervals_with_days]
    arr = np.array(enrollment)
    arr = arr.reshape((5,-1))
    arr = arr[:,:-1]
    return arr


def get_interval_enrollment(debug=False, building_codes=None, grid=None, max_dist=None, scale_by_dist=False):
    buildings, intervals_dec = get_buildings_with_sections_for_time(
        building_filename=r'C:\Users\nickb\Google Drive\Career\PACCS\building_abbreviations.csv',
        room_filename=r'C:\Users\nickb\Google Drive\Career\PACCS\centrally_scheduled_classrooms.csv',
        class_filename=r'C:\Users\nickb\Google Drive\Career\PACCS\ClassSchedule-23_comma.csv',
        seat_utilization=False,
        debug=debug, include_all_rooms=True,
    start_time=730,
    end_time=2200)

    read_grid(r'C:\Users\nickb\Google Drive\Career\PACCS\buildings_grid.csv', buildings)

    intervals_with_days = add_days(intervals_dec)
    interval_to_enrollment = {interval: 0 for interval in intervals_with_days}

    for code, building in buildings.items():
        dist = 1
        if building_codes is not None and code not in building_codes:
            continue
        if grid is not None:
            if max_dist is not None and building.dist(grid) > max_dist:
                continue
            if scale_by_dist:
                dist = building.dist(grid)
        for number, room in building.rooms.items():
            for interval, sections in room.interval_names_to_sections_dict.items():
                if interval in interval_to_enrollment:
                    for section in sections:
                        interval_to_enrollment[interval] += section.actual_enrollment/dist

    return interval_to_enrollment, intervals_with_days, intervals_dec


def read_grid(filename, buildings, debug=False):
    rows = []
    with open(filename, 'rt', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # skip the header

        for row in reader:
            rows.append(row)

    for code, building in buildings.items():
        min_dist = 1.0
        diff = 0.0
        match = None

        for row in rows:
            grid = row[0]
            name = row[1]

            dist = str_distance(name, building.name) / len(building.name)
            if dist < min_dist:
                diff = min_dist - dist
                min_dist = dist
                match = row
            elif dist - min_dist < diff:
                diff = dist - min_dist

            nums = [('One', '1'), ('Two','2'), ('Three', '3'), ('Four', '4'), ('Five', '5'), ['Laboratory','Lab']]
            for pair in nums:
                if pair[0] in name:
                    new_name = name.replace(pair[0], pair[1])
                    dist = str_distance(new_name, building.name) / len(building.name)
                    if dist < min_dist:
                        diff = min_dist-dist
                        min_dist = dist
                        match = row
                    elif dist - min_dist < diff:
                        diff = dist-min_dist


        if min_dist < 0.5:
            cert = (diff - min_dist + 1)/2

            if debug:
                print('{} -> {}'.format(building.name, match[1]))
                print("Match certainty: {}%".format(round(cert *100)) )

            if cert < 0.75 and min_dist > 0:
                match_name = match[1]
                new_match = match_name.replace('Center', '').replace('Hall','').replace('Building','')
                new_name = building.name.replace('Center', '').replace('Hall','').replace('Building','')

                if debug:
                    print("  -- Questionable")

                    shaved_dist = str_distance(new_match, new_name) / len(new_name)
                    if shaved_dist > 0.3:
                        print(" -- Very Questionable")

            building.grid = match[0]


if __name__ == "__main__":
    get_int_enrollment(debug=False, grid='I6', scale_by_dist=True)
