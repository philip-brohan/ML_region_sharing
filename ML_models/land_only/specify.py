# Specification of the model

# As far as possible, everything specific to the model should be in here

# Then the model spec. and dataset input scripts can be generic.
# Follow the instructions in autoencoder.py to use this.

import tensorflow as tf
import numpy as np
from utilities.plots import get_land_mask
from utilities.grids import E5sCube

specification = {}

specification["modelName"] = "Train on land"

specification["inputTensors"] = ("ERA5_tf_MM/2m_temperature",)
specification["outputTensors"] = None  # If None, same as input

specification["outputNames"] = ("T2m",)  # For printout

specification["nInputChannels"] = len(specification["inputTensors"])
if specification["outputTensors"] is not None:
    specification["nOutputChannels"] = len(specification["outputTensors"])
else:
    specification["nOutputChannels"] = specification["nInputChannels"]

specification["startYear"] = None  # Start and end years of training period
specification["endYear"] = None  # (if None, use all available)

specification["testSplit"] = 11  # Keep back test case every n months

# Can use less than all the data (for testing)
specification["maxTrainingMonths"] = None
specification["maxTestMonths"] = None

# What to do if there is more than one field/month
specification["maxEnsembleCombinations"] = (
    5  # Every possible combination of ensembles can get large
)
specification["correlatedEnsembles"] = (
    False  # Ensemble member 1 in source 1 matches member 1 in source 2
)

# Fit parameters
specification["nMonthsInEpoch"] = (
    None  # Length of an epoch - if None, use all the data once
)
specification["nEpochs"] = 250  # How many epochs to train for
specification["shuffleBufferSize"] = 1000  # Buffer size for shuffling
specification["batchSize"] = 32  # Arbitrary
specification["beta"] = 0.001  # Weighting factor for KL divergence of latent space
specification["gamma"] = 0.000  # Weighting factor for KL divergence of output
specification["maxGradient"] = 5  # Numerical instability protection

# Output control
specification["printInterval"] = (
    1  # How often to print metrics and save weights (epochs)
)

# Optimization
specification["strategy"] = tf.distribute.MirroredStrategy()
specification["optimizer"] = tf.keras.optimizers.Adam(1e-3)
specification["trainCache"] = True
specification["testCache"] = True

# Regularization
specification["regularization"] = {
    "encoder_activity": 0.0,
    "encoder_kernel": 0.0,
    "generator_activity": 0.0,
    "generator_kernel": 0.0,
}

# Mask to specify a subset of data to train on
lm = get_land_mask(grid_cube=E5sCube)
specification["trainingMask"] = tf.constant(
    np.reshape(lm.data, [721, 1440, 1]), dtype=tf.int32
)
