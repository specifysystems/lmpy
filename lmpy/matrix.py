"""Module that contains a Matrix class that has header information.

Todo:
    * Use https://docs.scipy.org/doc/numpy/user/basics.subclassing.html when
        changing this to subclass numpy.ndarray.
    * Handle multiple rows / columns / etc of headers like:
        (PAM x, y, site ids).
    * Load should handle compressed and not compressed.
"""
from copy import deepcopy
import io
import json
import zipfile

import numpy as np


HEADERS_KEY = 'headers'
DATA_KEY = 'data'
VERSION_KEY = 'version'
VERSION = '3.0.0'
HEADERS_FILENAME = 'headers.json'
DATA_FILENAME = 'data.npz'


# .............................................................................
class Matrix(object):
    """Lifemapper wrapper for Numpy ndarrays that adds headers.

    Attributes:
        data (numpy.ndarray): The base, undecorated data for a Matrix.  It may
            be None if the data has not been initialized.
        headers (dict): A dictionary of headers for each axis of the Matrix.
            Note that the keys must be integer strings.
    """
    # ...........................
    def __init__(self, mtx, headers=None):
        """Constructor.

        Args:
            mtx (numpy.ndarray): A matrix (like) object to use as the base data
                for the Matrix.  This can be None if the data has not been
                initialized.
            headers (:obj:`dict` or :obj:`list` of :obj:`list` of :obj:`str`):
                Headers for this matrixOptional headers for this matrix.  This
                may be either a list of lists, where the index of a list in the
                lists will be treated as the axis::
                    (ex. [['Row 1', 'Row 2', 'Row 3'],
                          ['Column 1', 'Column 2']])
                Or this could be a dictionary where the key is used for the
                axis.  (Ex:
                    {
                        '1' : ['Column 1', 'Column 2'],
                        '0' : ['Row 1', 'Row 2', 'Row 3']
                    }
        """
        self.data = mtx
        self.headers = {}
        if headers is not None:
            self.set_headers(headers)

    # ...........................
    @classmethod
    def load(cls, flo):
        """Attempts to load a Matrix object from a file.

        Args:
            flo (file-like): A file-like object for the stored Matrix or Numpy
                array.

        Todo:
            * Add support for loading a CSV file.

        Returns:
            Matrix: A newly loaded Matrix object.

        Raises:
            IOError: If there is a problem loading the Matrix data.
        """
        # Try loading the Matrix object
        try:
            return cls.load_new(flo)
        except Exception as e1:
            # Try loading a numpy array
            try:
                # Seek back to start of file
                flo.seek(0)
                data = np.load(flo)
                return cls(data)
            except Exception as e:
                raise IOError('{} : {}'.format(
                    'Cannot load matrix data from file-like object provided',
                    str(e)))

    # ...........................
    @classmethod
    def load_csv(cls, flo, dtype=np.float, num_header_rows=0,
                 num_header_cols=0):
        """Attempts to load a Matrix object from a CSV file-like object.

        Args:
            flo (file-like): A file-like object with matrix data.
            dtype (:obj:`method`, optional): The data type for the data.  Will
                be used to cast data when adding to matrix.
            num_header_rows (:obj:`int`, optional): The number of header rows
                in the CSV file.
            num_header_cols (:obj:`int`, optional): The number of header
                columns in the CSV file.

        Returns:
            Matrix: The newly loaded Matrix object.
        """
        col_headers = []
        row_headers = []
        header_lines = []  # Leading rows that are headers
        data = []
        i = 0
        for line in flo:
            items = line.strip().split(',')
            # If header row, add to header rows for processing
            if i < num_header_rows:
                # Add the headers to header lines for processing
                header_lines.append(items[num_header_cols:])
            else:
                if num_header_cols == 1:
                    row_headers.append(items[0].strip())
                elif num_header_cols > 1:
                    row_headers.append(
                        [q.strip() for q in items[:num_header_cols]])
                data.append([dtype(x) for x in items[num_header_cols:]])

            i += 1

        # Process header columns from header rows
        if num_header_rows == 1:
            col_headers = [q.strip() for q in header_lines[0]]
        elif num_header_rows > 1:
            for j in range(len(header_lines[0])):
                h = []
                for x in range(num_header_rows):
                    h.append(header_lines[x][j].strip())
                col_headers.append(h)

        data_array = np.array(data)

        return cls(data_array, headers={'0': row_headers, '1': col_headers})

    # ...........................
    @classmethod
    def load_new(cls, flo):
        """Attempts to load a Matrix object from a file.

        Args:
            flo (file-like): A file-like object with matrix data.

        Todo:
            * Merge this into main load method.

        Returns:
            Matrix: The newly loaded Matrix object.
        """
        with zipfile.ZipFile(flo) as zip_f:
            my_obj = json.loads(zip_f.read(HEADERS_FILENAME).decode('utf-8'))
            data_bytes = io.BytesIO()
            data_bytes.write(zip_f.read(DATA_FILENAME))
            data_bytes.seek(0)
            tmp = np.load(data_bytes)
            data = tmp[tmp.files[0]]
            # data = np.array(tmp[list(tmp.keys())[0]])
            data_bytes.close()

        return cls(data, headers=my_obj[HEADERS_KEY])

    # ...........................
    @classmethod
    def load_our_format_old(cls, flo):  # pragma: no cover
        """Attempts to load a Matrix object from a file.

        Note:
            * This is obsolete and should only be used for legacy data

        Args:
            flo (file-like): A file-like object with matrix data.

        Todo:
            * Merge this into main load method.

        Returns:
            Matrix: The newly loaded Matrix object.
        """
        header_lines = []
        data_lines = []
        do_headers = True
        data_stream = io.BytesIO()
        for line in flo:
            try:
                str_line = line.decode('utf-8')
                if do_headers:
                    if str_line.startswith(DATA_KEY):
                        do_headers = False
                        break
                    else:
                        header_lines.append(str_line)
            except Exception as e:
                data_stream.write(line)
                # data_lines.append(line)

        my_obj = json.loads(''.join(header_lines))

        headers = my_obj[HEADERS_KEY]
        # Load returns a tuple if compressed
        data_stream.seek(0)
        tmp = np.load(data_stream)

        # Get data from temp object, we will return data item for first key
        data = tmp[list(tmp.keys())[0]]
        return cls(data, headers=headers)

    # ...........................
    @classmethod
    def concatenate(cls, mtx_list, axis=0):
        """Concatenates multiple Matrix objects together to form a new Matrix.

        Args:
            mtx_list (:obj:`list` of :obj:`Matrix`): A List of Matrix objects
                to concatenate together.
            axis (int, optional): The axis to concatenate these Matrix objects
                on.  This should be an integer for the matrix axis of
                concatenation.  This will be converted to a string where needed
                for headers.

        Note:
            * Assumes that headers for other axes are the same.

        Returns:
            Matrix: The concatenated Matrix objects.
        """
        mtx_objs = []
        axis_headers = []
        first_mtx = None
        for mtx in mtx_list:
            if not isinstance(mtx, Matrix):
                mtx = Matrix(mtx)
            if mtx.data is not None:
                # Make sure we reshape if necessary if adding new axis
                #    (stacking)
                if mtx.data.ndim < axis + 1:  # Add 1 since zero-based
                    new_shape = list(mtx.data.shape) + [1]
                    mtx.data = mtx.data.reshape(new_shape)
                    mtx.set_headers([''], axis=str(axis))

                h = mtx.get_headers(axis=str(axis))
                if h is None:
                    h = ['']
                axis_headers.extend(h)
                mtx_objs.append(mtx.data)
            if first_mtx is None:
                first_mtx = mtx

        # Create a new data matrix
        new_data = np.concatenate(mtx_objs, axis=axis)
        # Use the first Matrix's headers as the base
        new_headers = first_mtx.get_headers()
        # Replace the axis of headers with the concatenated version
        new_headers[str(axis)] = axis_headers
        return cls(new_data, headers=new_headers)

    # ...........................
    def append(self, mtx, axis=0):
        """Appends the provided Matrix object to this one.

        Args:
            mtx (Matrix): The Matrix object to append to this one.
            axis (:obj:`int`, optional): The axis to append this matrix on.

        Note:
            * Only keeps the headers for the append axis, assumes the other
              axes are the same.
        """
        self.data = np.append(self.data, mtx.data, axis=axis)
        self.headers[str(axis)].append(mtx.get_headers(axis=axis))

    # ...........................
    def flatten_2D(self):
        """Flattens a higher dimension Matrix object into a 2D matrix.

        Todo:
            * Modify this method to take an argument for the number of
                dimensions that the matrix should be flattened to.

        Returns:
            Matrix: A Matrix object flattened to only have two dimensions.
        """
        flat_mtx = self
        while flat_mtx.data.ndim > 2:
            # More than two dimensions so we must flatten
            old_shape = flat_mtx.data.shape
            old_num_rows = old_shape[0]
            new_shape = tuple(
                [old_shape[0]*old_shape[2],
                 old_shape[1]] + list(old_shape[3:]))
            new_mtx = Matrix(np.zeros(new_shape))

            old_rh = flat_mtx.get_row_headers()
            if old_rh is None:
                old_rh = []
            new_rh = []

            # Get old headers
            old_headers = flat_mtx.get_headers(axis=2)
            if old_headers is None:
                old_headers = [''] * old_shape[2]

            # Set data and headers
            for i in range(old_shape[2]):
                oh = old_headers[i]
                # Set data
                start_row = i * old_num_rows
                end_row = (i+1) * old_num_rows
                new_mtx.data[start_row:end_row, :] = flat_mtx.data[:, :, i]

                # Set row headers
                for rh in old_rh:
                    if not isinstance(rh, list):
                        rh = [rh]
                    new_rh.append(rh+[oh])

            # Set the headers on the new matrix
            new_mtx.set_row_headers(new_rh)
            new_mtx.set_column_headers(flat_mtx.get_column_headers())

            # Higher order headers
            for axis in flat_mtx.headers.keys():
                if int(axis) > 2:
                    # Reduce the key of the axis by one and set headers on
                    #   new matrix
                    new_mtx.set_headers(
                        flat_mtx.get_headers(axis=axis),
                        axis=str(int(axis) - 1))

            flat_mtx = new_mtx

        return flat_mtx

    # ...........................
    def get_column_headers(self):
        """Shortcut to get column headers.

        Todo:
            * Throw a different exception if no column header?

        Returns:
            A list of headers for each column.
        """
        return self.get_headers(axis=1)

    # ...........................
    def get_headers(self, axis=None):
        """Gets the headers associated with this Matrix.

        Args:
            axis (:obj:`int`, optional): If provided, return headers for this
                axis, else, return all.

        Returns:
            If axis is None, a dictionary of all headers for the matrix.
            If axis is int, A list of headers for the specified axis.
        """
        if axis is None:
            return self.headers
        else:
            if str(axis) in self.headers.keys():
                return self.headers[str(axis)]
            else:
                return None

    # ...........................
    def get_row_headers(self):
        """Shortcut to get row headers.

        Todo:
            * Throw a different exception if no row headers?

        Returns:
            A list of headers for the rows in the matrix.
        """
        return self.get_headers(axis=0)

    # ...........................
    def save(self, flo):
        """Saves the Matrix to a file-like object.

        Saves the Matrix object in a JSON / Numpy zip file to the file-like
        object.

        Args:
            flo (file-like): The file-like object to write to.
        """
        my_obj = {}
        my_obj[HEADERS_KEY] = self.headers
        my_obj[VERSION_KEY] = VERSION

        np_bytes = io.BytesIO()
        np.savez_compressed(np_bytes, self.data)
        np_bytes.seek(0)
        zip_np_str = np_bytes.getvalue()
        np_bytes.close()

        with zipfile.ZipFile(
            flo, mode='w', compression=zipfile.ZIP_DEFLATED,
                allowZip64=True) as zip_f:

            zip_f.writestr(HEADERS_FILENAME, json.dumps(my_obj, default=float))
            zip_f.writestr(DATA_FILENAME, zip_np_str)

    # ...........................
    def set_column_headers(self, headers):
        """Shortcut to set column headers.

        Args:
            headers (:obj:`list` of :obj:`str`): A list of new column headers.
        """
        self.set_headers(headers, axis=1)

    # ...........................
    def set_headers(self, headers, axis=None):
        """Sets the headers for this Matrix.

        Args:
            headers (:obj:`dict` or :obj:`list` of :obj:`list` or :obj:`list`):
                Matrix headers.  Can be a list of lists, a dictionary of lists,
                or if axis is provided, a single list.
            axis (:obj:`int`): If provided, set the headers for a specific
                axis, else, process as if it is for the entire Matrix.

        Todo:
            * Validate input for single axis operation?

        Note:
            * Resets headers dictionary when setting values for all headers.
            * Duck types to use list of lists or dictionary to set values for
                different axes.

        """
        if axis is not None:
            self.headers[str(axis)] = headers
        else:
            self.headers = {}

            for k in headers.keys():
                self.headers[str(k)] = headers[str(k)]

    # ...........................
    def set_row_headers(self, headers):
        """Shortcut to set row headers.

        Args:
            headers (:obj:`list` of :obj:`str`): A list of new row headers.
        """
        self.set_headers(headers, axis=0)

    # ...........................
    def slice(self, *args):
        """Subsets the matrix and returns a new instance.

        Args:
            *args: A variable length argument list of iterables for the indices
                to retrieve for each axis.

        Note:
            * The first parameter will be for axis 0, second for axis 1, etc.

        Returns:
            Matrix: A new Matrix that is a subset of the original specified by
                the slicing parameters.
        """
        new_data = np.copy(self.data)
        new_headers = deepcopy(self.headers)
        # For each arg in the list
        for i in range(len(args)):
            # Subset the data matrix
            new_data = new_data.take(args[i], axis=i)
            # Subset the headers
            tmp = []
            for j in args[i]:
                tmp.append(new_headers[str(i)][j])
            new_headers[str(i)] = tmp
        return Matrix(new_data, headers=new_headers)

    # ...........................
    def slice_by_header(self, header, axis):
        """Gets a slice of the Matrix matching the header provided.

        Args:
            header (str): The name of a header to use for slicing
            axis (int): The axis to find this header.

        Raises:
            ValueError: If the header is not found for the specified axis.

        Todo:
            * Add capability to slice over multiple axes and multiple headers.
                Maybe combine with other slice method and provide method to
                search for header indices.

        Returns:
            Matrix: A subset of the original Matrix specified by the header.
        """
        idx = self.headers[str(axis)].index(header)

        new_data = np.copy(np.take(self.data, idx, axis=axis))

        # Need to reshape the result.  Take the existing shape and change the
        #    query axis to 1
        new_shape = list(self.data.shape)
        new_shape[axis] = 1
        new_data = new_data.reshape(new_shape)

        # Copy the headers and set the header for the axis to just be the
        #    search header
        new_headers = deepcopy(self.headers)
        new_headers[str(axis)] = [header]

        # Return a new Matrix
        return Matrix(new_data, headers=new_headers)

    # ...........................
    def write_csv(self, flo, *slice_args):
        """Writes the Matrix object to a CSV file-like object.

        Args:
            flo (file-like): The file-like object to write to.
            *slice_args: A variable length argument list of iterables to use
                for a slice operation prior to generating CSV content.

        Todo:
            Handle header overlap (where the header for one axis is for another
                axis header.

        Note:
            Currently only works for 2-D tables.
        """
        if list(slice_args):
            mtx = self.slice(*slice_args)
        else:
            mtx = self

        if mtx.data.ndim > 2:
            mtx = mtx.flatten_2D()

        # .....................
        # Inner functions

        # .....................
        def already_lists(x):
            """Use this function for processing headers when they are lists.
            """
            return x

        # .....................
        def make_lists(x):
            """Use this function for processing non-list headers.
            """
            return [x]

        # .....................
        def csv_generator():
            """Generator that yields rows of values to be output as CSV.
            """
            try:
                row_headers = mtx.headers['0']
            except:
                # No row headers
                row_headers = [[] for _ in range(mtx.data.shape[0])]

            if isinstance(row_headers[0], list):
                listify = already_lists
            else:
                listify = make_lists

            # Start with the header row, if we have one
            if '1' in mtx.headers and mtx.headers['1']:
                # Make column headers lists of lists
                if not isinstance(mtx.headers['1'][0], (tuple, list)):
                    header_row = ['']*len(
                        listify(row_headers[0]) if row_headers else [])
                    header_row.extend(mtx.headers['1'])
                    yield header_row
                else:
                    for i in range(len(mtx.headers['1'][0])):
                        header_row = ['']*len(
                            listify(row_headers[0]) if row_headers else [])
                        header_row.extend(
                            [mtx.headers['1'][j][i] for j in range(
                                len(mtx.headers['1']))])
                        yield header_row
            # For each row in the data set
            for i in range(mtx.data.shape[0]):
                # Add the row headers if exists
                row = []
                row.extend(listify(row_headers[i]))
                # Get the data from the data array
                row.extend(mtx.data[i].tolist())
                yield row

        # .....................
        # Main write_csv function
        for row in csv_generator():
            flo.write(u"{0}\n".format(','.join([str(v) for v in row])))


# .............................................................................
class ArrayStream(list):
    """Generator class for a numpy array for JSON serialization.

    Attributes:
        x (numpy.ndarray): A numpy array to be streamed to JSON serialization.
        my_len (int): The size of the first dimension of the array.

    Note:
        * This is done to save memory rather than creating a list of the entire
            array / matrix.  It is used by the JSON encoder to write the data
            to file.
    """
    # ...........................
    def __init__(self, x):
        """Constructor.

        Args:
            x : The numpy array to stream.
        """
        self.x = x
        self.my_len = self.x.shape[0]

    # ...........................
    def __iter__(self):
        """Iterator for array.
        """
        return self.gen()

    # ...........................
    def __len__(self):
        """Length function.
        """
        return self.my_len

    # ...........................
    def gen(self):
        """Loops over array and create ArrayStreams for sub arrays.

        Yields:
            The next item in the stream.
        """
        n = 0

        while n < self.my_len:
            if isinstance(self.x[n], np.ndarray):
                yield ArrayStream(self.x[n])
            else:
                yield self.x[n]
            n += 1

# .............................................................................
# Set the module for Matrix to be lmpy
Matrix.__module__ = 'lmpy'

__all__ = ['ArrayStream', 'Matrix']
