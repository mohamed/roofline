#!/usr/bin/env python3

"""
This is a simple script to compute the Roofline Model
(https://en.wikipedia.org/wiki/Roofline_model) of given HW platforms
running given apps

Peak performance must be specified in GFLOP/s
Peak bandwidth must be specified in GB/s
Arithemtic intensity is specified in FLOP/byte
Performance is specified in GFLOP/s

Copyright 2018-2024, Mohamed A. Bamakhrama
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

    achievable_perf = numpy.zeros((num_platforms, len(intensity)))
    for i in range(num_platforms):
        achievable_perf[i:] = numpy.minimum(peak_performance[i],
                                            peak_bandwidth[i] * intensity)
    return achievable_perf


def process(hw_platforms, apps, xkcd):
    """
    Processes the hw_platforms and apps to plot the Roofline.
    """
    assert isinstance(hw_platforms, list)
    assert isinstance(apps, list)
    assert isinstance(xkcd, bool)

    # arithmetic intensity
    arithmetic_intensity = numpy.logspace(START, STOP, num=N, base=2)

    # Compute the rooflines
    achv_perf = roofline(len(hw_platforms),
                         numpy.array([float(p[1]) for p in hw_platforms]),
                         numpy.array([float(p[2]) for p in hw_platforms]),
                         arithmetic_intensity)
    norm_achv_perf = roofline(len(hw_platforms),
                              numpy.array([(float(p[1])*1e3) / float(p[3])
                                           for p in hw_platforms]),
                              numpy.array([(float(p[2])*1e3) / float(p[3])
                                           for p in hw_platforms]),
                              arithmetic_intensity)

    # Apps
    if apps != []:
        apps_intensity = numpy.array([float(a[1]) for a in apps])

    # Plot the graphs
    if xkcd:
        matplotlib.pyplot.xkcd()
    fig, axes = matplotlib.pyplot.subplots(1, 2)
    for axis in axes:
        axis.set_xscale('log', base=2)
        axis.set_yscale('log', base=2)
        axis.set_xlabel('Arithmetic Intensity (FLOP/byte)', fontsize=12)
        axis.grid(True, which='major')

    matplotlib.pyplot.setp(axes, xticks=arithmetic_intensity,
                           yticks=numpy.logspace(-5, 20, num=26, base=2))

    axes[0].set_ylabel("Achieveable Performance (GFLOP/s)", fontsize=12)
    axes[1].set_ylabel("Normalized Achieveable Performance (MFLOP/s/$)",
                       fontsize=12)

    axes[0].set_title('Roofline Model', fontsize=14)
    axes[1].set_title('Normalized Roofline Model', fontsize=14)

    for idx, val in enumerate(hw_platforms):
        axes[0].plot(arithmetic_intensity, achv_perf[idx, 0:],
                     label=val[0], marker='o')
        axes[1].plot(arithmetic_intensity, norm_achv_perf[idx, 0:],
                     label=val[0], marker='o')

    if apps != []:
        color = matplotlib.pyplot.cm.rainbow(numpy.linspace(0, 1, len(apps)))
        for idx, val in enumerate(apps):
            for axis in axes:
                axis.axvline(apps_intensity[idx], label=val[0],
                             linestyle=':', color=color[idx])
                if len(val) > 2:
                    assert len(val) % 2 == 0
                    for cnt in range(2, len(val), 2):
                        pair = [apps_intensity[idx], float(val[cnt+1])]
                        axis.plot(pair[0], pair[1], 'rx')
                        axis.annotate(val[cnt], xy=(pair[0], pair[1]),
                                      textcoords='data')

    for axis in axes:
        axis.legend()
    fig.tight_layout()
    matplotlib.pyplot.show()


def read_file(filename, row_len, csv_name, allow_variable_rows=False):
    """
    Reads CSV file and returns a list of row_len-ary tuples
    """
    assert isinstance(row_len, int)
    elements = []
    try:
        fname = filename if filename is not None else sys.stdin
        with open(fname, 'r', encoding='utf-8') as in_file:
            reader = csv.reader(in_file, dialect='excel')
            for row in reader:
                if not row[0].startswith('#'):
                    if not allow_variable_rows:
                        if len(row) != row_len:
                            print(f"Error: Each row in {csv_name} must be "
                                  f"contain exactly {row_len} entries!",
                                  file=sys.stderr)
                            sys.exit(1)
                        else:
                            assert len(row) >= row_len
                    element = tuple([row[0]] + row[1:])
                    elements.append(element)
    except IOError as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
    return elements


def main():
    """
    main function
    """
    hw_platforms = []
    apps = []
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar="hw_csv",
                        help="HW platforms CSV file", type=str)
    parser.add_argument("-a", metavar="apps_csv",
                        help="applications CSV file", type=str)
    parser.add_argument("--xkcd", action='store_true', default=False)

    args = parser.parse_args()
    # HW
    print("Reading HW characteristics...")
    hw_platforms = read_file(args.i, 4, "HW CSV")
    # apps
    if args.a is None:
        print("No application file given...")
    else:
        print("Reading applications parameters...")
        apps = read_file(args.a, 2, "SW CSV", True)

    print(hw_platforms)
    print(f"Plotting using XKCD plot style is set to {args.xkcd}")
    if apps:
        print(apps)
    process(hw_platforms, apps, args.xkcd)
    sys.exit(0)


if __name__ == "__main__":
    main()
