Regional cross-training in ML climate models
============================================

A major challenge in the application of Machine Learning (ML) to climate science is the limited availability of training data. The decorrelation time of the atmosphere is a few days, so there are only of order 100 independent atmospheric states per year. If we have 100 years of training data, this means that there are about 10,000 independent states in total. And this is a best case - if we are training on monthly averages, the number is ten times smaller, and there are many parts of the world where we don't have 100 years of data - where observational data are available only for a few decades. This is enough training data to fit an `ML climate model <http://brohan.org/Proxy_20CR/>`_, but very much at the low end of what is needed for a deep learning model.

So a key skill, in climate ML, is going to be making the most efficient use of limited data. This document describes a method for training a model on data from one region, and then applying it to another region. This is a form of transfer learning, and it is a way of making the most of the data that we have.

.. figure:: ../ML_models/all_convolutional/comparison.webp
   :width: 95%
   :align: center
   :figwidth: 95%

   :doc:`Validation plot <ML_all_convolutional/validation>` of an ML model trained only on data from the Northern Hemisphere (NH), and then applied to the Southern Hemisphere (SH). Left-hand column is the target field (:doc:`normalized 2m-temperature <normalization/index>`), centre column is the model output, and the two right-hand columns are scatter plots for the Northern and Southern Hemispheres.

`Previous work <http://brohan.org/Proxy_20CR/>`_ has built ML climate models based on a conventional Deep Convolutional Variational Autoencoder (DCVAE). These models have a mix of convolutional layers and fully connected layers. Convolutional layers are an obvious choice if training data is spatially limited, as they learn and apply the same set of spatial patterns at all locations. But fully connected layers are a problem, because they have no spatial restrictions, and will optimize themselves to the training data only - and can't be expected to produce useful results in a region where they haven't been trained. 

So, inspired by the design of the autoencoder used in `stable diffusion <https://stability.ai/stable-image>`_, we have built a DCVAE with only convolutional layers:

.. figure:: ML_all_convolutional/Model_structure.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Structure of the all-convolutional model. The encoder and decoder are both made up of a series of convolutional layers, with no fully connected layers. The latent space is a 3D grid. (:doc:`Details <ML_all_convolutional/index>`).

The model takes, as part of its input, a training mask. So it operates on `ERA5 <https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5>`_ data, but trains to reproduce only the subset of that data where the mask is set. This means we can train on Northern Hemisphere data only (for example) but still evaluate the model on both the Northern Hemisphere, and the Southern Hemisphere (where it has not trained - we're relying on the Northern Hemisphere result to generalize). The figure above shows how well this works, and we can also validate with a time-series of hemispheric averages:

.. figure:: ../ML_models/all_convolutional/multi.webp
   :width: 95%
   :align: center
   :figwidth: 95%

   Global mean series (black original, red DCVAE output) and scatter plots for hemispheric means of 2m temperature. Top panel shows NH (used for training). Bottom panel shows SH (masked from training). (:doc:`Details <ML_all_convolutional/validate_multi>`).

The results are better in the region trained on - but the difference is small. The model has generalized well.

Note that a key component of the generalizability of the model is the use of a :doc:`normalization scheme <normalization/index>` that homogenizes the distribution of the data across the globe. This is a key part of the training process, and is essential for the model to be able to generalize to regions where it has not been trained.

Appendices
----------

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Get the training data <get_data/index>
   Normalize the data for model fitting <normalization/index>
   An ML model with common structure at all locations <ML_all_convolutional/index>
   Utility functions for plotting and re-gridding <utils/index>


Small print
-----------

.. toctree::
   :titlesonly:
   :maxdepth: 1

   How to reproduce or extend this work <how_to>
   Authors and acknowledgements <credits>


  
This document is crown copyright (2024). It is published under the terms of the `Open Government Licence <https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/>`_. Source code included is published under the terms of the `BSD licence <https://opensource.org/licenses/BSD-2-Clause>`_.
