import fastf1
import fastf1 as ff1
import numpy as np
import matplotlib as mpl
import fastf1.plotting
import seaborn as sns
import mplcyberpunk
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import operator
import pandas as pd
from fastf1.core import Laps
from fastf1 import utils
from timple.timedelta import strftimedelta
from matplotlib import cm
from matplotlib.colors import to_rgba
from fastf1.ergast import Ergast


# predkosc kierowcy na najszybszym okrazeniu
def get_speed_telemetry(year, event_name, driver, ses):
    colormap = mpl.cm.plasma
    session = ff1.get_session(year, event_name, ses)
    session.load()
    lap = session.laps.pick_driver(driver).pick_fastest()

    # Get telemetry data
    x = lap.telemetry['X']              # values for x-axis
    y = lap.telemetry['Y']              # values for y-axis
    color = lap.telemetry['Speed']      # value to base color gradient on
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
    fig.suptitle(f'{year} {session.event["EventName"]} - {driver} - Speed', size=24, y=0.97)

    # Adjust margins and turn of axis
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
    ax.axis('off')

    ax.plot(lap.telemetry['X'], lap.telemetry['Y'], color='black', linestyle='-', linewidth=16, zorder=0)
    norm = plt.Normalize(color.min(), color.max())
    lc = LineCollection(segments, cmap=colormap, norm=norm, linestyle='-', linewidth=5)
    lc.set_array(color)

    cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
    normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
    legend = mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=colormap, orientation="horizontal")
    plt.show()


# prędkość kierowcy na najszybszym okrążeniu wraz z oznaczeniami zakrętów
def get_speed_traces_with_corner_annotations(year, event_name, driver, ses):
    fastf1.plotting.setup_mpl(misc_mpl_mods=False)

    session = fastf1.get_session(year, event_name, ses)
    session.load()
    fastest_lap = session.laps.pick_driver(driver).pick_fastest()

    car_data = fastest_lap.get_car_data().add_distance()
    circuit_info = session.get_circuit_info()
    team_color = fastf1.plotting.team_color(fastest_lap['Team'])
    fig, ax = plt.subplots()
    ax.plot(car_data['Distance'], car_data['Speed'],
            color=team_color, label=fastest_lap['Driver'])

    v_min = car_data['Speed'].min()
    v_max = car_data['Speed'].max()
    ax.vlines(x=circuit_info.corners['Distance'], ymin=v_min - 20, ymax=v_max + 20,
              linestyles='dotted', colors='grey')
    for _, corner in circuit_info.corners.iterrows():
        txt = f"{corner['Number']}{corner['Letter']}"
        ax.text(corner['Distance'], v_min - 30, txt,
                va='center_baseline', ha='center', size='small')

    ax.set_xlabel('Distance in m')
    ax.set_ylabel('Speed in km/h')
    ax.legend()
    plt.suptitle(f"{session.event['EventName']} {year} speed traces with corners annotations")
    ax.set_ylim([v_min - 40, v_max + 20])

    plt.show()


# porownanie predkosci dwoch kierowcow na najszybszym okrazeniu  w danej sesji
def overlaying_speed_traces_of_two_drivers(year, event_name, driver1, driver2, ses):
    plt.style.use("cyberpunk")
    session = fastf1.get_session(year, event_name, ses)
    session.load()
    driver1_lap = session.laps.pick_driver(driver1).pick_fastest()
    driver2_lap = session.laps.pick_driver(driver2).pick_fastest()
    driver1_tel = driver1_lap.get_car_data().add_distance()
    driver2_tel = driver2_lap.get_car_data().add_distance()
    driver1_color = fastf1.plotting.team_color(driver1_lap['Team'])
    driver2_color = fastf1.plotting.team_color(driver2_lap['Team'])
    fig, ax = plt.subplots(figsize=(16, 9), dpi=100)

    ax.plot(driver1_tel['Distance'], driver1_tel['Speed'], color=driver1_color, label=driver1)
    ax.plot(driver2_tel['Distance'], driver2_tel['Speed'], color=driver2_color, label=driver2)

    circuit_info = session.get_circuit_info()
    ax.vlines(x=circuit_info.corners['Distance'], ymin=40, ymax=370,
              linestyles='dotted', colors='grey')
    for _, corner in circuit_info.corners.iterrows():
        txt = f"{corner['Number']}{corner['Letter']}"
        ax.text(corner['Distance'], 50, txt,
                va='center_baseline', ha='center', size='small')
    ax.set_xlabel('Distance in m')
    ax.set_ylabel('Speed in km/h')
    ax.legend()
    plt.title(f"Fastest Lap Comparison {driver1} and {driver2}\n "
                 f"{session.event['EventName']} {session.event.year} {session.name}\n"
              f"{driver1}: {strftimedelta(session.laps.pick_driver(driver1).pick_fastest()['LapTime'], '%m:%s.%ms')}\n"
              f"{driver2}: {strftimedelta(session.laps.pick_driver(driver2).pick_fastest()['LapTime'], '%m:%s.%ms')}\n")

    plt.show()


def overlaying_rpm_traces_of_two_drivers(year, event_name, driver1, driver2, ses):
    fastf1.plotting.setup_mpl(misc_mpl_mods=False)
    session = fastf1.get_session(year, event_name, ses)
    session.load()
    driver1_lap = session.laps.pick_driver(driver1).pick_fastest()
    driver2_lap = session.laps.pick_driver(driver2).pick_fastest()
    driver1_tel = driver1_lap.get_car_data().add_distance()
    driver2_tel = driver2_lap.get_car_data().add_distance()
    driver1_color = fastf1.plotting.team_color(driver1_lap['Team'])
    driver2_color = fastf1.plotting.team_color(driver2_lap['Team'])
    fig, ax = plt.subplots(figsize=(16, 9), dpi=100)

    ax.plot(driver1_tel['Distance'], driver1_tel['RPM'], color=driver1_color, label=driver1)
    ax.plot(driver2_tel['Distance'], driver2_tel['RPM'], color=driver2_color, label=driver2)

    circuit_info = session.get_circuit_info()
    ax.vlines(x=circuit_info.corners['Distance'], ymin=70, ymax=12000,
              linestyles='dotted', colors='grey')
    for _, corner in circuit_info.corners.iterrows():
        txt = f"{corner['Number']}{corner['Letter']}"
        ax.text(corner['Distance'], 70, txt,
                va='center_baseline', ha='center', size='small')
    ax.set_xlabel('Distance in m')
    ax.set_ylabel('Speed in km/h')
    ax.legend()
    plt.title(f"RPM comparison {driver1} and {driver2}\n "
              f"{session.event['EventName']} {session.event.year} {session.name}")
    plt.show()


def comparison_of_throttle_pressure_for_two_drivers(year, event_name, driver1, driver2, ses):
    plt.style.use("cyberpunk")
    # load a session and its telemetry data
    session = fastf1.get_session(year, event_name, ses)
    session.load()
    driver1_lap = session.laps.pick_driver(driver1).pick_fastest()
    driver2_lap = session.laps.pick_driver(driver2).pick_fastest()
    driver1_tel = driver1_lap.get_car_data().add_distance()
    driver2_tel = driver2_lap.get_car_data().add_distance()
    driver1_color = fastf1.plotting.team_color(driver1_lap['Team'])
    driver2_color = fastf1.plotting.team_color(driver2_lap['Team'])
    fig, ax = plt.subplots(figsize=(16, 9), dpi=100)

    ax.plot(driver1_tel['Distance'], driver1_tel['Throttle'], color=driver1_color, label=driver1)
    ax.plot(driver2_tel['Distance'], driver2_tel['Throttle'], color=driver2_color, label=driver2)

    circuit_info = session.get_circuit_info()
    ax.vlines(x=circuit_info.corners['Distance'], ymin=0, ymax=100,
              linestyles='dotted', colors='grey')
    for _, corner in circuit_info.corners.iterrows():
        txt = f"{corner['Number']}{corner['Letter']}"
        ax.text(corner['Distance'], 0, txt,
                va='center_baseline', ha='center', size='small')
    ax.set_xlabel('Distance in m')
    ax.set_ylabel('Throttle pressure in %')
    ax.legend()
    plt.title(f"Comparison of throttle pressure for {driver1} and {driver2}\n "
              f"{session.event['EventName']} {session.event.year} {session.name}")
    plt.show()


def comparison_of_gear_number_for_two_drivers(year, event_name, drivers, ses):
    # load a session and its telemetry data
    session = fastf1.get_session(year, event_name, ses)
    session.load()
    plt.style.use("cyberpunk")

    fig, ax = plt.subplots(figsize=(16, 9), dpi=100)

    for driver in drivers:
        driver1_lap = session.laps.pick_driver(driver).pick_fastest()
        driver1_tel = driver1_lap.get_car_data().add_distance()
        driver1_color = fastf1.plotting.team_color(driver1_lap['Team'])
        ax.plot(driver1_tel['Distance'], driver1_tel['nGear'], color=driver1_color, label=driver)

    circuit_info = session.get_circuit_info()
    ax.vlines(x=circuit_info.corners['Distance'], ymin=0, ymax=8,
              linestyles='dotted', colors='grey')
    for _, corner in circuit_info.corners.iterrows():
        txt = f"{corner['Number']}{corner['Letter']}"
        ax.text(corner['Distance'], 0, txt,
                va='center_baseline', ha='center', size='small')
    ax.set_xlabel('Distance in m')
    ax.set_ylabel('Gear')
    ax.legend()

    plt.title(f"Comparison of brake pressure for {drivers} and {drivers}\n "
              f"{session.event['EventName']} {session.event.year} {session.name}")

    plt.show()


def comparison_of_brake_pressure_for_two_drivers(year, event_name, driver1, driver2, ses):
    fastf1.plotting.setup_mpl(misc_mpl_mods=False)

    # load a session and its telemetry data
    session = fastf1.get_session(year, event_name, ses)
    session.load()
    driver1_lap = session.laps.pick_driver(driver1).pick_fastest()
    driver2_lap = session.laps.pick_driver(driver2).pick_fastest()
    driver1_tel = driver1_lap.get_car_data().add_distance()
    driver2_tel = driver2_lap.get_car_data().add_distance()
    driver1_color = fastf1.plotting.team_color(driver1_lap['Team'])
    driver2_color = fastf1.plotting.team_color(driver2_lap['Team'])
    fig, ax = plt.subplots(figsize=(16, 9), dpi=100)

    ax.plot(driver1_tel['Distance'], driver1_tel['Brake'], color=driver1_color, label=driver1)
    ax.plot(driver2_tel['Distance'], driver2_tel['Brake'], color=driver2_color, label=driver2)

    circuit_info = session.get_circuit_info()
    ax.vlines(x=circuit_info.corners['Distance'], ymin=0, ymax=1,
              linestyles='dotted', colors='grey')
    for _, corner in circuit_info.corners.iterrows():
        txt = f"{corner['Number']}{corner['Letter']}"
        ax.text(corner['Distance'], 0, txt,
                va='center_baseline', ha='center', size='small')
    ax.set_xlabel('Distance in m')
    ax.set_ylabel('Brake in True/False')
    ax.legend()
    plt.title(f"Comparison of brake pressure for {driver1} and {driver2}\n "
              f"{session.event['EventName']} {session.event.year} {session.name}")
    plt.show()


def get_gained_positions_on_first_lap(year, event_name):
    gained_positions = {}
    gaining_position_sum = {}
    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False)

    session = fastf1.get_session(year, event_name, 'R')
    session.load(telemetry=True)
    for driver in session.drivers:
        results = session.results
        first_lap = session.laps.pick_driver(driver).pick_laps(1)
        grid_position = results[results['DriverNumber'] == driver]['GridPosition']
        if int(grid_position) != 0:
            position_after_first_lap = first_lap['Position']
            if not grid_position.empty and not position_after_first_lap.empty:
                gained_positions1 = int(grid_position.iloc[0]) - int(position_after_first_lap.iloc[0])
            else:
                # handle the case when one or both DataFrames are empty
                print("Error: DataFrames are empty.")
            gained_positions[driver] = gained_positions1
            if driver not in gaining_position_sum:
                gaining_position_sum[driver] = [0, 0]
            gaining_position_sum[driver][0] += gained_positions[driver]
            gaining_position_sum[driver][1] += 1
        else:
            print(f"{event_name} kierowca o numerze {driver} rusza z alei serwisowej")
    sorted_driver_times = dict(sorted(gained_positions.items(), key=operator.itemgetter(1)))

    sorted_driver_times_names = list()

    team_colors = list()
    for index in sorted_driver_times:
        try:
            sorted_driver_times_names.append(results[results['DriverNumber'] == index]['Abbreviation'][0])
            color = fastf1.plotting.team_color(results[results['DriverNumber'] == index]['TeamName'].values[0])
            team_colors.append(color)
        except:
            "empty"
    fig, ax = plt.subplots(figsize=(16, 9), dpi=100)
    data = {'driver': list(map(str, sorted_driver_times.keys())),
            'positions': list(sorted_driver_times.values())}
    df = pd.DataFrame(data)
    ax.barh(df.index, df['positions'],
            color=team_colors, edgecolor='grey')
    ax.set_yticks(df.index)
    ax.set_yticklabels(sorted_driver_times_names)

    # show fastest at the top
    ax.invert_yaxis()

    # draw vertical lines behind the bars
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    plt.xlabel('Zyskane pozycje')
    plt.ylabel('Kierowcy')
    plt.title(f"Zyskane pozycje w {session.session_info['Meeting']['Name']} {year}")
    plt.show()


def get_gained_positions_on_first_lap_wall(session, ax=None):
    gained_positions = {}
    gaining_position_sum = {}
    for driver in session.drivers:
        results = session.results
        first_lap = session.laps.pick_driver(driver).pick_laps(1)
        grid_position = results[results['DriverNumber'] == driver]['GridPosition']
        if int(grid_position) != 0:
            position_after_first_lap = first_lap['Position']
            if not grid_position.empty and not position_after_first_lap.empty:
                gained_positions1 = int(grid_position.iloc[0]) - int(position_after_first_lap.iloc[0])
            else:
                # handle the case when one or both DataFrames are empty
                print("Error: DataFrames are empty.")
            gained_positions[driver] = gained_positions1
            if driver not in gaining_position_sum:
                gaining_position_sum[driver] = [0, 0]
            gaining_position_sum[driver][0] += gained_positions[driver]
            gaining_position_sum[driver][1] += 1
        else:
            print(f"{session.session_info['Meeting']['Name']} kierowca o numerze {driver} rusza z alei serwisowej")
    sorted_driver_times = dict(sorted(gained_positions.items(), key=operator.itemgetter(1)))

    sorted_driver_times_names = list()

    team_colors = list()
    for index in sorted_driver_times:
        try:
            sorted_driver_times_names.append(results[results['DriverNumber'] == index]['Abbreviation'][0])
            color = fastf1.plotting.team_color(results[results['DriverNumber'] == index]['TeamName'].values[0])
            team_colors.append(color)
        except:
            "empty"
    data = {'driver': list(map(str, sorted_driver_times.keys())),
            'positions': list(sorted_driver_times.values())}
    df = pd.DataFrame(data)
    ax.barh(df.index, df['positions'],
            color=team_colors, edgecolor='grey')
    ax.set_yticks(df.index)
    ax.set_yticklabels(sorted_driver_times_names)

    # show fastest at the top
    ax.invert_yaxis()

    # draw vertical lines behind the bars
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    ax.set_xlabel('Positions gained')
    ax.set_ylabel('Drivers')
    ax.set_title(f"Positions gained on first lap in {session.session_info['Meeting']['Name']} {session.event.year}")
    return ax


def get_gained_positions_in_full_race(year, event_name):
    gained_positions = {}
    gaining_position_sum = {}
    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False)
    session = fastf1.get_session(year, event_name, 'R')
    session.load(telemetry=True)
    for driver in session.drivers:
        results = session.results
        grid_position = results[results['DriverNumber'] == driver]['GridPosition']
        if int(grid_position) != 0:
            finish_position = results[results['DriverNumber'] == driver]['Position']
            if not grid_position.empty and not finish_position.empty:
                gained_positions1 = int(grid_position.iloc[0]) - int(finish_position.iloc[0])
            else:
                print("Error: DataFrames are empty.")
            gained_positions[driver] = gained_positions1
            if driver not in gaining_position_sum:
                gaining_position_sum[driver] = [0, 0]
            gaining_position_sum[driver][0] += gained_positions[driver]
            gaining_position_sum[driver][1] += 1
        else:
            print(f"{event_name} kierowca o numerze {driver} rusza z alei serwisowej")
    sorted_driver_times = dict(sorted(gained_positions.items(), key=operator.itemgetter(1)))
    results = session.results
    team_colors = list()
    sorted_driver_times_names = list()
    for index in sorted_driver_times:
        try:
            sorted_driver_times_names.append(results[results['DriverNumber'] == index]['Abbreviation'][0])
            color = fastf1.plotting.team_color(results[results['DriverNumber'] == index]['TeamName'].values[0])
            team_colors.append(color)
        except:
            "empty"

    fig, ax = plt.subplots(figsize=(16, 9), dpi=100)
    data = {'driver': list(map(str, sorted_driver_times.keys())),
            'positions': list(sorted_driver_times.values())}
    df = pd.DataFrame(data)
    ax.barh(df.index, df['positions'],
            color=team_colors, edgecolor='grey')
    ax.set_yticks(df.index)
    ax.set_yticklabels(sorted_driver_times_names)

    # show fastest at the top
    ax.invert_yaxis()

    # draw vertical lines behind the bars
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)
    plt.xlabel('Zyskane pozycje')
    plt.ylabel('Kierowcy')
    plt.title(f'Zyskane pozycje w {session.session_info["Meeting"]["Name"]} {year}')
    plt.show()


def get_gained_positions_in_full_race_wall(session, ax=None):
    gained_positions = {}
    gaining_position_sum = {}
    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False)
    for driver in session.drivers:
        results = session.results
        grid_position = results[results['DriverNumber'] == driver]['GridPosition']
        if int(grid_position) != 0:
            finish_position = results[results['DriverNumber'] == driver]['Position']
            if not grid_position.empty and not finish_position.empty:
                gained_positions1 = int(grid_position.iloc[0]) - int(finish_position.iloc[0])
            else:
                print("Error: DataFrames are empty.")
            gained_positions[driver] = gained_positions1
            if driver not in gaining_position_sum:
                gaining_position_sum[driver] = [0, 0]
            gaining_position_sum[driver][0] += gained_positions[driver]
            gaining_position_sum[driver][1] += 1
        else:
            print(f"{session.session_info['Meeting']['Name']} kierowca o numerze {driver} rusza z alei serwisowej")
    sorted_driver_times = dict(sorted(gained_positions.items(), key=operator.itemgetter(1)))
    results = session.results
    team_colors = list()
    sorted_driver_times_names = list()
    for index in sorted_driver_times:
        try:
            sorted_driver_times_names.append(results[results['DriverNumber'] == index]['Abbreviation'][0])
            color = fastf1.plotting.team_color(results[results['DriverNumber'] == index]['TeamName'].values[0])
            team_colors.append(color)
        except:
            "empty"

    data = {'driver': list(map(str, sorted_driver_times.keys())),
            'positions': list(sorted_driver_times.values())}
    df = pd.DataFrame(data)
    ax.barh(df.index, df['positions'],
            color=team_colors, edgecolor='grey')
    ax.set_yticks(df.index)
    ax.set_yticklabels(sorted_driver_times_names)

    # show fastest at the top
    ax.invert_yaxis()

    # draw vertical lines behind the bars
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    ax.set_xlabel('Positions gained')
    ax.set_ylabel('Drivers')
    ax.set_title(f'Position gained in {session.session_info["Meeting"]["Name"]} {session.event.year}')
    return ax


def visualization_of_position_changes_during_the_race(year, event_name):
    fastf1.plotting.setup_mpl(misc_mpl_mods=False)
    session = fastf1.get_session(year, event_name, 'R')
    session.load(telemetry=False, weather=False)

    fig, ax = plt.subplots(figsize=(8.0, 4.9))
    for drv in session.drivers:
        drv_laps = session.laps.pick_driver(drv)

        abb = drv_laps['Driver'].iloc[0]
        color = fastf1.plotting.driver_color(abb)

        ax.plot(drv_laps['LapNumber'], drv_laps['Position'],
                label=abb, color=color)
    ax.set_ylim([20.5, 0.5])
    ax.set_yticks([1, 5, 10, 15, 20])
    ax.set_xlabel('Lap')
    ax.set_ylabel('Position')
    ax.legend(bbox_to_anchor=(1.0, 1.0))
    plt.tight_layout()
    plt.suptitle(f'Zmiana pozycji na przestrzeni wyścigu {session.session_info["Meeting"]["Name"]} {year}')
    plt.show()


def visualization_of_position_changes_during_the_race_wall(session, ax=None):
    for drv in session.drivers:
        drv_laps = session.laps.pick_driver(drv)

        abb = drv_laps['Driver'].iloc[0]
        color = fastf1.plotting.driver_color(abb)

        ax.plot(drv_laps['LapNumber'], drv_laps['Position'],
                label=abb, color=color)
    ax.set_ylim([20.5, 0.5])
    ax.set_yticks([1, 5, 10, 15, 20])
    ax.set_xlabel('Lap')
    ax.set_ylabel('Position')
    ax.legend(bbox_to_anchor=(1.0, 1.0))
    ax.set_title(f'Position change during {session.session_info["Meeting"]["Name"]} {session.event.year} race')
    return ax


def get_0_x_times(year, event_name, speed):
    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)
    session = fastf1.get_session(year, event_name, 'R')
    session.load()
    times_0_200 = {}
    for driver in session.drivers:
        # Pobranie pierwszego okrążenia dla każdego kierowcy
        first_lap = session.laps.pick_driver(driver).pick_laps(1).get_telemetry()
        # Przefiltrowanie danych odnośnie startu 0-200km/h
        filtered_lap = first_lap[
            (first_lap['Time'] <= first_lap[first_lap['Speed'] >= speed]['Time'].iloc[0]) & (first_lap['Speed'] >= 0)][
            ['Speed', 'Time']]
        filtered_lap.to_csv(f'{driver}_first_lap.csv', index=False)
        speed_value_under_200 = filtered_lap['Speed'].iloc[-2]
        driver_0_200_test = first_lap[(first_lap['Speed'] >= speed)][['Speed', 'Time']].iloc[0]
        time_and_speed_before_200 = first_lap[(first_lap['Speed'] < speed)][['Speed', 'Time']].iloc[-1]
        speed_difference = filtered_lap['Speed'].iloc[-1] - filtered_lap['Speed'].iloc[-2]
        time_difference = filtered_lap['Time'].iloc[-1] - filtered_lap['Time'].iloc[-2]
        result = time_difference / speed_difference * (speed - filtered_lap['Speed'].iloc[-2]) + \
                 filtered_lap['Time'].iloc[-2]
        times_0_200[driver] = result.total_seconds()
    sorted_driver_times = dict(sorted(times_0_200.items(), key=operator.itemgetter(1)))

    results = session.results
    team_colors = list()
    sorted_driver_times_names = list()
    for index in sorted_driver_times:
        sorted_driver_times_names.append(results[results['DriverNumber'] == index]['Abbreviation'][0])
        color = fastf1.plotting.team_color(results[results['DriverNumber'] == index]['TeamName'].values[0])
        team_colors.append(color)

    best_time = round(list(sorted_driver_times.values())[0], 3)
    for key, value in sorted_driver_times.items():
        sorted_driver_times[key] = round(sorted_driver_times[key] - best_time, 3)
    data = {'driver': list(map(str, sorted_driver_times.keys())),
            'time': list(sorted_driver_times.values())}

    df = pd.DataFrame(data)
    fig, ax = plt.subplots(figsize=(16, 9), dpi=100)
    ax.barh(df.index, df['time'],
            color=team_colors, edgecolor='grey')
    ax.set_yticks(df.index)
    ax.set_yticklabels(sorted_driver_times_names)

    # show fastest at the top
    ax.invert_yaxis()

    # draw vertical lines behind the bars
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)
    plt.title(f"{session.session_info['Meeting']['Name']} {year} Qualifying\n"
              f"Best time from 0 to {speed}: {sorted_driver_times_names[0]} {best_time}s")
    plt.show()


def get_0_x_times_wall(session, speed, ax=None):
    times_0_200 = {}
    for driver in session.drivers:
        # Pobranie pierwszego okrążenia dla każdego kierowcy
        first_lap = session.laps.pick_driver(driver).pick_laps(1).get_telemetry()
        # Przefiltrowanie danych odnośnie startu 0-200km/h
        filtered_lap = first_lap[
            (first_lap['Time'] <= first_lap[first_lap['Speed'] >= speed]['Time'].iloc[0]) & (first_lap['Speed'] >= 0)][
            ['Speed', 'Time']]
        filtered_lap.to_csv(f'{driver}_first_lap.csv', index=False)
        speed_value_under_200 = filtered_lap['Speed'].iloc[-2]
        driver_0_200_test = first_lap[(first_lap['Speed'] >= speed)][['Speed', 'Time']].iloc[0]
        time_and_speed_before_200 = first_lap[(first_lap['Speed'] < speed)][['Speed', 'Time']].iloc[-1]
        speed_difference = filtered_lap['Speed'].iloc[-1] - filtered_lap['Speed'].iloc[-2]
        time_difference = filtered_lap['Time'].iloc[-1] - filtered_lap['Time'].iloc[-2]
        result = time_difference / speed_difference * (speed - filtered_lap['Speed'].iloc[-2]) + \
                 filtered_lap['Time'].iloc[-2]
        times_0_200[driver] = result.total_seconds()
    sorted_driver_times = dict(sorted(times_0_200.items(), key=operator.itemgetter(1)))

    results = session.results
    team_colors = list()
    sorted_driver_times_names = list()
    for index in sorted_driver_times:
        sorted_driver_times_names.append(results[results['DriverNumber'] == index]['Abbreviation'][0])
        color = fastf1.plotting.team_color(results[results['DriverNumber'] == index]['TeamName'].values[0])  # wysypuje sie przy kick'u
        team_colors.append(color)

    best_time = round(list(sorted_driver_times.values())[0], 3)
    for key, value in sorted_driver_times.items():
        sorted_driver_times[key] = round(sorted_driver_times[key] - best_time, 3)
    data = {'driver': list(map(str, sorted_driver_times.keys())),
            'time': list(sorted_driver_times.values())}

    df = pd.DataFrame(data)
    ax.barh(df.index, df['time'],
            color=team_colors, edgecolor='grey')
    ax.set_yticks(df.index)
    ax.set_yticklabels(sorted_driver_times_names)

    # show fastest at the top
    ax.invert_yaxis()

    # draw vertical lines behind the bars
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)
    ax.set_xlabel('Gap')
    ax.set_ylabel('Drivers')
    ax.set_title(f"{session.session_info['Meeting']['Name']} {session.event.year} Qualifying\n"
                 f"Best time from 0 to {speed}: {sorted_driver_times_names[0]} {best_time}s")
    return ax


# Team pace comparison
def team_pace_comparison(year, event_name):
    session = fastf1.get_session(year, event_name, 'R')
    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)
    session.load()
    laps = session.laps.pick_quicklaps()

    transformed_laps = laps.copy()
    transformed_laps.loc[:, "LapTime (s)"] = laps["LapTime"].dt.total_seconds()

    # order the team from the fastest (lowest median lap time) tp slower
    team_order = (
        transformed_laps[["Team", "LapTime (s)"]]
        .groupby("Team")
        .median()["LapTime (s)"]
        .sort_values()
        .index
    )

    # make a color palette associating team names to hex codes
    team_palette = {team: fastf1.plotting.team_color(team) for team in team_order}

    fig, ax = plt.subplots(figsize=(15, 10))
    sns.boxplot(
        data=transformed_laps,
        x="Team",
        y="LapTime (s)",
        order=team_order,
        palette=team_palette,
        whiskerprops=dict(color="white"),
        boxprops=dict(edgecolor="white"),
        medianprops=dict(color="grey"),
        capprops=dict(color="white"),
    )
    plt.title(f"Team pace comparison of {session.session_info['Meeting']['Name']} {year}")
    plt.grid(visible=False)

    # x-label is redundant
    ax.set(xlabel=None)
    plt.tight_layout()
    plt.savefig("team_pace_comparison.png")
    plt.show()


# Team pace comparison during session
def team_pace_comparison_wall(session, ax=None):
    laps = session.laps.pick_quicklaps()
    transformed_laps = laps.copy()
    transformed_laps.loc[:, "LapTime (s)"] = laps["LapTime"].dt.total_seconds()

    # order the team from the fastest (lowest median lap time) tp slower
    team_order = (
        transformed_laps[["Team", "LapTime (s)"]]
        .groupby("Team")
        .median()["LapTime (s)"]
        .sort_values()
        .index
    )

    # make a color palette associating team names to hex codes
    team_palette = {team: fastf1.plotting.team_color(team) for team in team_order}

    sns.boxplot(
        data=transformed_laps,
        x="Team",
        y="LapTime (s)",
        order=team_order,
        palette=team_palette,
        whiskerprops=dict(color="white"),
        boxprops=dict(edgecolor="white"),
        medianprops=dict(color="grey"),
        capprops=dict(color="white"),
    )
    ax.set_title(f"Team pace comparison of {session.session_info['Meeting']['Name']} {session.event.year}")
    ax.grid(visible=False)
    # x-label is redundant
    ax.set(xlabel=None)
    return ax


# Wizualizacja tempa 10 najlepszych kierowców w sesji
def driver_laptimes_visualization_concrete(year, event_name):
    race = fastf1.get_session(year, event_name, 'R')
    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)
    race.load()
    point_finishers = race.drivers[:10]
    driver_laps = race.laps.pick_drivers(point_finishers).pick_quicklaps()
    driver_laps = driver_laps.reset_index()
    finishing_order = [race.get_driver(i)["Abbreviation"] for i in point_finishers]
    driver_colors = {abv: fastf1.plotting.DRIVER_COLORS[driver] for abv,
    driver in fastf1.plotting.DRIVER_TRANSLATE.items()}

    # create the figure
    fig, ax = plt.subplots(figsize=(10, 5))

    driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()

    sns.violinplot(data=driver_laps,
                   x="Driver",
                   y="LapTime(s)",
                   inner=None,
                   density_norm="area",
                   order=finishing_order,
                   palette=driver_colors
                   )

    sns.swarmplot(data=driver_laps,
                  x="Driver",
                  y="LapTime(s)",
                  order=finishing_order,
                  hue="Compound",
                  palette=fastf1.plotting.COMPOUND_COLORS,
                  hue_order=["SOFT", "MEDIUM", "HARD"],
                  linewidth=0,
                  size=5,
                  )
    ax.set_xlabel("Driver")
    ax.set_ylabel("Lap Time (s)")
    plt.suptitle(f"{race.event['EventName']} {year} Lap Time Distributions")
    sns.despine(left=True, bottom=True)

    plt.tight_layout()
    plt.savefig("driver_laptimes_visualization.png")
    plt.show()


# wizualizacja tempa pokonywania okrazen 10 najlepszych kierowcow w sesji
def driver_laptimes_visualization_wall(year, event_name, ax=None):
    race = fastf1.get_session(year, event_name, 'R')
    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)
    race.load()
    point_finishers = race.drivers[:10]
    driver_laps = race.laps.pick_drivers(point_finishers).pick_quicklaps()
    driver_laps = driver_laps.reset_index()
    finishing_order = [race.get_driver(i)["Abbreviation"] for i in point_finishers]
    driver_colors = {abv: fastf1.plotting.DRIVER_COLORS[driver] for abv,
    driver in fastf1.plotting.DRIVER_TRANSLATE.items()}

    driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()

    sns.violinplot(data=driver_laps,
                   x="Driver",
                   y="LapTime(s)",
                   inner=None,
                   density_norm="area",
                   order=finishing_order,
                   palette=driver_colors,
                   )

    sns.swarmplot(data=driver_laps,
                  x="Driver",
                  y="LapTime(s)",
                  order=finishing_order,
                  hue="Compound",
                  palette=fastf1.plotting.COMPOUND_COLORS,
                  hue_order=["SOFT", "MEDIUM", "HARD"],
                  linewidth=0,
                  size=5,
                  )

    ax.set_xlabel("Driver")
    ax.set_ylabel("Lap Time (s)")
    ax.set_title(f"{race.event['EventName']} {year} Lap Time Distributions")
    sns.despine(left=True, bottom=True)
    return ax


# Wizualizacja stategii opon
def tyre_strategies(year, event_name):
    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False)

    session = fastf1.get_session(year, event_name, 'R')
    session.load()
    laps = session.laps
    drivers = session.drivers
    drivers = [session.get_driver(driver)["Abbreviation"] for driver in drivers]
    stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
    stints = stints.groupby(["Driver", "Stint", "Compound"])
    stints = stints.count().reset_index()
    stints = stints.rename(columns={"LapNumber": "StintLength"})
    fig, ax = plt.subplots(figsize=(5, 10))

    for driver in drivers:
        driver_stints = stints.loc[stints["Driver"] == driver]

        previous_stint_end = 0
        for idx, row in driver_stints.iterrows():
            # each row contains the compound name and stint length
            # we can use these information to draw horizontal bars
            plt.barh(
                y=driver,
                width=row["StintLength"],
                left=previous_stint_end,
                color=fastf1.plotting.COMPOUND_COLORS[row["Compound"]],
                edgecolor="black",
                fill=True
            )

            previous_stint_end += row["StintLength"]
    plt.suptitle(f"{session.event['EventName']} {year} tyre strategies")

    plt.xlabel("Lap Number")
    plt.grid(False)
    # invert the y-axis so drivers that finish higher are closer to the top
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    plt.tight_layout()

    plt.show()


def tyre_strategies_wall(session, ax=None):
    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False)
    laps = session.laps
    drivers = session.drivers
    drivers = [session.get_driver(driver)["Abbreviation"] for driver in drivers]
    stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
    stints = stints.groupby(["Driver", "Stint", "Compound"])
    stints = stints.count().reset_index()
    stints = stints.rename(columns={"LapNumber": "StintLength"})

    for driver in drivers:
        driver_stints = stints.loc[stints["Driver"] == driver]

        previous_stint_end = 0
        for idx, row in driver_stints.iterrows():
            # each row contains the compound name and stint length
            # we can use these information to draw horizontal bars
            ax.barh(
                y=driver,
                width=row["StintLength"],
                left=previous_stint_end,
                color=fastf1.plotting.COMPOUND_COLORS[row["Compound"]],
                edgecolor="black",
                fill=True
            )

            previous_stint_end += row["StintLength"]

    ax.set_xlabel("Lap")
    ax.set_ylabel("Driver")
    ax.grid(False)
    # invert the y-axis so drivers that finish higher are closer to the top
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_title(f"{session.event['EventName']} {session.event.year} tyre strategies")
    return ax


# Wizualizacja czasów okrążeń danego kierowcy w danej sesji
def driver_lap_times(year, destination, driver, ses):
    fastf1.plotting.setup_mpl(misc_mpl_mods=False)
    race = fastf1.get_session(year, destination, ses)
    race.load()
    driver_laps = race.laps.pick_driver(driver).pick_quicklaps()
    driver_laps = driver_laps.reset_index()
    driver_laps["LapTime"] = driver_laps["LapTime"].dt.total_seconds()
    fig, ax = plt.subplots(figsize=(8, 8))

    sns.scatterplot(data=driver_laps,
                    x="LapNumber",
                    y="LapTime",
                    ax=ax,
                    hue="Compound",
                    palette=fastf1.plotting.COMPOUND_COLORS,
                    s=80,
                    linewidth=0,
                    legend='auto')

    ax.set_xlabel("Lap Number")
    ax.set_ylabel("Lap Time")

    # The y-axis increases from bottom to top by default
    # Since we are plotting time, it makes sense to invert the axis
    # ax.invert_yaxis()
    plt.suptitle(f"{driver} laptimes in the {year} {race.event['EventName']}")

    # Turn on major grid lines
    plt.grid(color='w', which='major', axis='both')
    sns.despine(left=True, bottom=True)

    plt.tight_layout()
    plt.show()


def quali_results_concrete_wall(year, event, ax=None):
    session = fastf1.get_session(year, event, 'Q')

    session.load()

    drivers = pd.unique(session.laps['Driver'])
    list_fastest_laps = list()
    q1, q2, q3 = session.laps.split_qualifying_sessions()
    for drv in drivers:
        drvs_fastest_lap = session.laps.pick_driver(drv).pick_fastest()
        list_fastest_laps.append(drvs_fastest_lap)
    fastest_laps = Laps(list_fastest_laps).sort_values(by='LapTime').reset_index(drop=True)
    pole_lap = fastest_laps.pick_fastest()
    fastest_laps['LapTimeDelta'] = fastest_laps['LapTime'] - pole_lap['LapTime']
    team_colors = list()
    filtered_fastest_laps = fastest_laps.dropna(subset=['Team'])
    #  Odrzucenie z wykresu kierowców którzy stracili więcej niz 5s w celu łaniejszego wykresu
    filtered_fastest_laps = filtered_fastest_laps[filtered_fastest_laps['LapTimeDelta'] < pd.Timedelta(seconds=5)]
    for index, lap in filtered_fastest_laps.iterlaps():
        color = fastf1.plotting.team_color(lap['Team'])
        team_colors.append(color)

    ax.barh(filtered_fastest_laps.index, filtered_fastest_laps['LapTimeDelta'],
            color=team_colors, edgecolor='grey')
    ax.set_yticks(filtered_fastest_laps.index)
    ax.set_yticklabels(filtered_fastest_laps['Driver'])

    # show fastest at the top
    ax.invert_yaxis()

    # draw vertical lines behind the bars
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    lap_time_string = strftimedelta(pole_lap['LapTime'], '%m:%s.%ms')

    ax.set_title(f"{session.session_info['Meeting']['Name']} {year} Qualifying\n"
                 f"Fastest Lap: {lap_time_string} ({pole_lap['Driver']})")
    return ax


def quali_results_concrete(year, event):
    session = fastf1.get_session(year, event, 'Q')
    plt.style.use("cyberpunk")
    session.load()

    drivers = pd.unique(session.laps['Driver'])
    list_fastest_laps = list()
    q1, q2, q3 = session.laps.split_qualifying_sessions()
    for drv in drivers:
        drvs_fastest_lap = session.laps.pick_driver(drv).pick_fastest()
        list_fastest_laps.append(drvs_fastest_lap)
    fastest_laps = Laps(list_fastest_laps).sort_values(by='LapTime').reset_index(drop=True)
    pole_lap = fastest_laps.pick_fastest()
    fastest_laps['LapTimeDelta'] = fastest_laps['LapTime'] - pole_lap['LapTime']
    team_colors = list()
    filtered_fastest_laps = fastest_laps.dropna(subset=['Team'])  # usuwa wszystkie NaT
    #  Odrzucenie z wykresu kierowców którzy stracili więcej niz 5s w celu łaniejszego wykresu
    filtered_fastest_laps = filtered_fastest_laps[filtered_fastest_laps['LapTimeDelta'] < pd.Timedelta(seconds=5)]
    for index, lap in filtered_fastest_laps.iterlaps():
        color = fastf1.plotting.team_color(lap['Team'])
        team_colors.append(color)
    fig, ax = plt.subplots(figsize=(16, 9), dpi=100)
    ax.barh(filtered_fastest_laps.index, filtered_fastest_laps['LapTimeDelta'],
            color=team_colors, edgecolor='grey')
    ax.set_yticks(filtered_fastest_laps.index)
    ax.set_yticklabels(filtered_fastest_laps['Driver'])

    # show fastest at the top
    ax.invert_yaxis()

    # draw vertical lines behind the bars
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    lap_time_string = strftimedelta(pole_lap['LapTime'], '%m:%s.%ms')

    plt.suptitle(f"{session.session_info['Meeting']['Name']} {year} Qualifying\n"
                 f"Fastest Lap: {lap_time_string} ({pole_lap['Driver']})")
    plt.savefig(f'quali_results.png')
    plt.show()


def quali_results():
    event = fastf1.get_event_schedule(2023)
    for x in range(1, 23):
        eventName = event['EventName'][x]
        session = fastf1.get_session(2023, eventName, 'Q')
        fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme=None, misc_mpl_mods=False)
        print(eventName)
        session.load()

        drivers = pd.unique(session.laps['Driver'])
        list_fastest_laps = list()
        q1, q2, q3 = session.laps.split_qualifying_sessions()
        for drv in drivers:
            drvs_fastest_lap = session.laps.pick_driver(drv).pick_fastest()
            list_fastest_laps.append(drvs_fastest_lap)
        fastest_laps = Laps(list_fastest_laps).sort_values(by='LapTime').reset_index(drop=True)
        pole_lap = fastest_laps.pick_fastest()
        fastest_laps['LapTimeDelta'] = fastest_laps['LapTime'] - pole_lap['LapTime']
        team_colors = list()
        filtered_fastest_laps = fastest_laps.dropna(subset=['Team'])
        #  Odrzucenie z wykresu kierowców którzy stracili więcej niz 5s w celu łaniejszego wykresu
        filtered_fastest_laps = filtered_fastest_laps[filtered_fastest_laps['LapTimeDelta'] < pd.Timedelta(seconds=5)]
        for index, lap in filtered_fastest_laps.iterlaps():
            color = fastf1.plotting.team_color(lap['Team'])
            team_colors.append(color)
        fig, ax = plt.subplots(figsize=(16, 9), dpi=100)
        ax.barh(filtered_fastest_laps.index, filtered_fastest_laps['LapTimeDelta'],
                color=team_colors, edgecolor='grey')
        ax.set_yticks(filtered_fastest_laps.index)
        ax.set_yticklabels(filtered_fastest_laps['Driver'])

        # show fastest at the top
        ax.invert_yaxis()

        # draw vertical lines behind the bars
        ax.set_axisbelow(True)
        ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

        lap_time_string = strftimedelta(pole_lap['LapTime'], '%m:%s.%ms')

        plt.suptitle(f"{session.event['EventName']} {session.event.year} Quali\n"
                     f"Fastest Lap: {lap_time_string} ({pole_lap['Driver']})")
        plt.show()


def compare_fastest_lap_visualization_on_map(ses, year, driver1, driver2, identifier, ax=None):
    laps = ses.laps
    laps_driver1 = laps.pick_driver(driver1)
    laps_driver2 = laps.pick_driver(driver2)

    # Get the telemetry data from their fastest lap
    fastest_driver1 = laps_driver1.pick_fastest().get_telemetry().add_distance()
    fastest_driver2 = laps_driver2.pick_fastest().get_telemetry().add_distance()

    # Since the telemetry data does not have a variable that indicates the driver,
    # create that column
    fastest_driver1['Driver'] = driver1
    fastest_driver2['Driver'] = driver2

    # Merge both lap telemetries to one DataFrame
    telemetry = fastest_driver1._append(fastest_driver2)

    num_minisectors = 25

    # Grab the maximum value of distance that is known in the telemetry
    total_distance = max(telemetry['Distance'])

    # Generate equally sized mini-sectors
    minisector_length = total_distance / num_minisectors

    # Initiate minisector variable, with 0 (meters) as a starting point.
    minisectors = [0]

    # Add multiples of minisector_length to the minisectors
    for i in range(0, (num_minisectors - 1)):
        minisectors.append(minisector_length * (i + 1))

    telemetry['Minisector'] = telemetry['Distance'].apply(
        lambda dist: (
            int((dist // minisector_length) + 1)
        )
    )
    # Calculate avg. speed per driver per mini sector
    average_speed = telemetry.groupby(['Minisector', 'Driver'])['Speed'].mean().reset_index()
    # Select the driver with the highest average speed
    fastest_driver = average_speed.loc[average_speed.groupby(['Minisector'])['Speed'].idxmax()]
    # Get rid of the speed column and rename the driver column
    fastest_driver = fastest_driver[['Minisector', 'Driver']].rename(columns={'Driver': 'Fastest_driver'})
    # Join the fastest driver per minisector with the full telemetry
    telemetry = telemetry.merge(fastest_driver, on=['Minisector'])
    # Order the data by distance to make matploblib does not get confused
    telemetry = telemetry.sort_values(by=['Distance'])
    # Convert driver name to integer
    telemetry.loc[telemetry['Fastest_driver'] == driver1, 'Fastest_driver_int'] = 1
    telemetry.loc[telemetry['Fastest_driver'] == driver2, 'Fastest_driver_int'] = 2
    x = np.array(telemetry['X'].values)
    y = np.array(telemetry['Y'].values)
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    fastest_driver_array = telemetry['Fastest_driver_int'].to_numpy().astype(float)
    cmap = cm.get_cmap('winter', 2)

    # Get the custom color for a specific team
    team_color1 = fastf1.plotting.driver_color(driver1)
    print(team_color1)
    team_color2 = fastf1.plotting.team_color(ses.laps.pick_driver(driver2).pick_fastest()['Team'])

    # Replace the color for the team in the colormap
    team_index = 0
    cmap_colors = cmap(np.arange(cmap.N))
    cmap_colors[team_index] = to_rgba(team_color1)
    cmap_colors[1] = to_rgba(team_color2)

    # Create a new colormap with the modified colors
    custom_cmap = cm.colors.ListedColormap(cmap_colors, name='custom_winter', N=cmap.N)

    # Create a LineCollection with the custom colormap
    lc_comp = LineCollection(segments, norm=plt.Normalize(1, custom_cmap.N + 1), cmap=custom_cmap)

    lc_comp.set_array(fastest_driver_array)
    lc_comp.set_linewidth(5)

    plt.rcParams['figure.figsize'] = [18, 10]

    ax.add_collection(lc_comp)
    ax.axis('equal')
    ax.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

    cbar = plt.colorbar(mappable=lc_comp, boundaries=np.arange(1, 4))
    cbar.set_ticks(np.arange(1.5, 3.5))
    cbar.set_ticklabels([driver1, driver2])
    ax.set_title(f"{ses.session_info['Meeting']['Name']} {year} {identifier}\n"
              f"Comparision {driver1} with {driver2}")
    return ax


def wall_of_plots(year, event_name, driver_1, driver_2, ses):
    quali = ff1.get_session(year, event_name, ses)
    quali.load()

    # Laps can now be accessed through the .laps object coming from the session
    if quali.name == "Qualifying":
        q1, q2, q3 = quali.laps.split_qualifying_sessions()
        laps_driver_1 = q3.pick_driver(driver_1)
        laps_driver_2 = q3.pick_driver(driver_2)
    else:
        laps_driver_1 = quali.laps.pick_driver(driver_1)
        laps_driver_2 = quali.laps.pick_driver(driver_2)

    # Select the fastest lap
    fastest_driver_1 = laps_driver_1.pick_fastest()
    fastest_driver_2 = laps_driver_2.pick_fastest()

    # Retrieve the telemetry and add the distance column
    telemetry_driver_1 = fastest_driver_1.get_telemetry().add_distance()
    telemetry_driver_2 = fastest_driver_2.get_telemetry().add_distance()

    # Make sure whe know the team name for coloring
    team_driver_1 = fastest_driver_1['Team']
    team_driver_2 = fastest_driver_2['Team']
    delta_time, ref_tel, compare_tel = utils.delta_time(fastest_driver_1, fastest_driver_2, )
    plt.style.use("cyberpunk")
    plot_size = [20, 100]
    plot_title = f"{quali.event.year} {quali.event.EventName} - {quali.name} - {driver_1} VS {driver_2}"
    plot_ratios = [3, 3, 3, 3, 3, 3, 3, 5, 4, 4, 4, 4, 4]
    plot_filename = "wersja_cyberpunkowa"
    # Make plot a bit bigger
    plt.rcParams['figure.figsize'] = plot_size
    # Create subplots with different sizes
    fig, ax = plt.subplots(13, gridspec_kw={'height_ratios': plot_ratios})
    # corners
    circuit_info = quali.get_circuit_info()
    ax[0].vlines(x=circuit_info.corners['Distance'], ymin=-0.3, ymax=max(delta_time),
                 linestyles='dotted', colors='grey')
    for _, corner in circuit_info.corners.iterrows():
        txt = f"{corner['Number']}{corner['Letter']}"
        ax[0].text(corner['Distance'], -0.3, txt,
                   va='center_baseline', ha='center', size='small')
    # Set the plot title
    ax[0].title.set_text(plot_title)
    # Delta line
    # change plot colour to yellow
    ax[0].plot(ref_tel['Distance'], delta_time, label=driver_1, color=ff1.plotting.team_color(team_driver_1))
    ax[0].plot(ref_tel['Distance'], delta_time)
    ax[0].axhline(0, color='white')
    ax[0].set(ylabel=f"Gap to {driver_1} (s)")
    ax[0].set(xlabel='Lap distance (meters)')
    # Speed trace
    ax[1].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Speed'], label=driver_1,
               color=ff1.plotting.team_color(team_driver_1))
    ax[1].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Speed'], label=driver_2,
               color=ff1.plotting.team_color(team_driver_2))
    ax[1].set(ylabel='Speed (km/h)')
    ax[1].legend(loc="lower right")
    ax[1].set(xlabel='Lap distance (meters)')

    # Throttle trace
    ax[2].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Throttle'], label=driver_1,
               color=ff1.plotting.team_color(team_driver_1))
    ax[2].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Throttle'], label=driver_2,
               color=ff1.plotting.team_color(team_driver_2))
    ax[2].set(ylabel='Throttle (%)')
    ax[2].set(xlabel='Lap distance (meters)')

    # Brake trace
    ax[3].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Brake'], label=driver_1,
               color=ff1.plotting.team_color(team_driver_1))
    ax[3].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Brake'], label=driver_2,
               color=ff1.plotting.team_color(team_driver_2))
    ax[3].set(ylabel='Brake')
    ax[3].set(xlabel='Lap distance (meters)')

    # Gear trace
    ax[4].plot(telemetry_driver_1['Distance'], telemetry_driver_1['nGear'], label=driver_1,
               color=ff1.plotting.team_color(team_driver_1))
    ax[4].plot(telemetry_driver_2['Distance'], telemetry_driver_2['nGear'], label=driver_2,
               color=ff1.plotting.team_color(team_driver_2))
    ax[4].set(ylabel='Gear')
    ax[4].set(xlabel='Lap distance (meters)')

    # RPM trace
    ax[5].plot(telemetry_driver_1['Distance'], telemetry_driver_1['RPM'], label=driver_1,
               color=ff1.plotting.team_color(team_driver_1))
    ax[5].plot(telemetry_driver_2['Distance'], telemetry_driver_2['RPM'], label=driver_2,
               color=ff1.plotting.team_color(team_driver_2))
    ax[5].set(ylabel='RPM')
    ax[5].set(xlabel='Lap distance (meters)')

    # DRS trace
    ax[6].plot(telemetry_driver_1['Distance'], telemetry_driver_1['DRS'], label=driver_1,
               color=ff1.plotting.team_color(team_driver_1))
    ax[6].plot(telemetry_driver_2['Distance'], telemetry_driver_2['DRS'], label=driver_2,
               color=ff1.plotting.team_color(team_driver_2))
    ax[6].set(ylabel='DRS')
    ax[6].set(xlabel='Lap distance (meters)')

    # space between plots
    plt.subplots_adjust(hspace=0.3)

    # ax[7] = quali_results_concrete_wall(2023, "Bahrain", ax=ax[7])
    # ax[8] = compare_fastest_lap_visualization_on_map(quali, year, driver_1, driver_2, ses, ax=ax[8])
    # tyre_strategies_wall(quali, ax=ax[7])
    # driver_laptimes_visualization_wall(2023, "Bahrain", ax=ax[9])
    # team_pace_comparison_wall(quali, ax=ax[7])
    # get_0_x_times_wall(quali, 100, ax=ax[12])
    # visualization_of_position_changes_during_the_race_wall(quali, ax=ax[9])
    # get_gained_positions_in_full_race_wall(quali, ax=ax[10])
    # get_gained_positions_on_first_lap_wall(quali, ax=ax[11])
    # Store figure
    plt.savefig(plot_filename, dpi=300)

    plt.show()


if __name__ == '__main__':
    wall_of_plots(2024, "Monaco", "VER", "LEC", "R")
