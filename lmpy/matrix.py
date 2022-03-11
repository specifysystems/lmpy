"""Module that contains a Matrix class that has header information.

Note:
    * Subclassing based on
        https://docs.scipy.org/doc/numpy/user/basics.subclassing.html

Todo:
    * Handle multiple rows / columns / etc of headers like:
        (PAM x, y, site ids).
    * Load should handle compressed and not compressed.
    * Watch NEP-0018 for Numpy function overrides (ex. concatenate)
"""
from collections.abc import KeysView
from copy import deepcopy
import io
import json
import zipfile

import numpy as np


HEADERS_KEY = 'headers'
METADATA_KEY = 'metadata'
VERSION_KEY = 'version'
VERSION = '2.0.2'
HEADERS_FILENAME = 'headers.json'
DATA_FILENAME = 'data.npz'


# .............................................................................
class Matrix(np.ndarray):
    """Lifemapper wrapper for Numpy ndarrays that adds headers."""

    # ...........................
    def __new__(cls, input_array, headers=None, metadata=None):
        """Create a new Matrix object from an existing ndarray.

        Args:
            input_array (numpy.ndarray): An existing ndarray
            headers (:obj:`dict` or :obj:`list` of :obj:`list` of :obj:`str`):
                Optional headers for this matrix.  This may be either a list of
                lists, where the index of a list in the lists will be treated
                as the axis::
                    (ex. [['Row 1', 'Row 2', 'Row 3'],
                          ['Column 1', 'Column 2']])
                Or this could be a dictionary where the key is used for the
                axis.  (Ex:
                    {
                        '1' : ['Column 1', 'Column 2'],
                        '0' : ['Row 1', 'Row 2', 'Row 3']
                    }
            metadata (:obj:`dict`): Optional metadata about his matrix.

        Note:
            * Triggers a call to Matrix.__array_finalize__.

        Returns:
            Matrix: A converted numpy array to Matrix.
        """
        # input_array is already formed ndarray instance, cast to our type
        obj = np.asarray(input_array).view(cls)

        # Set the 'headers' attribute to the value passed
        if headers is None:
            headers = {}
        if metadata is None:
            metadata = {}
        obj.headers = headers
        obj.metadata = metadata
        return obj

    # ...........................
    def __array_finalize__(self, obj):
        """Overridden function from ndarray.

        ``self`` is a new object resulting from ndarray.__new__(Matrix, ...),
        therefore it only has the attributes that the ndarray.__new__
        constructor gave it.

        Args:
            obj (:obj:`Matrix1): If the object is a matrix, pull out headers and
                metadata.
        """
        # We could have got to the ndarray.__new__ call in 3 ways:
        # 1. From an explicit constructor - Matrix():
        #    obj is None
        #    We're in the middle of the Matrix.__new__ constructor, and
        #        self.headers will be set when we return to Matrix.__new__
        if obj is None:  # pragma: no cover
            return

        # 2. From casting - arr.view(Matrix):
        #    obj is arr
        #    type(obj) can be Matrix
        # 3. From new-from-template - mtx[:3]
        #    type(obj) is Matrix

        # Note: It is is here, rather than the __new__ method, that we set the
        #    default value for 'headers', because this method sees all creation
        #    of default objects
        self.headers = getattr(obj, 'headers', {})
        self.metadata = getattr(obj, 'metadata', {})

    # ...........................
    @classmethod
    def load(cls, filename):
        """Load a matrix from a filename.

        Args:
            filename (:obj:`str`): File location of matrix to load.

        Returns:
            Matrix: The matrix read from the file.
        """
        with open(filename, 'rb') as in_file:
            return Matrix.load_flo(in_file)

    # ...........................
    @classmethod
    def load_csv(cls, flo, dtype=float, num_header_rows=0, num_header_cols=0):
        """Attempts to load a Matrix object from a CSV file-like object.

        Args:
            flo (File-like object): A file like object containing csv data.
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
                    row_headers.append([q.strip() for q in items[:num_header_cols]])
                data.append([dtype(x) for x in items[num_header_cols:]])

            i += 1

        # Process header columns from header rows
        if num_header_rows == 1:
            col_headers = [q.strip() for q in header_lines[0]]
        elif num_header_rows > 1:
            for j in range(len(header_lines[0])):
                hdr = []
                for hdr_idx in range(num_header_rows):
                    hdr.append(header_lines[hdr_idx][j].strip())
                col_headers.append(hdr)

        data_array = np.array(data)

        return cls(data_array, headers={'0': row_headers, '1': col_headers})

    # ...........................
    @classmethod
    def load_flo(cls, flo):
        """Attempts to load a Matrix object from a file.

        Args:
            flo (file-like): A file-like object with matrix data.

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
    def concatenate(cls, mtx_list, axis=0):
        """Concatenates multiple Matrix objects together to form a new Matrix.

        Args:
            mtx_list (:obj:`list` of :obj:`Matrix`): A List of Matrix objects
                to concatenate together.
            axis (:obj:`int`, optional): The axis to concatenate these Matrix objects
                on.  This should be an integer for the matrix axis of concatenation.
                This will be converted to a string where needed for headers.

        Note:
            * Assumes that headers for other axes are the same.

        Returns:
            Matrix: The concatenated Matrix objects.
        """
        mtx_objs = []
        axis_headers = []
        first_mtx = None
        for mtx in mtx_list:
            # Make sure we reshape if necessary if adding new axis (stacking)
            if mtx.ndim < axis + 1:  # Add 1 since zero-based
                mtx = Matrix(np.expand_dims(mtx, axis), headers=mtx.headers)
                mtx.set_headers([''], axis=str(axis))
            # Cast mtx to Matrix in case it is not
            mtx = mtx.view(Matrix)
            h = mtx.get_headers(axis=str(axis))
            if h is None:
                h = ['']
            axis_headers.extend(h)
            mtx_objs.append(mtx)
            if first_mtx is None:
                first_mtx = mtx
        # Create a new Matrix, use the first matrix for base headers and
        #    metadata
        new_mtx = cls(
            np.concatenate(mtx_objs, axis=axis),
            headers=first_mtx.get_headers(),
            metadata=first_mtx.get_metadata(),
        )
        # Set the headers for the new axis
        new_mtx.set_headers(axis_headers, axis=str(axis))
        return new_mtx

    # ...........................
    def flatten_2d(self):
        """Flattens a higher dimension Matrix object into a 2D matrix.

        Todo:
            * Modify this method to take an argument for the number of
                dimensions that the matrix should be flattened to.

        Returns:
            Matrix: A Matrix object flattened to only have two dimensions.
        """
        flat_mtx = self
        while flat_mtx.ndim > 2:
            # More than two dimensions so we must flatten
            old_shape = flat_mtx.shape
            old_num_rows = old_shape[0]
            new_shape = tuple(
                [old_shape[0] * old_shape[2], old_shape[1]] + list(old_shape[3:])
            )
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
                end_row = (i + 1) * old_num_rows
                new_mtx[start_row:end_row, :] = flat_mtx[:, :, i]

                # Set row headers
                for rh in old_rh:
                    if not isinstance(rh, list):
                        rh = [rh]
                    new_rh.append(rh + [oh])

            # Set the headers on the new matrix
            new_mtx.set_row_headers(new_rh)
            new_mtx.set_column_headers(flat_mtx.get_column_headers())

            # Higher order headers
            for axis in flat_mtx.headers.keys():
                if int(axis) > 2:
                    # Reduce the key of the axis by one and set headers on
                    #   new matrix
                    new_mtx.set_headers(
                        flat_mtx.get_headers(axis=axis), axis=str(int(axis) - 1)
                    )

            flat_mtx = new_mtx

        return flat_mtx

    # ...........................
    def get_column_headers(self):
        """Shortcut to get column headers.

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
            dict: If axis is None, a dictionary of all headers for the matrix.
            list: If axis is int, A list of headers for the specified axis.
        """
        try:
            if axis is None:
                return self.headers

            if str(axis) in self.headers.keys():
                return self.headers[str(axis)]

            return None
        except Exception:  # pragma: no cover
            return {}

    # ...........................
    def get_metadata(self):
        """Retrieves matrix metadata.

        Returns:
            dict: A dictionary of metadata for the matrix.
        """
        return self.metadata

    # ...........................
    def get_row_headers(self):
        """Shortcut to get row headers.

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
        my_obj[METADATA_KEY] = self.metadata
        my_obj[VERSION_KEY] = VERSION

        np_bytes = io.BytesIO()
        np.savez_compressed(np_bytes, self)
        np_bytes.seek(0)
        zip_np_str = np_bytes.getvalue()
        np_bytes.close()

        with zipfile.ZipFile(
            flo, mode='w', compression=zipfile.ZIP_DEFLATED, allowZip64=True
        ) as zip_f:

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
            headers (:obj:`dict` or :obj:`list` of :obj:`list` or :obj:`list`): Matrix
                headers.  Can be a list of lists, a dictionary of lists, or if axis is
                provided, a single list.
            axis (:obj:`int`): If provided, set the headers for a specific axis, else,
                process  as if it is for the entire Matrix.

        Todo:
            Validate input for single axis operation?

        Note:
            Resets headers dictionary when setting values for all headers.
            Duck types to use list of lists or dictionary to set values for different
                axes.
        """
        if isinstance(headers, KeysView):
            headers = list(headers)

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
        new_data = np.copy(self)
        new_headers = deepcopy(self.headers)
        # For each arg in the list
        for i in range(len(args)):
            # Subset the data matrix
            new_data = new_data.take(args[i], axis=i)
            # Subset the headers
            tmp = []
            if str(i) in new_headers.keys():
                for j in args[i]:
                    tmp.append(new_headers[str(i)][j])
            new_headers[str(i)] = tmp
        return Matrix(new_data, headers=new_headers)

    # ...........................
    def slice_by_header(self, header, axis):
        """Gets a slice of the Matrix matching the header provided.

        Args:
            header (:obj:`str`): The name of a header to use for slicing
            axis (:obj:`int`): The axis to find this header.

        Todo:
            Add capability to slice over multiple axes and multiple headers.
                Maybe combine with other slice method and provide method to
                search for header indices.

        Returns:
            Matrix: A subset of the original Matrix specified by the header.
        """
        idx = self.headers[str(axis)].index(header)
        new_data = np.copy(np.take(self, idx, axis=axis))

        # Need to reshape the result.  Take the existing shape and change the
        #    query axis to 1
        new_shape = list(self.shape)
        new_shape[axis] = 1
        new_data = new_data.reshape(new_shape)

        # Copy the headers and set the header for the axis to just be the
        #    search header
        new_headers = deepcopy(self.headers)
        new_headers[str(axis)] = [header]

        # Return a new Matrix
        return Matrix(new_data, headers=new_headers, metadata=self.metadata)

    # ...........................
    @property
    def T(self):
        """Get the transpose of the matrix.

        Returns:
            Matrix: The matrix transpose.
        """
        if self.ndim < 2:
            return self

        return self.transpose()

    # ...........................
    def transpose(self, *axes):
        """Transposes the Matrix.

        Args:
            axes (:obj:`None`, :obj:`tuple` of :obj:`int`, n :obj:`int`s): The order of
                the axes in the transposition. see: ndarray.transpose

        Returns:
            Matrix: A transposed version of the original matrix
        """
        new_mtx = Matrix(self.view(np.ndarray).transpose(*axes))
        if len(axes) == 0:
            dim_order = range(len(self.shape) - 1, -1, -1)
        elif isinstance(axes[0], tuple):
            dim_order = list(axes[0])
        else:
            dim_order = list(axes)
        # Set headers
        for i, old_dim in enumerate(dim_order):
            old_dim = str(old_dim)
            try:
                if old_dim in self.get_headers().keys():
                    new_mtx.set_headers(self.get_headers(axis=old_dim), axis=str(i))
            except Exception as err:  # pragma: no cover
                print(err)
                print(dir(self))
        return new_mtx

    # ...........................
    def write(self, filename):
        """Write the matrix to the specified file location.

        Args:
            filename (:obj:`str`): The file location to save to.
        """
        with open(filename, 'wb') as out_file:
            self.save(out_file)

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

        if mtx.ndim > 2:
            mtx = mtx.flatten_2d()

        # .....................
        # Inner functions

        # .....................
        def already_lists(x):
            """Use this function for processing headers when they are lists.

            Args:
                x (:obj:`list`): A list value to return.

            Returns:
                list: A list of data.
            """
            return x

        # .....................
        def make_lists(x):
            """Use this function for processing non-list headers.

            Args:
                x (:obj:`object`): A non-list value to modify.

            Returns:
                list: A list of data.
            """
            return [x]

        # .....................
        def csv_generator():
            """Generator that yields rows of values to be output as CSV.

            Yields:
                list: A list of data for a row.
            """
            try:
                row_headers = mtx.headers['0']
            except (KeyError, TypeError):
                # No row headers
                row_headers = [[] for _ in range(mtx.shape[0])]

            if isinstance(row_headers[0], list):
                listify = already_lists
            else:
                listify = make_lists

            # Start with the header row, if we have one
            if '1' in mtx.headers and mtx.headers['1']:
                # Make column headers lists of lists
                if not isinstance(mtx.headers['1'][0], (tuple, list)):
                    header_row = [''] * len(
                        listify(row_headers[0]) if row_headers else []
                    )
                    header_row.extend(mtx.headers['1'])
                    yield header_row
                else:
                    for i in range(len(mtx.headers['1'][0])):
                        header_row = [''] * len(
                            listify(row_headers[0]) if row_headers else []
                        )
                        header_row.extend(
                            [
                                mtx.headers['1'][j][i]
                                for j in range(len(mtx.headers['1']))
                            ]
                        )
                        yield header_row
            # For each row in the data set
            for i in range(mtx.shape[0]):
                # Add the row headers if exists
                row = []
                row.extend(listify(row_headers[i]))
                # Get the data from the data array
                row.extend(mtx[i].tolist())
                yield row

        # .....................
        # Main write_csv function
        for row in csv_generator():
            flo.write(u"{}\n".format(','.join([str(v) for v in row])))


# .............................................................................
# Set the module for Matrix to be lmpy
Matrix.__module__ = 'lmpy'

__all__ = ['Matrix']
