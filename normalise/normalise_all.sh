#!/usr/bin/bash

# Make normalisation constants for all the datasets
# Requires pre-made raw tensors

(cd ERA5 && ./make_all_fits.py)
