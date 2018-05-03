import numpy as np

DAYS = ['M', 'T', 'W', 'R', 'F']


def get_time_interval_name(i_interval, i_day, intervals_dec):
    day = DAYS[i_day]
    interval = intervals_dec[i_interval]

    time_interval = day + ' ' + str(interval)

    return time_interval

def time_interval_name(day, time_dec):
    return day + ' ' + str(time_dec)


def get_ticks_per_day(dec_list, day_list):
    time_str_ticks = dec_to_time_str(dec_list)

    new_ticks_list = []

    for day in day_list:
        for time_str in time_str_ticks:
            new_ticks_list.append(day + " " + time_str)

    return new_ticks_list


'''
Converts time as decimal to a decimal representation that matches clock (base 60 for minutes)
    800 to
    1630 to 1630
    1260 to 1300
    990 to 1030 
'''
def dec_to_time(dec):
    dec_minutes = dec % 100
    if dec_minutes >= 60:
        return dec - 60 + 100
    else:
        return dec


def dec_to_time_str(dec):
    dec_a = np.array(dec)
    minutes = dec_a % 100
    hours24 =(dec_a / 100).astype(int)

    pm = (hours24 / 12.0) > 1
    hours12 = hours24
    hours12[pm] = hours12[pm] % 12

    time_list = []
    for i in range(len(hours12)):
        time_str = str(hours12[i]) + ":" + minutes_to_string(minutes[i])
        time_list.append(time_str)

    return time_list


def minutes_to_string(minutes):
    if minutes < 10:
        return "0" + str(minutes)
    else:
        return str(minutes)


'''
Takes in start_time and end_time as decimals
    800 for 8:00 or 8:00 am
    1630 for 16:30 or 4:30 pm
interval as an integer number of minutes

Returns a list of the start times of all intervals of length `interval` between start_time and end_time
    end_time is either the last minute in the last interval or included within the last interval
'''
def get_intervals_dec(start_time, end_time, interval):
    intervals_dec = []

    interval_start = dec_to_time(start_time)
    interval_end = interval_start
    while interval_start < end_time:
        interval_start = dec_to_time(interval_end)
        interval_end = dec_to_time(interval_start + interval)
        intervals_dec.append(interval_start)

    return intervals_dec
