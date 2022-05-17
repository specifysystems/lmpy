# lmpy.randomize Submodule

The lmpy randomization submodule includes tools for randomizing Presence-Absence
Matrices in a fashion that retains marginal totals (the same number of presences are
present in each column and row after randomization that were there before
randomization).  We include an implementation of the [Gotelli Swap](./swap.py) method
as well as our own [Grady randomization method](./grady.py) that is designed to operate
at significantly larger scales.

Matrix randomization is necessary in order to measure the difference between the
statistics of
a matrix computed directly from research data against the statistics of a randomized
version of that matrix.  The randomized matrix is created to have the same properties,
such as size, values, row and column totals.  The difference between these statistics
determines the statistical significance of the results.
