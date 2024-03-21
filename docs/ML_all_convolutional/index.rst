A cross-region model with common structure at all locations
===========================================================

Following `previous work <http://brohan.org/Proxy_20CR/>`_, we will base our models on the `Deep Convolutional Variational AutoEncoder (VAE) <https://en.wikipedia.org/wiki/Variational_autoencoder>`_. The difference from the previous work is that we want to minimize the number of parameters that are location-specific. This is to allow the model to be trained on data from one location and then used to generate data for another location.
Convolutional model layers have the useful property that they are location-independent, so this model consists entirely of convolutional layers - the dense layer that previously output the latent space vector has been replaced by additional convolutions. The weakness of this is that it reduces the ability of the model to transfer information between locations, so we add some additional convolutional layers to help with this.

.. figure:: Model_structure.png
   :width: 95%
   :align: center
   :figwidth: 95%

   The structure of the VAE used to train the generator

The model is explicitly designed to train on regionally-limited data. So the :doc:`specification file <specify>` includes a mask. Training is done only on regions indicated by the mask, but the model always calculates output for all regions. This gives us output for regions where we are using data to train, and regions where we are using no training data, separately. The default mask trains only on the Northern Hemisphere.

The model structure and data flows are defined in files that should not need modification:

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Model structure <VAE>
   Input Datasets <make_dataset>

To run the model, we need to specify the model inputs, outputs and hyperparameters. This is done in a specification file. Copy the specification file and the model training script to a new directory, and edit the specification file to suit your needs. Then run the training script. 

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Specification file <specify>
   Training script <training>

And to test the training success there are scripts for plotting the training history and for testing the model on a test dataset.

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Plot training_history <plot_history>
   Validate on single month <validation>
   Validate on time-series <validate_multi>

