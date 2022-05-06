# lmpy Randomization Submodule

The lmpy randomization submodule includes tools for randomizing Presence-Absence
Matrices in a fashion that retains marginal totals (the same number of presences are
present in each column and row after randomization that were there before
randomization).  We include an implementation of the [Gotelli Swap](./swap.py) method
as well as our own [Grady randomization method](./grady.py) that is designed to operate
at significantly larger scales.