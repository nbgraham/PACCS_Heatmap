from time_dec import DAYS, dec_to_time
import numpy as np


def get_total_possible(intervals_dec, start_time=730, end_time=2200, total_days=DAYS):
    possible_slots = np.array(intervals_dec)
    possible_slots[possible_slots < start_time] = 0
    possible_slots[possible_slots > end_time] = 0
    possible_slots[possible_slots != 0] = 1

    possible_slots_days = []
    for day in DAYS:
        if day in total_days:
            possible_slots_days.append(possible_slots)
        else:
            possible_slots_days.append(np.zeros(possible_slots.shape))

    return np.vstack(possible_slots_days)


def get_total_possible_all(intervals_dec, start_time=730, start_day='M',end_time=2200, end_day='F'):
    possible_slots = np.array(intervals_dec)

    first_day_possible_slots = np.copy(possible_slots)
    first_day_possible_slots[first_day_possible_slots<start_time] = 0
    first_day_possible_slots[first_day_possible_slots!=0] = 1

    last_day_possible_slots = np.copy(possible_slots)
    last_day_possible_slots[last_day_possible_slots < start_time] = 0
    last_day_possible_slots[last_day_possible_slots != 0] = 1

    middle_days_possible_slots = np.ones(possible_slots.shape)
    outside_days_possible_slots = np.zeros(possible_slots.shape)

    start_day_i = DAYS.index(start_day)
    end_day_i = DAYS.index(end_day)

    # Add days before
    possible_slots_days = [outside_days_possible_slots]*start_day_i

    # Add start, middle, and end days
    if start_day_i == end_day_i:
        possible_slots_days.append(first_day_possible_slots*last_day_possible_slots)
    else:
        possible_slots_days.append(first_day_possible_slots)
        possible_slots_days.extend([middle_days_possible_slots]*(end_day_i-start_day_i-1))
        possible_slots_days.append(last_day_possible_slots)

    # Add days after
    possible_slots_days.extend([outside_days_possible_slots]*(len(DAYS)-end_day_i-1))

    return np.vstack(possible_slots_days)


def number_of_intervals(interval, start_time=900, end_time=1600, days=DAYS):
    intervals = 0
    interval_time = dec_to_time(start_time + interval)
    while interval_time <= end_time:
        interval_time = dec_to_time(interval_time + interval)
        intervals += 1

    return intervals * len(days)


def number_of_intervals_d(interval, start_time=900,start_day='M', end_time=1600, end_day='F', day_start=730, day_end=2200):
    intervals = 0
    interval_time, interval_day = dec_to_time_day(start_time + interval, start_day, day_start=day_start, day_end=day_end)
    while DAYS.index(interval_day) <= DAYS.index(end_day):
        if DAYS.index(interval_day) != DAYS.index(end_day) or interval_time <= end_time:
            intervals += 1
        else:
            break # end time on end day is passed
        interval_time, interval_day = dec_to_time_day(interval_time + interval, interval_day, day_start=day_start,
                                                          day_end=day_end)

    return intervals


def dec_to_time_day(dec, day, day_start, day_end):
    time = dec_to_time(dec)
    new_day = day
    while time > day_end:
        time = dec_to_time(time - day_end + day_start)
        new_day = DAYS[DAYS.index(new_day)+1]

    return time, new_day


if __name__ == "__main__":
    all = number_of_intervals(30,start_time=730,end_time=2200)
    print(all)
    prime_time = number_of_intervals(30,start_time=900,end_time=1429)
    print(prime_time)
    mwf_prime_time = number_of_intervals(30, start_time=900, end_time=1429, days=['M','W','F'])
    print(mwf_prime_time)
    tr_prime_time = number_of_intervals(30, start_time=900, end_time=1429, days=['T','R'])
    print(tr_prime_time)
    all_eF = number_of_intervals_d(30, start_time=730, start_day='M',end_time=1630, end_day='F')
    print(all_eF)

