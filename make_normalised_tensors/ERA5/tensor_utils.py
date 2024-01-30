# Utility functions for creating and manipulating normalised tensors

import tensorflow as tf
import numpy as np

from get_data.ERA5 import ERA5_monthly
from utilities import grids
from normalise.ERA5.normalise import (
    normalise_cube,
    unnormalise_cube,
    load_fitted,
)


# Load the data for 1 month
def load_raw(year, month, variable="total_precipitation"):
    raw = ERA5_monthly.load(
        variable=variable,
        year=year,
        month=month,
        grid=grids.E5sCube,
    )
    raw.data.data[raw.data.mask == True] = 0.0
    return raw


# Convert raw cube to normalised tensor
def raw_to_tensor(raw, variable, month):
    (shape, location, scale) = load_fitted(month, variable=variable)
    norm = normalise_cube(raw, shape, location, scale)
    norm.data.data[raw.data.mask == True] = 0.0
    ict = tf.convert_to_tensor(norm.data, tf.float32)
    return ict


# Convert normalised tensor to cube
def tensor_to_cube(tensor):
    cube = grids.E5sCube.copy()
    cube.data = tensor.numpy()
    cube.data = np.ma.MaskedArray(cube.data, cube.data == 0.0)
    return cube


# Convert normalised tensor to raw values
def tensor_to_raw(tensor, variable, month):
    (shape, location, scale) = load_fitted(month, variable=variable)
    cube = tensor_to_cube(tensor)
    raw = unnormalise_cube(cube, shape, location, scale)
    raw.data.data[raw.data.mask == True] = 0.0
    return raw
