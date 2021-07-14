=================================
PAM Randomization and Null Models
=================================

Introduction
============
Researchers and users generally want to explore various indices that can be
derived from presence-absence matrices (PAMs).  These indices may be based on
sites or species and can utilize additional data structures, such as
phylogenetic trees.  Many times, only the value of these indices calculated
from observed datasets is generated, or at least reported.  Generally,
researchers would prefer to compute the statistical significance of these
metrics and this can be done by generating a null model by randomizing the
observed PAM many times and computing the same indices on the generated
randomizations to create a distribution of values and then the value generated
from the observed data can be evaluated against this distribution.

Again, to generate these null models, the observed PAMs must be randomized.
There are multiple ways to accomplish that task and so one must decide how to
perform the randomizations.  This usually involves deciding on a set of
properties to maintain when randomizing the data, which may include maintaining
row and / or column totals
`(Gotelli 2000) <https://esajournals.onlinelibrary.wiley.com/doi/abs/10.1890/0012-9658(2000)081%5B2606:NMAOSC%5D2.0.CO%3B2>`_.
For Lifemapper randomizations, we maintain row and column totals, meaning that
for each site (row) the number of species present at that site does not change
in the randomizations.  We also maintain the same number of sites present for
each species (column).  These randomization properties limit the number of
possible methods for generating our randomizations and the methods that do meet
that criteria are often computationally complex.  Each of the methods that
Lifemapper exposes is described below.

Randomization algorithms
========================
Swap
----
The swap method, or Gotelli swap as it is sometimes called, looks for row and
column combinations that have diagonal or anti-diagonal patterns of zeros and
ones like
`(Gotelli & Ensminger 2001) <https://link.springer.com/article/10.1007/s004420100717>`_:

::

    0, 1   or   1, 0
    1, 0        0, 1

Once one of these patterns is found, it is "swapped" so zeros become ones and
ones become zeros.  This changes the values in the cells in question but
maintains the totals for the rows and columns.  This process is repeated some
number of times and then the new randomized matrix is returned at that point,
and that method is called "Independent Swap".  Alternatively, "Sequential Swap"
performs a "burn-in" number of swaps and then returns a randomized matrix every
X number of swaps after that.  These methods have been studied by multiple
researchers and have been shown to be biased if the number of iterations is not
chosen carefully.  Unfortunately, to overcome potential bias, the number of
swaps performed must be increased and this increase can greatly increase the
running time of the algorithm.  However, we provide an implementation of this
algorithm for use and study because it is so commonly used.

::

    >>> NUM_SWAPS = 50000
    >>> rand_pam = swap_randomize(my_pam, NUM_SWAPS)

Trial Swap
----------
The Trial Swap method is very similar to the regular swap method, with the
primary difference being the iteration control method.  Where swap counts the
number of swaps performed, trial swap counts the number of row and column
searches.  Eigenvector analysis shows that this helps to overcome the bias in
the swap approach.  The number of trials required to achieve adequate
perturbation of the matrix can be large and causes this method to require too
much time to run for larger input matrices.  We provide this method because it
is also commonly used in other tools and by researchers.

::

    >>> NUM_TRIALS = my_pam.size
    >>> rand_pam = trial_swap(my_pam, num_trials=NUM_TRIALS)

Grady's Heuristic Fill
----------------------
Lifemapper is designed to operate on very large PAMs, far larger than those
possible with any other software that we know of.  We have found in testing
that other PAM randomization methods are far too slow to operate on these large
PAMs, if they can even operate at all at these data scales.  In response to
this issue, we have created our own algorithm for randomizing PAMs while
maintaining row and column marginal totals (Grady in prep).  Our algorithm
utilizes a heuristic to create an approximation of a valid randomization which
is then corrected so that the marginal totals are maintained.  This approach
provides multiple benefits when creating randomizations.  First, the
flexibility afforded by allowing the heuristic to generate an invalid result
allows us to operate on each matrix cell independently, and therefore allows us
to create heuristics that utilize parallelization, resulting in faster running
times, a reduced memory footprint, and better utilization of modern compute
resources.  Next, our algorithm is open source and easily pluggable, so new
heuristics can be developed by the larger community and easily incorporated.
Third, the design of the algorithm does not require anything other than the
marginal totals to be known about the observed matrix which eliminates bias
that it may cause.  It should be noted that the reduced memory footprint of
this algorithm, independence from the observed PAM, and utilization of parallel
compute resources not only speed up individual runs of the algorithm but allow
for multiple instances of the algorithm to run concurrently on a single
machine, further reducing the time required to create a null model.

The choice of heuristic approximation function can have a significant impact on
our algorithm.  It is possible to create bias in the algorithm with a poorly
chosen heuristic.  For example, a heuristic that just returns the observed PAM
or a subset of possible randomizations, would be a poor choice for a heuristic.
It is also possible to create heuristics that require a large amount of memory
or compute resources, or that require a large amount of time to run.  Care
should be taken when creating and selecting heuristics and there may not be a
common selection that always produces unbiased results in the shortest amount
of time.

::

    >>> rand_pam = grady_randomize(my_pam, approximation_heuristic=total_fill_percentage_heuristic)

Strona's Curveball Method
-------------------------
Another method of note is the "curve ball" method presented by
`Strona et al. (2014) <https://www.nature.com/articles/ncomms5114>`_.  This
method uses pair extractions to perform several swaps at once between a pair of
rows or columns.  Python code for this method is available with the
supplementary materials for their paper.  This method can be quite fast for
small to medium sized PAMs but is generally an order of magnitude slower than
the Grady Heuristic method.  The memory footprint of the curveball method is
somewhat less sustainable as matrix sizes grow as well.  At this time we do not
provide an implementation of this approach because we have just used the
published implementation for testing and not our own version.  Please contact
us if you wish to use this method and we would be happy to help you get
started.

----

Generating a null model
=======================
There are a couple of ways to organize computations to generate a null model.
Lifemapper utilizes a workflow management system called Makeflow to manage
dependent computations and spread them across computational units in a cluster.
This example will show you how to create a null model on a single machine and
with a single Python process.  This example will avoid writing out each
randomized matrix as they can quickly require a large amount of disk space.  It
is fairly easy to utilize Python multi-processing to utilize multiple CPU cores
on a single machine but we will keep this example as simple as possible.  For
this null model, we'll assume that the "calculate_c_score" function exists.  We
will use the
`RunningStats <../autoapi/lmpy/statistics/running_stats/index.html#lmpy.statistics.running_stats.RunningStats>`_
class to keep track of mean, standard deviation, and p-values for our null
model.  Note that the RunningStats class can handle either single values or
Matrix objects for each index calculated.

::

    >>> NUM_ITERATIONS = 10000
    >>> observed_c_score = calculate_c_score(observed_pam)
    >>> rs = RunningStats(observed=observed_c_score)
    >>> for i in range(NUM_ITERATIONS):
    ...     rand_pam = grady_randomize(observed_pam)
    ...     rs.push(calculate_c_score(rand_pam))
    >>> print('Mean C-score: {}'.format(rs.mean))
    >>> print('Standard deviation: {}'.format(rs.standard_deviation))
    >>> print('P-value: {}'.format(rs.p_values))

----

References
==========
* Grady (in preparation). A parallel, heuristic-based fill method for creating presence-absence matrix randomizations.
* `Gotelli, N. J. (2000). Null model analysis of species co‐occurrence patterns. Ecology, 81(9), 2606-2621. <https://esajournals.onlinelibrary.wiley.com/doi/abs/10.1890/0012-9658(2000)081%5B2606:NMAOSC%5D2.0.CO%3B2>`_
* `Gotelli, N. J., & Entsminger, G. L. (2001). Swap and fill algorithms in null model analysis: rethinking the knight's tour. Oecologia, 129(2), 281-291. <https://link.springer.com/article/10.1007/s004420100717>`_
* `Strona, G., Nappo, D., Boccacci, F., Fattorini, S., & San-Miguel-Ayanz, J. (2014). A fast and unbiased procedure to randomize ecological binary matrices with fixed row and column totals. Nature communications, 5, 4114. <https://www.nature.com/articles/ncomms5114>`_
