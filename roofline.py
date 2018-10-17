#!/usr/bin/env python3

# This is a simple script to compute the Roofline Model
# (https://en.wikipedia.org/wiki/Roofline_model) of given HW platforms
# running given apps
#
# Peak bandwidth must be specified in GB/s
# Peak performance must be specified in GFLOP/s
# Arithemtic intensity is specified in FLOP/byte
# Performance is specified in GFLOP/s
#
# Copyright 2018, Mohamed A. Bamakhrama
# Licensed under BSD license shown in LICENSE


import csv
import sys
import math
import numpy
import argparse
import matplotlib
matplotlib.rc('font',family='Arial')
import matplotlib.pyplot


# Constants
# The following constants define the span of the intensity axis
start = -4
stop = 6
N = abs(stop - start + 1)


def roofline(num_platforms, peak_performance, peak_bandwidth, intensity):
    assert isinstance(num_platforms, int) and num_platforms > 0
    assert isinstance(peak_performance, numpy.ndarray)
    assert isinstance(peak_bandwidth, numpy.ndarray)
    assert isinstance(intensity, numpy.ndarray)
    assert num_platforms == peak_performance.shape[0] and num_platforms == peak_bandwidth.shape[0]

    achievable_performance = numpy.zeros((num_platforms, len(intensity)))
    for i in range(num_platforms):
        achievable_performance[i:] = numpy.minimum(peak_performance[i], peak_bandwidth[i] * intensity)
    return achievable_performance


def process(hw_platforms, sw_apps):
    assert isinstance(hw_platforms, list)
    assert isinstance(sw_apps, list)

    # arithmetic intensity
    arithmetic_intensity =  numpy.logspace(start, stop, num=N, base=2)
    # Hardware platforms
    platforms = list()
    peak_performance = list()
    peak_bandwidth = list()
    for platform in hw_platforms:
        assert isinstance(platform, tuple)
        assert len(platform) == 3
        platforms.append(platform[0])
        peak_performance.append(platform[1])
        peak_bandwidth.append(platform[2])
    peak_performance = numpy.array(peak_performance)
    peak_bandwidth   = numpy.array(peak_bandwidth)
    # Compute the rooflines
    achievable_performance = roofline(len(platforms), peak_performance, peak_bandwidth, arithmetic_intensity)

    # Apps
    apps = list()
    apps_intensity = list()
    for app in sw_apps:
        apps.append(app[0])
        apps_intensity.append(app[1])
    apps_intensity = numpy.array(apps_intensity);
    apps_performance = roofline(len(platforms), peak_performance, peak_bandwidth, apps_intensity)

    # Plot the graphs
    fig, ax = matplotlib.pyplot.subplots()
    ax.set_xscale('log', basex=2)
    ax.set_yscale('log', basey=2)
    matplotlib.pyplot.xticks(arithmetic_intensity)
    matplotlib.pyplot.yticks(numpy.logspace(1, 20, num=20, base=2))

    ax.set_xlabel('Arithmetic Intensity (FLOP/byte)',  fontsize=12)
    ax.set_ylabel('Achieveable Performance (GFLOP/s)', fontsize=12)
    ax.set_title('Roofline Model', fontsize=14)
    for i in range(len(platforms)):
        ax.plot(arithmetic_intensity, achievable_performance[i,0:], label=platforms[i], marker='o')
        ax.legend()

    color = matplotlib.pyplot.cm.rainbow(numpy.linspace(0,1,len(apps)))
    for i in range(len(apps)):
        matplotlib.pyplot.axvline(apps_intensity[i], label=apps[i], linestyle='-.', marker='x', color=color[i])
        ax.legend()

    matplotlib.pyplot.grid(True, which='major')
    matplotlib.pyplot.show()


def main():
    hw_platforms = list()
    apps = list()
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar="hw_csv", help="HW platforms CSV file", type=str)
    parser.add_argument("-a", metavar="apps_csv", help="applications CSV file", type=str)
    args = parser.parse_args()
    # HW
    print("Reading HW characteristics...")
    try:
        hw_in_file = open(args.i, 'r') if args.i != None else sys.stdin
        reader = csv.reader(hw_in_file, dialect='excel')
        for row in reader:
            if len(row) != 3:
                print("Error: Each row in HW CSV must be contain exactly three entries!", file=sys.stderr)
                sys.exit(1)
            platform = tuple([row[0], float(row[1]), float(row[2])])
            hw_platforms.append(platform)
        if args.i != None:
            hw_in_file.close()
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    # apps
    print("Reading applications intensities...")
    try:
        apps_in_file = open(args.a, 'r') if args.a != None else sys.stdin
        reader = csv.reader(apps_in_file, dialect='excel')
        for row in reader:
            if len(row) != 2:
                print("Error: Each row in apps CSV must be contain exactly two entries!", file=sys.stderr)
                sys.exit(1)
            app = tuple([row[0], float(row[1])])
            apps.append(app)
        if args.a != None:
            apps_in_file.close()        
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    print(hw_platforms)
    print(apps)
    process(hw_platforms, apps)
    sys.exit(0)


if __name__ == "__main__":
    main()
