#!/usr/bin/env python

# Make normalised tensors

import os
import argparse

sDir = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument(
    "--variable",
    help="Variable name",
    type=str,
    required=True,
)
args = parser.parse_args()


def is_done(year, month, variable):
    fn = "%s/MLP/normalised_datasets/ERA5_tf_MM/%s/%04d-%02d.tfd" % (
        os.getenv("SCRATCH"),
        variable,
        year,
        month,
    )
    if os.path.exists(fn):
        return True
    return False


for year in range(1950, 2024):
    for month in range(1, 13):
        if is_done(year, month, args.variable):
            continue
        cmd = "%s/make_training_tensor.py --year=%04d --month=%02d --variable=%s" % (
            sDir,
            year,
            month,
            args.variable,
        )
        print(cmd)
