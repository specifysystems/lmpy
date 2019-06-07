"""This module tests the analyses/lm_objects/matrix.py module.

Note:
    * These test functions are pytest style tests for the matrix.py module.
"""
import io
import random
import tempfile

import numpy as np
import pytest

from lmpy import matrix


# .............................................................................
def get_random_matrix(*dim_size):
    """Generates a randomized matrix with the shape provided in dim_size.

    Args:
        *dim_size (:obj:`list` of :obj:`int`): Variable length argument list of
            integers representing matrix dimension sizes.
    """
    headers = {}
    i = 0
    for i in range(len(dim_size)):
        headers[str(i)] = [
            'header-{}-{}'.format(i, x) for x in range(dim_size[i])]
    return matrix.Matrix(np.random.rand(*dim_size), headers=headers)


# .............................................................................
class Test_Matrix(object):
    """Test the Matrix class.
    """
    # .....................................
    def test_load(self):
        """Test the load class method.
        """
        orig_mtx = get_random_matrix(5, 5)

        # Create a file like object and save original matrix
        mtx_bytesio = io.BytesIO()
        orig_mtx.save(mtx_bytesio)
        mtx_bytesio.seek(0)

        # Attempt to load matrix
        loaded_mtx = matrix.Matrix.load(mtx_bytesio)
        mtx_bytesio.close()

        # Verify data and headers are the same
        assert np.allclose(loaded_mtx.data, orig_mtx.data)
        assert loaded_mtx.get_headers() == orig_mtx.get_headers()

        # Write to temp file
        with tempfile.TemporaryFile() as out_f:
            np.save(out_f, orig_mtx.data)
            out_f.seek(0)
            np_mtx = matrix.Matrix.load(out_f)

        # Verify that the data is the same
        assert np.allclose(np_mtx.data, orig_mtx.data)

        # Verify load fails with empty file
        with pytest.raises(IOError):
            mtx = matrix.Matrix.load(io.BytesIO())

    # .....................................
    def test_load_csv(self):
        """Test the load_csv method.
        """
        orig_mtx = get_random_matrix(5, 5)

        with io.StringIO() as out_str:
            orig_mtx.write_csv(out_str)
            out_str.seek(0)

            # Attempt to load matrix
            loaded_mtx = matrix.Matrix.load_csv(
                out_str, num_header_rows=1, num_header_cols=1)

        print(loaded_mtx.get_headers())
        print(orig_mtx.get_headers())

        # Verify data and headers are the same
        assert np.allclose(loaded_mtx.data, orig_mtx.data)
        assert loaded_mtx.get_headers() == orig_mtx.get_headers()

    # .....................................
    def test_load_csv_multi_headers(self):
        """Test the load_csv method.
        """
        orig_mtx = get_random_matrix(5, 5)
        new_row_headers = []
        new_col_headers = []
        orig_row_headers = orig_mtx.get_row_headers()
        orig_col_headers = orig_mtx.get_column_headers()

        for h in orig_row_headers:
            new_row_headers.append([h, '{}-2'.format(h)])
        orig_mtx.set_row_headers(new_row_headers)
        for h in orig_col_headers:
            new_col_headers.append([h, '{}-2'.format(h)])
        orig_mtx.set_column_headers(new_col_headers)

        print(orig_mtx.get_headers())

        with io.StringIO() as out_str:
            orig_mtx.write_csv(out_str)
            out_str.seek(0)
            print(out_str.getvalue())
            out_str.seek(0)

            # Attempt to load matrix
            loaded_mtx = matrix.Matrix.load_csv(
                out_str, num_header_rows=2, num_header_cols=2)

        print(loaded_mtx.get_headers())
        print(orig_mtx.get_headers())

        # Verify data and headers are the same
        assert np.allclose(loaded_mtx.data, orig_mtx.data)
        assert loaded_mtx.get_headers() == orig_mtx.get_headers()

    # .....................................
    def test_load_new(self):
        """Test the load_new method.
        """
        orig_mtx = get_random_matrix(5, 5)

        # Create a file like object and save original matrix
        mtx_bytesio = io.BytesIO()
        orig_mtx.save(mtx_bytesio)
        mtx_bytesio.seek(0)

        # Attempt to load matrix
        loaded_mtx = matrix.Matrix.load_new(mtx_bytesio)
        mtx_bytesio.close()

        # Verify data and headers are the same
        assert np.allclose(loaded_mtx.data, orig_mtx.data)
        assert loaded_mtx.get_headers() == orig_mtx.get_headers()

    # .....................................
    def test_concatenate(self):
        """Test the concatenate function.
        """
        mtx1 = get_random_matrix(3, 2)
        mtx2 = get_random_matrix(3, 3)
        mtx3 = get_random_matrix(6, 5)

        # Concatenate matrices
        mtx4 = matrix.Matrix.concatenate([mtx1, mtx2], axis=1)
        mtx5 = matrix.Matrix.concatenate([mtx4, mtx3], axis=0)

        # Check that shapes are what we expect
        assert mtx4.data.shape == (mtx1.data.shape[0],
                                   mtx1.data.shape[1] + mtx2.data.shape[1])
        assert mtx5.data.shape == (mtx4.data.shape[0] + mtx3.data.shape[0],
                                   mtx4.data.shape[1])

        # Concatenate numpy arrays
        mtx6 = matrix.Matrix.concatenate(
            [np.random.random((4, 2)), np.random.random((4, 6))], axis=1)
        assert mtx6.data.shape == (4, 8)

        # Concatenate a stack and a single
        mtx7 = get_random_matrix(4, 4, 3)
        mtx8 = get_random_matrix(4, 4)
        mtx9 = matrix.Matrix.concatenate([mtx7, mtx8], axis=2)
        assert mtx9.data.shape == (4, 4, 4)

    # .....................................
    def test_append(self):
        """Test append.
        """
        x1, y1 = (3, 4)
        x2, y2 = (6, 4)
        mtx1 = get_random_matrix(x1, y1)
        mtx2 = get_random_matrix(x2, y2)
        mtx1.append(mtx2, axis=0)

        # Verify the new shape
        assert mtx1.data.shape == (x1 + x2, y1)

    # .....................................
    def test_flatten_2D(self):
        """Test flatten_2D method.
        """
        x, y, z = 5, 5, 3
        mtx = get_random_matrix(x, y, z)
        flat_mtx = mtx.flatten_2D()

        # Test that there are two dimensions of headers and data
        assert len(flat_mtx.data.shape) == 2
        assert len(flat_mtx.get_headers().keys()) == 2

        # Test that the length of the row headers is now 2 (accounting for
        #    the flattened dimension
        for h in flat_mtx.get_row_headers():
            assert len(h) == 2

        # Check that the data shape in the row dimension is z * old shape
        assert flat_mtx.data.shape[0] == x * z

    # .....................................
    def test_flatten_2D_higher_dim(self):
        """Test flatten_2D method.
        """
        a, b, c, d = 4, 5, 6, 7
        mtx = get_random_matrix(a, b, c, d)
        flat_mtx = mtx.flatten_2D()

        # Test that there are two dimensions of headers and data
        assert len(flat_mtx.data.shape) == 2
        assert len(flat_mtx.get_headers().keys()) == 2

        # Test that the length of the row headers is now 3 (accounting for
        #    the flattened dimensions
        for h in flat_mtx.get_row_headers():
            assert len(h) == 3

        # Check that the data shape in the row dimension is c * a * d
        assert flat_mtx.data.shape[0] == a * c * d

    # .....................................
    def test_flatten_2D_missing_header(self):
        """Test flatten_2D method when headers are missing.
        """
        x, y, z = 5, 5, 3
        mtx = matrix.Matrix(np.random.random((x, y, z)))
        flat_mtx = mtx.flatten_2D()

        # Test that there are two dimensions of headers and data
        assert len(flat_mtx.data.shape) == 2
        assert len(flat_mtx.get_headers().keys()) == 2

        # Test that the length of the row headers is now 2 (accounting for
        #    the flattened dimension
        for h in flat_mtx.get_row_headers():
            assert len(h) == 2

        # Check that the data shape in the row dimension is z * old shape
        assert flat_mtx.data.shape[0] == x * z

    # .....................................
    def test_get_column_headers(self):
        """Test get_column_headers.
        """
        mtx = get_random_matrix(3, 8)
        col_headers = mtx.get_column_headers()
        assert isinstance(col_headers, list)
        assert len(col_headers) == mtx.data.shape[1]

    # .....................................
    def test_get_headers(self):
        """Test get_headers.
        """
        mtx = get_random_matrix(2, 2, 4)
        headers = mtx.get_headers()
        assert isinstance(headers, dict)
        for i in range(len(mtx.data.shape)):
            assert len(headers[str(i)]) == mtx.data.shape[i]
        assert mtx.get_headers(axis=9999) is None

    # .....................................
    def test_get_row_headers(self):
        """Test get_row_headers.
        """
        mtx = get_random_matrix(3, 8)
        row_headers = mtx.get_row_headers()
        assert isinstance(row_headers, list)
        assert len(row_headers) == mtx.data.shape[0]

    # .....................................
    def test_save(self):
        """Test the save method.

        Save should save a Matrix object to a file that can be loaded later.
        """
        orig_mtx = get_random_matrix(5, 5)

        # Create a file like object and save original matrix
        with tempfile.TemporaryFile() as save_f:
            # Save the original matrix
            orig_mtx.save(save_f)

            # Load the saved Matrix
            save_f.seek(0)
            loaded_mtx = matrix.Matrix.load(save_f)

        # Verify data and headers are the same
        assert np.allclose(loaded_mtx.data, orig_mtx.data)
        assert loaded_mtx.get_headers() == orig_mtx.get_headers()

    # .....................................
    def test_set_column_headers(self):
        """Test set_column_headers.
        """
        n_rows, n_cols = (9, 6)
        mtx = get_random_matrix(n_rows, n_cols)
        new_col_headers = ['Col head - {}'.format(i**2) for i in range(n_cols)]

        # Test that current column headers do not match new
        old_col_headers = mtx.get_column_headers()
        assert not all(
            [new_col_headers[i] == old_col_headers[i] for i in range(n_cols)])

        # Set the column headers and check that they now match
        mtx.set_column_headers(new_col_headers)
        mtx_new_headers = mtx.get_column_headers()
        assert all(
            [new_col_headers[i] == mtx_new_headers[i] for i in range(n_cols)])

    # .....................................
    def test_set_headers(self):
        """Test set_headers.
        """
        n_rows, n_cols = (8, 10)
        mtx = get_random_matrix(n_rows, n_cols)
        new_col_headers = ['Col head - {}'.format(i**2) for i in range(n_cols)]
        new_row_headers = ['Row head - {}'.format(i**2) for i in range(n_rows)]

        # Test that current headers do not match new
        old_col_headers = mtx.get_column_headers()
        old_row_headers = mtx.get_row_headers()
        assert not all(
            [new_col_headers[i] == old_col_headers[i] for i in range(n_cols)])
        assert not all(
            [new_row_headers[i] == old_row_headers[i] for i in range(n_rows)])

        # Set the row headers and check that they now match
        mtx.set_headers({'0': new_row_headers, '1': new_col_headers})
        test_col_headers = mtx.get_column_headers()
        test_row_headers = mtx.get_row_headers()
        assert all(
            [new_col_headers[i] == test_col_headers[i] for i in range(n_cols)])
        assert all(
            [new_row_headers[i] == test_row_headers[i] for i in range(n_rows)])

    # .....................................
    def test_set_row_headers(self):
        """Test set_row_headers.
        """
        n_rows, n_cols = (9, 6)
        mtx = get_random_matrix(n_rows, n_cols)
        new_row_headers = ['Row head - {}'.format(i**2) for i in range(n_rows)]

        # Test that current row headers do not match new
        old_row_headers = mtx.get_row_headers()
        assert not all(
            [new_row_headers[i] == old_row_headers[i] for i in range(n_rows)])

        # Set the row headers and check that they now match
        mtx.set_row_headers(new_row_headers)
        mtx_new_headers = mtx.get_row_headers()
        assert all(
            [new_row_headers[i] == mtx_new_headers[i] for i in range(n_rows)])

    # .....................................
    def test_slice(self):
        """Test the slice method.
        """
        # Randomly generate size of matrix
        n_dim = random.randint(2, 4)
        dims = []
        for i in range(n_dim):
            d_size = random.randint(1, 20)
            d_lower = random.randint(0, d_size - 1)
            d_upper = random.randint(d_lower + 1, d_size)
            dims.append((d_size, d_lower, d_upper))

        # Generate the matrix and get original headers
        mtx = get_random_matrix(*tuple([j[0] for j in dims]))
        orig_headers = mtx.get_headers()

        # Get slice parameters and slice matrix
        slice_params = tuple([range(j[1], j[2]) for j in dims])
        sliced_mtx = mtx.slice(*slice_params)

        # Test data matrix
        test_data = mtx.data

        # For each dimension, check the size, and headers
        for i in range(n_dim):
            dim_size, dim_lower, dim_upper = dims[i]
            assert sliced_mtx.data.shape[i] == dim_upper - dim_lower

            # Check headers
            orig_dim_headers = mtx.get_headers(axis=i)
            dim_headers = sliced_mtx.get_headers(axis=i)
            for j in range(len(dim_headers)):
                assert dim_headers[j] == orig_dim_headers[j + dim_lower]

            # Slice data for testing
            test_data = test_data.take(range(dim_lower, dim_upper), axis=i)

        # Check data
        assert np.allclose(test_data, sliced_mtx.data)

    # .....................................
    def test_slice_by_header(self):
        """Test slice_by_header.
        """
        mtx = get_random_matrix(3, 3, 3)
        # Get the header to use for slicing, we'll use layer 2
        slice_header = list(mtx.get_headers(axis=2))[1]

        # Slice the matrix to only that layer
        sliced_mtx = mtx.slice_by_header(slice_header, axis=2)

        # Check that the shape is correct, should be (3, 3, 1)
        assert sliced_mtx.data.shape == (3, 3, 1)

        # Check that data is the second layer
        assert np.allclose(sliced_mtx.data[:, :, 0], mtx.data[:, :, 1])

        # Check that the headers are what we expect
        assert mtx.get_row_headers() == sliced_mtx.get_row_headers()
        assert mtx.get_column_headers() == sliced_mtx.get_column_headers()
        assert [mtx.get_headers(axis=2)[1]] == sliced_mtx.get_headers(axis=2)
        assert len(sliced_mtx.get_headers(axis=2)) == 1

    # .....................................
    def test_write_csv_no_slice(self):
        """Test write_csv with no slicing.
        """
        mtx = get_random_matrix(10, 10)

        with io.StringIO() as out_str:
            mtx.write_csv(out_str)
            out_str.seek(0)

            # Test that csv can be read
            for line in out_str:
                assert len(line.split(',')) > 1

    # .....................................
    def test_write_csv_no_slice_list_row_headers(self):
        """Test write_csv with no slicing and a list of row headers.
        """
        mtx = get_random_matrix(10, 10)
        o_rh = mtx.get_row_headers()
        new_rh = []
        for h in o_rh:
            new_rh.append([h, 'a', 'b'])
        mtx.set_row_headers(new_rh)

        with io.StringIO() as out_str:
            mtx.write_csv(out_str)
            out_str.seek(0)

            # Test that csv can be read
            for line in out_str:
                assert len(line.split(',')) > 1

    # .....................................
    def test_write_csv_no_slice_no_row_headers(self):
        """Test write_csv no slicing and no row headers.
        """
        o_mtx = get_random_matrix(10, 10)
        mtx = matrix.Matrix(o_mtx.data)

        with io.StringIO() as out_str:
            mtx.write_csv(out_str)
            out_str.seek(0)

            # Test that csv can be read
            for line in out_str:
                assert len(line.split(',')) > 1

    # .....................................
    def test_write_csv_slice(self):
        """Test write_csv with slicing.
        """
        mtx = get_random_matrix(10, 10, 2)

        with io.StringIO() as out_str:
            mtx.write_csv(out_str, range(0, 10), range(0, 1), [0])
            out_str.seek(0)

            # Test that csv can be read
            for line in out_str:
                assert len(line.split(',')) > 1


# .............................................................................
class Test_ArrayStream(object):
    """Test the ArrayStream class.
    """
    # .....................................
    def test_gen_1d(self):
        """Test the gen function with a 1d array.

        Note:
            * gen() is an iterator and can be tested as such.
            * The ArrayStream object uses 'gen' when it is treated as an
                iterator.
        """
        arr = np.array([1, 2, 3])
        stream = matrix.ArrayStream(arr)
        assert len(stream) == arr.shape[0]
        for i in stream:
            assert i is not None

    # .....................................
    def test_gen_2d(self):
        """Test the gen function with a 2d array.

        Note:
            * gen() is an iterator and can be tested as such.
            * The ArrayStream object uses 'gen' when it is treated as an
                iterator.
        """
        arr = np.array([[1, 2, 3], [4, 5, 6]])
        stream = matrix.ArrayStream(arr)
        assert len(stream) == arr.shape[0]
        for i in stream:
            assert i is not None
