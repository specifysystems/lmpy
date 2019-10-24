==================
Running Statistics
==================

Introduction
============
The running_stats module allows you to keep a running track of calculated
statistics as they are produced rather than summarize, potentially many,
computations after all indices have been generated.  This is especially useful
when you want to compute site- or species-based statistics for large PAMs when
creating a null model.

----

Instantiation
=============
When tracking running statistics, you should first decide if you wish to
compute P-values from an F-statistic.  If so, you will need to provide observed
values when you instantiate the class.  Additionally, you will need to decide
if you want to perform one- or two-tailed tests and provide the appropriate
comparison function.

::

    >>> rs = RunningStats(observed=my_observed_statistic, compare_fn=compare_absolute_values) # One tailed

Tracking statistics
===================
Once you have an instance, simply "push" new values from random data as they
are generated.  When you have generated all the values, or if you want current
statistics, retrieve them from the available properties.

::

    >>> rs = RunningStats(observed=my_observed_statistic, compare_fn=compare_absolute_values) # One tailed
    >>> for i in range(10000):
    ...     rs.push(my_statistic(randomize(observed_data)))
    >>> print('Mean: {}'.format(rs.mean))
    >>> print('Standard deviation: {}'.format(rs.standard_deviation))
    >>> print('P-value: {}'.format(rs.p_values))
