#!/usr/bin/env python

# Make all the normalization fits

import os

sDir = os.path.dirname(os.path.realpath(__file__))


def is_done(month, variable):
    fn = "%s/MLP/normalization/SPI_monthly/ERA5_tf_MM/%s/shape_m%02d.nc" % (
        os.getenv("SCRATCH"),
        variable,
        month,
    )
    if os.path.exists(fn):
        return True
    return False


count = 0
for variable in (
    "2m_temperature",
    "mean_sea_level_pressure",
    "total_precipitation",
    "sea_surface_temperature",
):
    for month in range(1, 13):
        if is_done(month, variable):
            continue
        cmd = "%s/fit_for_month.py --month=%02d --variable=%s" % (
            sDir,
            month,
            variable,
        )
        print(cmd)
