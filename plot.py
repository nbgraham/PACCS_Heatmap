import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

from time_dec import DAYS, get_ticks_per_day, get_time_interval_name
from time_windows import get_default_time_windows
from my_colormap import red_green, red_green_high


def plot_room_efficiency(buildings, intervals_dec, get_room_occ, building_codes=[],
                         min_room_size=None, max_room_size=None, colorbar=True, seat_utilization=False):
    buildings = filtered(buildings, building_codes, min_room_size, max_room_size)
    if len(buildings) == 0:
        return -1

    sorted_rooms, occupancy = get_sorted_rooms_occupancy(buildings, ravel=False, seat_utilization=seat_utilization)

    rooms_str = [str(room) for room in sorted_rooms]
    windows = get_default_time_windows(intervals_dec)

    eff_matrix = compute_window_efficiency(occupancy, windows)

    def onclick(event):
        if event.ydata is not None and event.xdata is not None:
            i_room = int(round(event.ydata))
            i_window = int(round(event.xdata))

            room = sorted_rooms[i_room]
            room_str = str(room)

            window = windows[i_window]

            room_occupancy_by_time_by_day, time_interval_to_room_sections_dict = get_room_occ(room, intervals_dec)
            plot_heap_map_one_room(room_occupancy_by_time_by_day.T, room_str, time_interval_to_room_sections_dict,
                                   intervals_dec, window, colorbar=colorbar)

            print_room_window_summary(room_str, window, time_interval_to_room_sections_dict)

    fig = plt.figure()
    cid_up = fig.canvas.mpl_connect('button_press_event', onclick)
    fig.canvas.set_window_title('Room usage across time windows')
    im = plt.imshow(eff_matrix, vmin=0, vmax=1, cmap=red_green_high)
    if colorbar:
        fig.colorbar(im)

    for i_room in range(len(eff_matrix)):
        for i_window in range(len(windows)):
            perc_text = str(int(100*eff_matrix[i_room,i_window]))
            plt.text(i_window,i_room, perc_text, va='center', ha='center')

    plt.yticks(np.arange(len(rooms_str)), rooms_str)
    plt.xticks(np.arange(len(windows)), [window.label for window in windows])
    plt.xticks(rotation=90)
    plt.show()


def compute_window_efficiency(occupancy, windows):
    eff_matrix = np.zeros((len(occupancy), len(windows)))

    for i_window in range(len(windows)):
        window = windows[i_window]
        occupancy_during_window = occupancy * window.total_slots
        for i_room in range(len(occupancy)):
            eff_matrix[i_room, i_window] = np.sum(occupancy_during_window[i_room]) / np.sum(window.total_slots)

    return eff_matrix


def sort_by_room_name(rooms_str, occupancy_list):
    rooms_a = np.array(rooms_str).T
    occupancy_a = np.array(occupancy_list)

    room_inds = rooms_a.argsort()
    sorted_rooms_str = rooms_a[room_inds]
    sorted_occupancy_array = occupancy_a[room_inds]

    occupancy = occupancy_list_by_day_to_week(sorted_occupancy_array)

    return sorted_rooms_str, occupancy


def occupancy_list_by_day_to_week(occupancy_array):
    occupancy_list = []
    for i in range(len(occupancy_array)):
        occupancy_list.append(occupancy_array[i].ravel())

    occupancy = np.vstack(occupancy_list)

    return occupancy


def plot_heap_map_one_room(room_occupancy, room_str, room_dict, intervals_dec, window=None, colorbar=True):
    if window is not None:
        room_occupancy += 2*(1 - window.total_slots)
        room_occupancy[room_occupancy >= 2] = -1

    def onclick(event):
        if event.ydata is not None and event.xdata is not None:
            i_day = int(round(event.ydata))
            i_interval_day = int(round(event.xdata))

            interval_code = get_time_interval_name(i_interval_day, i_day, intervals_dec)

            print(room_str, interval_code)
            if interval_code in room_dict:
                sections = room_dict[interval_code]

                for section in sections:
                    print("   {}".format(section))
            else:
                print("   No class during this time")

            if window is not None:
                print("   Interval in window: {}".format(window.time_included(interval_code)))

    fig = plt.figure()
    fig.canvas.set_window_title("{} {}".format(room_str, window.label if window is not None else ""))
    cid_up = fig.canvas.mpl_connect('button_press_event', onclick)
    plot_occupancy_one_room(room_occupancy, intervals_dec, colorbar=colorbar)
    plt.show()


def filtered(buildings, building_codes, min_room_size, max_room_size):
    if len(building_codes) > 0:
        buildings = {code: buildings[code] for code in building_codes}

    for code, building in buildings.items():
        building.filtered_rooms = building.filter_rooms(min_room_size, max_room_size)

    return buildings


def plot_heat_map(buildings, intervals_dec, days_to_plot=[], building_codes=[],
                  min_room_size=None, max_room_size=None, colorbar=True, seat_utilization=False):
    buildings = filtered(buildings, building_codes, min_room_size, max_room_size)
    if all(len(building.filtered_rooms) == 0 for code, building in buildings.items()):
        return -1

    sorted_rooms, occupancy = get_sorted_rooms_occupancy(buildings, seat_utilization=seat_utilization)

    def onclick_day(day):
        def f(event):
            return onclick(event, day)
        return f

    def onclick(event, day=None):
        if event.ydata is not None and event.xdata is not None:
            i_room = int(round(event.ydata))
            i_interval = int(round(event.xdata))

            if day is None:
                i_day = int(i_interval/len(intervals_dec))
                i_interval_day = i_interval%len(intervals_dec)
            else:
                i_day = day
                i_interval_day = i_interval

            interval_code = get_time_interval_name(i_interval_day, i_day, intervals_dec)

            room = sorted_rooms[i_room]

            print(room, interval_code)
            if interval_code in room.interval_names_to_sections_dict:
                sections = room.interval_names_to_sections_dict[interval_code]

                for section in sections:
                    print("   {}".format(section))
            else:
                print("   No class during this time")

    total_ticks = get_ticks_per_day(intervals_dec, DAYS)
    if len(days_to_plot) == 0:
        fig = plt.figure()
        fig.canvas.set_window_title('Weekly heat map')
        cid_up = fig.canvas.mpl_connect('button_press_event', onclick)
        plot_occupancy(occupancy, sorted_rooms, intervals_dec, total_ticks, len(DAYS), colorbar=colorbar)
    else:
        for i_day_occupancy in range(len(DAYS)):
            if DAYS[i_day_occupancy] not in days_to_plot:
                continue

            start_range = i_day_occupancy*len(intervals_dec)
            end_range = (i_day_occupancy+1)*len(intervals_dec)
            day_occupancy = occupancy[:,start_range:end_range]

            fig = plt.figure()
            fig.canvas.set_window_title(DAYS[i_day_occupancy] + ' heat map')
            cid_up = fig.canvas.mpl_connect('button_press_event', onclick_day(i_day_occupancy))
            plot_occupancy(day_occupancy, sorted_rooms, intervals_dec, total_ticks[start_range:end_range], 1, colorbar=colorbar)
    plt.show()


def plot_occupancy(occupancy, rooms_str, intervals_dec, total_ticks, n_days, colorbar=True):
    im = plt.imshow(occupancy, cmap=red_green)
    plt.grid(color='w', linestyle='-', linewidth=1)
    if colorbar:
        plt.colorbar(im)

    if len(rooms_str) > 25:
        only_unqiue_prefixes(rooms_str)
        only_unqiue_prefixes(total_ticks, prefix_length=1)

    plt.yticks(np.arange(-.55, len(rooms_str) - .55), rooms_str)
    plt.xticks(np.arange(-.5, len(intervals_dec) * n_days - .5), total_ticks)
    plt.xticks(rotation=90)


def only_unqiue_prefixes(original_list, prefix_length = 6):
    prev = "!" * 10
    for i in range(len(original_list)):
        cur = str(original_list[i])
        if prev[:prefix_length] == cur[:prefix_length]:
            original_list[i] = ""
        else:
            room_str = str(original_list[i])
            original_list[i] = " ".join(room_str.split(" ")[:-1])
        prev = cur


def plot_occupancy_one_room(occupancy, intervals_dec, colorbar=True):
    im = plt.imshow(occupancy, cmap=red_green)
    plt.grid(color='w', linestyle='-', linewidth=1)
    if colorbar:
        plt.colorbar(im)
    plt.yticks(np.arange(-.55, len(DAYS) - .55), DAYS)
    plt.xticks(np.arange(-.5, len(intervals_dec) - .5), intervals_dec)
    plt.xticks(rotation=90)


def plot_avg_seat_utilization_by_room(rooms, avg_seat_utilization):
    utilization_a = np.array(avg_seat_utilization).reshape((-1,1))
    rooms_str = [str(room) for room in rooms]

    fig = plt.figure()
    fig.canvas.set_window_title('Average seat utilization of the classes in each room')
    im = plt.imshow(utilization_a, vmin=0, vmax=1, cmap=red_green_high)
    fig.colorbar(im)
    plt.yticks(np.arange(len(rooms_str)), rooms_str)
    plt.show()


def print_room_window_summary(room_str, window, time_interval_to_room_sections_dict):
    print(room_str)
    print(window.label)

    n_intervals_occupied = 0
    for time_interval in window.interval_names:
        print(time_interval)
        if time_interval in time_interval_to_room_sections_dict:
            n_intervals_occupied += 1
            sections = time_interval_to_room_sections_dict[time_interval]
            for section in sections:
                print("-- ", str(section))
        else:
            print(" -- EMPTY")
    occupancy_perc = round(n_intervals_occupied / len(window.interval_names) * 100, 2)
    print("Interval occupancy: {}%".format(occupancy_perc))


def get_sorted_rooms_occupancy(buildings, ravel=True, seat_utilization=False):
    sorted_rooms = []
    occupancy_list = []
    for _, building in buildings.items():
        cur_sorted_rooms = building.get_sorted_rooms(filtered=True)
        sorted_rooms.extend(cur_sorted_rooms)
        for room in cur_sorted_rooms:
            matrix = room.seat_occupancy_matrix if seat_utilization else room.occupancy_matrix
            a = matrix.ravel() if ravel else matrix
            occupancy_list.append(a)

    occupancy = np.vstack(occupancy_list) if ravel else occupancy_list
    return sorted_rooms, occupancy
