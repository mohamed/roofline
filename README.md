Roofline.py
===========

This is a simple script to plot the [Roofline model](https://dl.acm.org/citation.cfm?id=1498785) of
given HW platforms and given applications.
The script can take its input from:
1. `stdin`: In this case, it reads first the HW characteristics followed by a `EOF`.
   Then, you will be prompted to enter the applications' intensities followed by an `EOF`.
2. files: In this case, it reads two comma-separated values (CSV) files; one for HW and the other
   for the applications.

Requirements
------------
You need:
* Python 3.6 or higher with: `numpy` and `matplotlib`


License
-------
BSD license shown in LICENSE
