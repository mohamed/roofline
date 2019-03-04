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
    assert (num_platforms == peak_performance.shape[0] and
            num_platforms == peak_bandwidth.shape[0])

    achievable_performance = numpy.zeros((num_platforms, len(intensity)))
    for i in range(num_platforms):
        achievable_performance[i:] = numpy.minimum(peak_performance[i],
                                                   peak_bandwidth[i] * intensity)
    return achievable_performance


def process(hw_platforms, sw_apps, xkcd):
    """
    Processes the hw_platforms and sw_apps to plot the Roofline.
    """
    assert isinstance(hw_platforms, list)
    assert isinstance(sw_apps, list)
    assert isinstance(xkcd, bool)

    # arithmetic intensity
    arithmetic_intensity = numpy.logspace(START, STOP, num=N, base=2)
    # Hardware platforms
    platforms = [p[0] for p in hw_platforms]

    # Compute the rooflines
    achievable_performance = roofline(len(platforms),
                                      numpy.array([p[1] for p in hw_platforms]),
                                      numpy.array([p[2] for p in hw_platforms]),
                                      arithmetic_intensity)
    norm_achievable_performance = roofline(len(platforms),
                                           numpy.array([(p[1] * 1e3) / p[3]
                                                        for p in hw_platforms]),
                                           numpy.array([(p[2] * 1e3) / p[3]
                                                        for p in hw_platforms]),
                                           arithmetic_intensity)

    # Apps
    if sw_apps != []:
        apps = [a[0] for a in sw_apps]
        apps_intensity = numpy.array([a[1] for a in sw_apps])

    # Plot the graphs
    if xkcd:
        matplotlib.pyplot.xkcd()
    fig, axes = matplotlib.pyplot.subplots(1, 2)
    for axis in axes:
        axis.set_xscale('log', basex=2)
        axis.set_yscale('log', basey=2)
        axis.set_xlabel('Arithmetic Intensity (FLOP/byte)', fontsize=12)
        axis.grid(True, which='major')

    matplotlib.pyplot.setp(axes, xticks=arithmetic_intensity,
                           yticks=numpy.logspace(1, 20, num=20, base=2))

    axes[0].set_ylabel("Achieveable Performance (GFLOP/s)", fontsize=12)
    axes[1].set_ylabel("Normalized Achieveable Performance (MFLOP/s/$)", fontsize=12)

    axes[0].set_title('Roofline Model', fontsize=14)
    axes[1].set_title('Normalized Roofline Model', fontsize=14)

    for idx, val in enumerate(platforms):
        axes[0].plot(arithmetic_intensity, achievable_performance[idx, 0:],
                     label=val, marker='o')
        axes[1].plot(arithmetic_intensity, norm_achievable_performance[idx, 0:],
                     label=val, marker='o')

    if sw_apps != []:
        color = matplotlib.pyplot.cm.rainbow(numpy.linspace(0, 1, len(apps)))
        for idx, val in enumerate(apps):
            for axis in axes:
                axis.axvline(apps_intensity[idx], label=val,
                             linestyle='-.', marker='x', color=color[idx])

    for axis in axes:
        axis.legend()
    fig.tight_layout()
    matplotlib.pyplot.show()


def read_file(filename, row_len, csv_name):
    """
    Reads CSV file and returns a list of row_len-ary tuples
    """
    assert isinstance(row_len, int)
    elements = list()
    try:
        in_file = open(filename, 'r') if filename is not None else sys.stdin
        reader = csv.reader(in_file, dialect='excel')
        for row in reader:
            if len(row) != row_len:
                print("Error: Each row in %s must be contain exactly %d entries!"
                      % (csv_name, row_len), file=sys.stderr)
                sys.exit(1)
            element = tuple([row[0]] + [float(r) for r in row[1:]])
            elements.append(element)
        if filename is not None:
            in_file.close()
    except IOError as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
    return elements


def main():
    """
    main function
    """
    hw_platforms = list()
    apps = list()
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar="hw_csv", help="HW platforms CSV file", type=str)
    parser.add_argument("-a", metavar="apps_csv", help="applications CSV file", type=str)
    parser.add_argument("--hw-only", action='store_true', default=False)
    parser.add_argument("--xkcd", action='store_true', default=False)

    args = parser.parse_args()
    # HW
    print("Reading HW characteristics...")
    hw_platforms = read_file(args.i, 4, "HW CSV")
    # apps
    if args.hw_only:
        print("Plotting only HW characteristics without any applications...")
        apps = list()
    else:
        print("Reading applications intensities...")
        apps = read_file(args.a, 2, "SW CSV")

    print(hw_platforms)
    print("Plotting using XKCD plot style is set to %s" % (args.xkcd))
    if apps != []:
        print(apps)
    process(hw_platforms, apps, args.xkcd)
    sys.exit(0)


if __name__ == "__main__":
    main()
