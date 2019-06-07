"""Randomize PAMs using CJ's algorithm

This module contains functions used to randomize a PAM using CJ's algorithm.
This algorithm can run in a parallel fashion and uses a fill-based approach so
as to prevent a bias caused by starting with an initial condition of a
populated matrix.

Todo:
    * Clean up
    * Use curveball approach
    * Cite paper
"""
from random import random, choice, randint, shuffle
import numpy as np
import time

from matrix import Matrix

SEARCH_THRESHOLD = 100000 # Number of times to look for a match when fixing problems

# .............................................................................
def randPresAbs(threshold):
    """Picks a random number and return if it is less than the threshold

    Randomly picks a number and returns 1 if it is less than the threshold,
    else returns 0
    """
    if random() <= (threshold * 1.5):
        return 1
    else:
        return 0

# .............................................................................
def colAndRowPlusRbyC(rowTots, colTots, nRows, nCols):
    """Weighting method using column weight + row weight

    This method treats the row and column as one array and uses the
    proportional fill of the combination
    """
    rowWeights = rowTots
    colWeights = colTots
    rowWeights = rowWeights.reshape((nRows, 1))
    colWeights = colWeights.reshape((1, nCols))
    
    return ((rowWeights + colWeights) / (nRows + nCols -1)) + (
        (rowWeights*colWeights)/(nRows*nCols))

# .............................................................................
def maxColOrRow(rowTots, colTots, nRows, nCols):
    """Weighting method using max weight between row and column

    This method returns a matrix of weights where the weight of each cell is
    the maximum between the proportions of the row and col
    """
    rowWeights = rowTots
    colWeights = colTots
    rowWeights = rowWeights.reshape((nRows, 1))
    colWeights = colWeights.reshape((1, nCols))
    
    # Could do this better / faster
    rowOnes = np.ones(rowWeights.shape)
    colOnes = np.ones(colWeights.shape)
    
    a = rowWeights * colOnes
    b = rowOnes * colWeights
    
    return np.maximum.reduce([a, b])

# .............................................................................
def max_col_or_row(row_totals, col_totals):
    """Weighting method using max weight between row and column

    This method returns a matrix of weights where the weight of each cell is
    the maximum between the proportions of the row and col
    """
    row_weights = np.expand_dims(row_totals, 1)
    col_weights = np.expand_dims(col_totals, 0)

    # Todo: Do this with np.tile maybe?
    row_ones = np.ones(row_weights.shape)
    col_ones = np.ones(col_weights.shape)
    a = row_weights * col_ones
    b = row_ones * col_weights
    return np.maximum.reduce([a, b])


# .............................................................................
def gradyRandomize_old(mtx):
    """Main function for creating a random matrix

    Args:
        mtx: A Matrix object representation of a PAM
    """
    mtxData = mtx.data
    mtxHeaders = mtx.get_headers()
    
    # Step 1: Get the marginal totals of the matrix
    # ...........................
    #aTime1 = time.time()
    rowTots = np.sum(mtxData, axis=1)
    colTots = np.sum(mtxData, axis=0)
    nRows, nCols = mtxData.shape
    
    #initialTotal = np.sum(rowTots)
    
    #weights = colAndRowPlusRbyC(rowTots, colTots, nRows, nCols)
    weights = maxColOrRow(rowTots, colTots, nRows, nCols)
    
    
    rowTots = rowTots.reshape((nRows, 1))
    colTots = colTots.reshape((1, nCols))
    
    #bTime1 = time.time()
    #print "Step 1 time: {}".format(bTime1-aTime1)
    
    # Step 2: Get initial random matrix
    # ...........................
    getInitialRandomMatrix = np.vectorize(randPresAbs)
    
    mtx1 = getInitialRandomMatrix(weights)
    
    #bTime2 = time.time()
    #print "Step 2 time: {}".format(bTime2 - bTime1)
    
    # Step 3: Fix broken marginals
    # ...........................
    fixAttempts = 0
    numFixed = 0
    
    for i in xrange(nRows):
        rowSum = np.sum(mtx1[i,:])
        if rowSum > rowTots[i]:
            rowChoices = np.where(mtx1[i] == 1)[0]
            shuffle(rowChoices)
            # for as many indecies as we are over the total
            for x in range(int(rowSum - rowTots[i])):
                mtx1[i, rowChoices[x]] = 0
                numFixed += 1 
        
    for j in xrange(nCols):
        colSum = np.sum(mtx1[:,j])
        if colSum > colTots[0,j]:
            colChoices = np.where(mtx1[:,j] == 1)[0]
            shuffle(colChoices)
            for y in range(int(colSum - colTots[0,j])):
                mtx1[colChoices[y], j] = 0
                numFixed += 1
        
                
    #filledTotal = np.sum(mtx1)
    
    #bTime3 = time.time()
    #print "Step 3 time: {}".format(bTime3 - bTime2)

    # Step 4: Fill
    # ...........................
    problemRows = []
    problemColumns = []
    
    rowSums = np.sum(mtx1, axis=1)
    colSums = np.sum(mtx1, axis=0)
    
    unfilledRows = np.where(rowSums < rowTots[:,0])[0].tolist()
    unfilledCols = np.where(colSums < colTots[0,:])[0].tolist()
    #unfilledRows = np.where(rowSums < rowTots[:,0])[0]
    #unfilledCols = np.where(colSums < colTots[0,:])[0]
    
    #print "Unfilled rows: {}, unfilled columns: {}".format(
    #    unfilledRows.shape, unfilledCols.shape)
    #print "Unfilled rows: {}, unfilled columns: {}".format(
    #    len(unfilledRows), len(unfilledCols))
    
    while len(unfilledRows) > 0:
        possibleCols = []
        #r = np.random.choice(unfilledRows)
        r = choice(unfilledRows)
        possibleCols = list(
            set(np.where(mtx1[r,:] == 0)[0].tolist()
                ).intersection(set(unfilledCols)))
        #possibleCols = np.intersect1d(np.where(mtx1[r,:] == 0)[0], unfilledCols)
        
        if len(possibleCols) == 0:
            #np.delete(unfilledRows, r)
            unfilledRows.remove(r)
            problemRows.append(r)
        else:
            c = choice(possibleCols)
            #c = np.random.choice(possibleCols)
            mtx1[r,c] = 1
            rSum = np.sum(mtx1[r,:])
            cSum = np.sum(mtx1[:,c])
            
            if rSum == int(rowTots[r]):
                unfilledRows.remove(r)
                #np.delete(unfilledRows, r)
            
            if cSum == int(colTots[0, c]):
                unfilledCols.remove(c)
                #np.delete(unfilledCols, c)
    
    #problemColumns = unfilledCols.tolist()
    problemColumns = unfilledCols
    
    #bTime4 = time.time()
    #print "Step 4 time: {}".format(bTime4 - bTime3)
    #print "{} problem columns".format(len(problemColumns))

    # Step 5: Fix problems
    # ...........................
    j = 0
    while problemRows:
        #shuffle(problemRows)
        #shuffle(problemColumns)
        #r = problemRows[0]
        #c = problemColumns[0]
        r = choice(problemRows)
        c = choice(problemColumns)
        i = 0
        
        cs = np.where(mtx1[r] == 0)[0]
        rs = np.where(mtx1[:,c] == 0)[0]
        
        numTries = 0
        found = False
        
        while not found and numTries < SEARCH_THRESHOLD:
            r2 = np.random.choice(rs)
            c2 = np.random.choice(cs)
            numTries += 1
            
            if mtx1[r2,c2] == 1:
                mtx1[r,c2] = 1
                mtx1[r2,c2] = 0
                mtx1[r2,c] = 1
                found = True
        
        if not found:
            raise Exception("Couldn't fix row, col ({}, {})".format(r, c))
        
        #r2 = randint(0, nRows-1)
        #c2 = randint(0, nCols-1)
        # 
        ## Can I do this with numpy?  maybe find all of the combinations and just pick from that?
        #
        #while i < SEARCH_THRESHOLD and not (
        #    mtx1[r,c2] == 0 and mtx1[r2,c2] == 1 and mtx1[r2,c] == 0):
        #    i += 1
        #    r2 = randint(0, nRows-1)
        #    c2 = randint(0, nCols-1)
        #if i < SEARCH_THRESHOLD:
        #    mtx1[r,c2] = 1
        #    mtx1[r2,c2] = 0
        #    mtx1[r2,c] = 1
        #else:
        #    if j < SEARCH_THRESHOLD:
        #        j += 1
        ##    else:
        #        raise Exception ("Couldn't fix row, col (%s, %s)" % (r, c))
        
        rSum = np.sum(mtx1[r,:])#, axis=1)
        cSum = np.sum(mtx1[:,c])#, axis=0)
            
        if rSum == int(rowTots[r]):
            problemRows.remove(r)
        if cSum == int(colTots[0,c]):
            problemColumns.remove(c)
    
    #bTime5 = time.time()
    #print "Step 5 time: {}".format(bTime5 - bTime4)
    #print "Total time: {}".format(bTime5 - aTime1)

    return Matrix(mtx1, headers=mtxHeaders)

# .............................................................................
def grady_randomize(mtx, weights_fn=max_col_or_row):
    """Main function for creating a random matrix

    Args:
        mtx: A Matrix object representation of a PAM
    """
    import time
    # Step 0. Initialize
    # ..................
    # time_0 = time.time()
    mtx_data = mtx.data
    mtx_headers = mtx.get_headers()

    # Get marginal totals
    row_totals = np.sum(mtx_data, axis=1)
    col_totals = np.sum(mtx_data, axis=0)
    num_rows, num_cols = mtx_data.shape

    # Step 1. Build weights matrix
    # time_1 = time.time()
    weights = weights_fn(row_totals, col_totals)
    # Todo: Do better
    row_totals = row_totals.reshape((num_rows, 1))
    col_totals = col_totals.reshape((1, num_cols))

    # Step 2. Get Initial random matrix
    # time_2 = time.time()
    rand_mtx_data = (np.random.uniform(
        low=0.0, high=1.0, size=mtx_data.shape) <= weights).astype(np.int)
    
    # Step 3: Fix broken marginals
    # ...........................
    # For each row / column with more ones than the marginal total, remove
    #    extra ones until within limit
    # time_3 = time.time()
    row_sums = np.sum(rand_mtx_data, axis=1).reshape((num_rows, 1))
    for i in np.where(row_sums > row_totals)[0]:
        row_choices = np.where(rand_mtx_data[i] == 1)[0]
        change_count = int(row_sums[i] - row_totals[i])
        rand_mtx_data[i, np.random.permutation(row_choices)[:change_count]] = False

    col_sums = np.sum(rand_mtx_data, axis=0).reshape((1, num_cols))
    for j in np.where(col_sums > col_totals)[1]:
        col_choices = np.where(rand_mtx_data[:,j] == 1)[0]
        change_count = int(col_sums[0, j] - col_totals[0, j])
        rand_mtx_data[np.random.permutation(col_choices)[:change_count], j] = False

    # Step 4: Fill
    # ...........................
    # time_4 = time.time()
    problem_rows = []
    problem_cols = []
    
    row_sums = np.sum(rand_mtx_data, axis=1)
    col_sums = np.sum(rand_mtx_data, axis=0)
    
    unfilled_cols = np.where(col_sums < col_totals[0, :])[0].tolist()
    for row_idx in np.random.permutation(
        np.where(row_sums < row_totals[:, 0])[0]):

        possible_cols = np.random.permutation(
            np.intersect1d(
                np.where(rand_mtx_data[row_idx, :] == 0)[0],
                unfilled_cols, assume_unique=True))
        num_to_fill = int(row_totals[row_idx, 0] - row_sums[row_idx])
        if num_to_fill > possible_cols.shape[0]:
            # Add this row to problem rows because we can't fill it enough
            problem_rows.append(row_idx)
            # Just fill what we can
            num_to_fill = possible_cols.shape[0]
        # Fill cells
        rand_mtx_data[row_idx, possible_cols[:num_to_fill]] = True

        # Add to col_sums
        col_sums[possible_cols[:num_to_fill]] += 1
        
        # Check if we should remove these columns from the list
        for c in np.where(
            col_sums[possible_cols[:num_to_fill]] == col_totals[
                0, possible_cols[:num_to_fill]])[0]:
            unfilled_cols.remove(possible_cols[c])
    
    problem_cols = unfilled_cols
    

    # Step 5: Fix problems
    # ...........................
    # time_5 = time.time()
    j = 0
    while problem_rows:
        r = choice(problem_rows)
        c = choice(problem_cols)
        i = 0
        
        cs = np.where(rand_mtx_data[r] == 0)[0]
        rs = np.where(rand_mtx_data[:,c] == 0)[0]
        
        num_tries = 0
        found = False
        
        while not found and num_tries < SEARCH_THRESHOLD:
            r2 = np.random.choice(rs)
            c2 = np.random.choice(cs)
            num_tries += 1
            
            if rand_mtx_data[r2,c2] == 1:
                rand_mtx_data[r,c2] = 1
                rand_mtx_data[r2,c2] = 0
                rand_mtx_data[r2,c] = 1
                found = True
        
        if not found:
            raise Exception("Couldn't fix row, col ({}, {})".format(r, c))
        
        r_sum = np.sum(rand_mtx_data[r,:])#, axis=1)
        c_sum = np.sum(rand_mtx_data[:,c])#, axis=0)
            
        if r_sum == int(row_totals[r]):
            problem_rows.remove(r)
        if c_sum == int(col_totals[0,c]):
            problem_cols.remove(c)
    # time_6 = time.time()

    row_sums = np.sum(rand_mtx_data, axis=1)
    
    #print 'Step 0:', time_1 - time_0
    #print 'Step 1:', time_2 - time_1
    #print 'Step 2:', time_3 - time_2
    #print 'Step 3:', time_4 - time_3
    #print 'Step 4:', time_5 - time_4
    #print 'Step 5:', time_6 - time_5

    return Matrix(rand_mtx_data, headers=mtx_headers)
    