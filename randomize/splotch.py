#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Module containing methods to perform a splotch randomization of a PAM
"""
import numpy as np
import pysal
from random import choice, randrange

from LmCommon.common.matrix import Matrix

# .............................................................................
def splotchRandomize(mtx, shapegridFn, numSides):
    """Randomize a matrix using the Splotch method

    Args:
        mtx: A Matrix object for a PAM
        shapegridFn: File location of shapegrid shapefile
        numSides: The number of sides for each shapegrid cell, used to build
            connectivity matrix

    Note:
        Use Pysal to build an adjacency matrix for the cells in the shapegrid
    """
    mtxHeaders = mtx.getHeaders()
    columnSums = np.sum(mtx.data, axis=0)

    if numSides == 4:
        neighborMtx = pysal.rook_from_shapefile(shapegridFn)
    elif numSides == 6:
        neighborMtx = pysal.queen_from_shapefile(shapegridFn)
    else:
        raise Exception("Invalid number of cell sides")
    
    randomColumns = []
    for colSum in columnSums:
        randomColumns.append(_splotchColumn(neighborMtx, colSum))
    
    randPam = Matrix.concatenate(randomColumns)
    randPam.setHeaders(mtxHeaders)
    return randPam

# .............................................................................
def _splotchColumn(neighborMtx, numPresent):
    """Generates a splotch randomized column

    Args:
        neighborMtx: A PySal generated adjacency matrix (n x n) where n is
            number of cells
        numPresent: The number of cells to set as present
    """
    npCol = np.zeros((neighborMtx.n, 1), dtype=np.bool)
    
    # Need a connected set
    connected = set([])
    
    # Need an explored set
    explored = set([])
    
    # Pick a random start id
    rowId = randrange(0, neighborMtx.n)
    numExplored = 0
    
    # While we have more to explore
    while numExplored < numPresent:
        explored.add(rowId)
        numExplored += 1
        npCol[rowId, 0] = True
        
        # Add new ids to connected set
        newConnections = set(neighborMtx.neighbors[rowId]).difference(explored)
        connected = connected.union(newConnections)

        # Pick a new row id
        rowId = choice(tuple(connected))
        connected.remove(rowId)
        
    return Matrix(npCol)
