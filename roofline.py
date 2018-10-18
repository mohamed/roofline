#!/usr/bin/env python3

"""
This is a simple script to compute the Roofline Model
(https://en.wikipedia.org/wiki/Roofline_model) of given HW platforms
running given apps

Peak bandwidth must be specified in GB/s
Peak performance must be specified in GFLOP/s
Arithemtic intensity is specified in FLOP/byte
Performance is specified in GFLOP/s

Copyright 2018, Mohamed A. Bamakhrama
Licensed under BSD license shown in LICENSE
"""


import csv
import sys
import argparse
import numpy
import matplotlib.pyplot
import matplotlib
matplotlib.rc('font', family='Arial')


# Constants
# The following constants define the span of the intensity axis
START = -4
STOP = 6
N = abs(STOP - START + 1)


def roofline(num_platforms, peak_performance, peak_bandwidth, intensity):
    """
    Computes the roofline model for the given platforms.
    Returns The achievable performance
    """

    assert isinstance(num_platforms, int) and num_platforms > 0
    assert isinstance(peak_performance, numpy.ndarray)
    assert isinstance(peak_bandwidth, numpy.ndarray)
    assert isinstance(intensity, numpy.ndarray)
    assert num_platforms == peak_performance.shape[0] \
            and num_platforms == peak_bandwidth.shape[0]

    achievable_performance = numpy.zeros((num_platforms, len(intensity)))
    for i in range(num_platforms):
        achievable_performance[i:] = numpy.minimum(peak_performance[i],
                                                   peak_bandwidth[i] * intensity)
    return achievable_performance


def process(hw_platforms, sw_apps, normalize=False):
    """
    Processes the hw_platforms and sw_apps to plot the Roofline.
    """
    assert isinstance(hw_platforms, list)
    assert isinstance(sw_apps, list)

    # arithmetic intensity
    arithmetic_intensity = numpy.logspace(START, STOP, num=N, base=2)
    # Hardware platforms
    platforms = [p[0] for p in hw_platforms]
    peak_performance = [(p[1] * 1e3) / p[3] if normalize else p[1] for p in hw_platforms]
    peak_bandwidth = [(p[2] * 1e3) / p[3] if normalize else p[2] for p in hw_platforms]
    peak_performance = numpy.array(peak_performance)
    peak_bandwidth = numpy.array(peak_bandwidth)
    # Compute the rooflines
    achievable_performance = roofline(len(platforms), peak_performance,
                                      peak_bandwidth, arithmetic_intensity)

    # Apps
    apps = [a[0] for a in sw_apps]
    apps_intensity = [a[1] for a in sw_apps]
    apps_intensity = numpy.array(apps_intensity)

    # Plot the graphs
    _, axis = matplotlib.pyplot.subplots()
    axis.set_xscale('log', basex=2)
    axis.set_yscale('log', basey=2)
    matplotlib.pyplot.xticks(arithmetic_intensity)
    matplotlib.pyplot.yticks(numpy.logspace(1, 20, num=20, base=2))

    axis.set_xlabel('Arithmetic Intensity (FLOP/byte)', fontsize=12)
    if normalize:
        axis.set_ylabel("Normalized Achieveable Performance (MFLOP/s/$)", fontsize=12)
    else:
        axis.set_ylabel("Achieveable Performance (GFLOP/s)", fontsize=12)
    axis.set_title('Roofline Model', fontsize=14)
    for idx, val in enumerate(platforms):
        axis.plot(arithmetic_intensity, achievable_performance[idx, 0:],
                  label=val, marker='o')
        axis.legend()

    color = matplotlib.pyplot.cm.rainbow(numpy.linspace(0, 1, len(apps)))
    for idx, val in enumerate(apps):
        matplotlib.pyplot.axvline(apps_intensity[idx], label=val,
                                  linestyle='-.', marker='x', color=color[idx])
        axis.legend()

    matplotlib.pyplot.grid(True, which='major')
    matplotlib.pyplot.show()


def main():
    """
    main function
    """
    hw_platforms = list()
    apps = list()
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar="hw_csv", help="HW platforms CSV file", type=str)
    parser.add_argument("-a", metavar="apps_csv", help="applications CSV file", type=str)
    parser.add_argument("-n", help="normalize performance by price", action="store_true",
                        default=False)
    args = parser.parse_args()
    # HW
    print("Reading HW characteristics...")
    try:
        hw_in_file = open(args.i, 'r') if args.i is not None else sys.stdin
        reader = csv.reader(hw_in_file, dialect='excel')
        for row in reader:
            if len(row) != 4:
                print("Error: Each row in HW CSV must be contain exactly four entries!",
                      file=sys.stderr)
                sys.exit(1)
            platform = tuple([row[0], float(row[1]), float(row[2]), float(row[3])])
            hw_platforms.append(platform)
        if args.i is not None:
            hw_in_file.close()
    except IOError as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
    # apps
    print("Reading applications intensities...")
    try:
        apps_in_file = open(args.a, 'r') if args.a is not None else sys.stdin
        reader = csv.reader(apps_in_file, dialect='excel')
        for row in reader:
            if len(row) != 2:
                print("Error: Each row in apps CSV must be contain exactly two entries!",
                      file=sys.stderr)
                sys.exit(1)
            app = tuple([row[0], float(row[1])])
            apps.append(app)
        if args.a is not None:
            apps_in_file.close()
    except IOError as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
    print(hw_platforms)
    print(apps)
    process(hw_platforms, apps, args.n)
    sys.exit(0)


if __name__ == "__main__":
    main()
