# Specify a Deep Convolutional Variational AutoEncoder

# This is a generic model that can be used for any set of input and output fields
# Follow the instructions in autoencoder.py to use it for a specific model.

import os
import tensorflow as tf


class DCVAE(tf.keras.Model):
    # Initialiser - set up instance and define the models
    def __init__(self, specification):
        super(DCVAE, self).__init__()
        self.specification = specification

        # Model to encode input to latent space distribution
        self.encoder = tf.keras.Sequential(
            [
                tf.keras.layers.InputLayer(
                    input_shape=(721, 1440, self.specification["nInputChannels"])
                ),
                tf.keras.layers.Conv2D(
                    filters=5 * 2,
                    kernel_size=3,
                    strides=(2, 2),
                    padding="same",
                    activation="elu",
                ),
                tf.keras.layers.Conv2D(
                    filters=10 * 2,
                    kernel_size=3,
                    strides=(2, 2),
                    padding="same",
                    activation="elu",
                ),
                tf.keras.layers.Conv2D(
                    filters=10 * 2,
                    kernel_size=3,
                    strides=(2, 2),
                    padding="same",
                    activation="elu",
                ),
                tf.keras.layers.Conv2D(
                    filters=20 * 2,
                    kernel_size=3,
                    strides=(2, 2),
                    padding="same",
                    activation="elu",
                ),
                tf.keras.layers.Conv2D(
                    filters=40 * 2,
                    kernel_size=3,
                    strides=(2, 2),
                    padding="same",
                    activation="elu",
                ),
                tf.keras.layers.Flatten(),
                # No activation
                tf.keras.layers.Dense(
                    self.specification["latentDimension"] * 2,
                    kernel_regularizer=tf.keras.regularizers.L2(
                        self.specification["regularization"]["encoder_kernel"]
                    ),
                    activity_regularizer=tf.keras.regularizers.L2(
                        self.specification["regularization"]["encoder_activity"]
                    ),
                ),
            ]
        )

        # Model to generate output from latent space
        self.generator = tf.keras.Sequential(
            [
                tf.keras.layers.InputLayer(
                    input_shape=(self.specification["latentDimension"],)
                ),
                tf.keras.layers.Dense(
                    units=23 * 45 * 40 * 2,
                    activation="elu",
                    kernel_regularizer=tf.keras.regularizers.L2(
                        self.specification["regularization"]["generator_kernel"]
                    ),
                    activity_regularizer=tf.keras.regularizers.L2(
                        self.specification["regularization"]["generator_activity"]
                    ),
                ),
                tf.keras.layers.Reshape(target_shape=(23, 45, 40 * 2)),
                tf.keras.layers.Conv2DTranspose(
                    filters=20 * 2,
                    kernel_size=3,
                    strides=2,
                    padding="same",
                    output_padding=(1, 1),
                    activation="elu",
                ),
                tf.keras.layers.Conv2DTranspose(
                    filters=10 * 2,
                    kernel_size=3,
                    strides=2,
                    padding="same",
                    output_padding=(0, 1),
                    activation="elu",
                ),
                tf.keras.layers.Conv2DTranspose(
                    filters=10 * 2,
                    kernel_size=3,
                    strides=2,
                    padding="same",
                    output_padding=(0, 1),
                    activation="elu",
                ),
                tf.keras.layers.Conv2DTranspose(
                    filters=5 * 2,
                    kernel_size=3,
                    strides=2,
                    padding="same",
                    output_padding=(0, 1),
                    activation="elu",
                ),
                tf.keras.layers.Conv2DTranspose(
                    filters=self.specification["nOutputChannels"],
                    kernel_size=3,
                    strides=2,
                    padding="same",
                    output_padding=(0, 1),
                ),
            ]
        )

        # Metrics for training and test loss
        self.train_rmse = tf.Variable(
            tf.zeros([self.specification["nOutputChannels"]]), trainable=False
        )
        self.train_logpz = tf.Variable(0.0, trainable=False)
        self.train_logqz_x = tf.Variable(0.0, trainable=False)
        self.train_loss = tf.Variable(0.0, trainable=False)
        self.test_rmse = tf.Variable(
            tf.zeros([self.specification["nOutputChannels"]]), trainable=False
        )
        self.test_logpz = tf.Variable(0.0, trainable=False)
        self.test_logqz_x = tf.Variable(0.0, trainable=False)
        self.test_loss = tf.Variable(0.0, trainable=False)
        # And regularization loss
        self.regularization_loss = tf.Variable(0.0, trainable=False)

    # Call the encoder model with a batch of input examples and return a batch of
    #  means and a batch of variances of the encoded latent space PDFs.
    def encode(self, x, training=False):
        mean, logvar = tf.split(
            self.encoder(x, training=training), num_or_size_splits=2, axis=1
        )
        return mean, logvar

    # Sample a batch of points in latent space from the encoded means and variances
    def reparameterize(self, mean, logvar, training=False):
        eps = tf.random.normal(shape=mean.shape)
        return eps * tf.exp(logvar * 0.5) + mean

    # Call the generator model with a batch of points in latent space and return a
    #  batch of outputs
    def generate(self, z, training=False):
        generated = self.generator(z, training=training)
        return generated

    # Run the full VAE - convert a batch of inputs to one of outputs
    def call(self, x, training=True):
        mean, logvar = self.encode(x[1], training=training)
        latent = self.reparameterize(mean, logvar, training=training)
        generated = self.generate(latent, training=training)
        return generated

    # Utility function to calculte fit of sample to N(mean,logvar)
    # Used in loss calculation
    def log_normal_pdf(self, sample, mean, logvar, raxis=1):
        log2pi = tf.math.log(2.0 * 3.141592653589793)
        return tf.reduce_sum(
            -0.5 * ((sample - mean) ** 2.0 * tf.exp(-logvar) + logvar + log2pi),
            axis=raxis,
        )

    @tf.function
    def fit_loss(self, generated, target, climatology):
        # Metric is fractional variance reduction compared to climatology
        weights = tf.where(target != 0.0, 1.0, 0.0)  # Missing data zero weighted
        # Keep the last dimension (different variables)
        skill = tf.reduce_sum(
            tf.math.squared_difference(generated, target) * weights, axis=[0, 1, 2]
        ) / tf.reduce_sum(weights, axis=[0, 1, 2])
        guess = tf.reduce_sum(
            tf.math.squared_difference(climatology, target) * weights, axis=[0, 1, 2]
        ) / tf.reduce_sum(weights, axis=[0, 1, 2])
        return skill / guess

    # Calculate the losses from autoencoding a batch of inputs
    # We are calculating a seperate loss for each variable, and for for the
    #  two components of the latent space KLD regularizer. This is useful
    #  for monitoring and debugging, but the weight update only depends
    #  on a single value (their sum).
    @tf.function
    def compute_loss(self, x, training):
        mean, logvar = self.encode(x[1], training=training)
        latent = self.reparameterize(mean, logvar, training=training)
        generated = self.generate(latent, training=training)

        gV = generated
        cV = gV * 0.0 + 0.5  # Climatology
        tV = x[-1]
        fit_metric = self.fit_loss(gV, tV, cV)

        logpz = (
            tf.reduce_mean(self.log_normal_pdf(latent, 0.0, 0.0) * -1)
            * self.specification["beta"]
        )
        logqz_x = (
            tf.reduce_mean(self.log_normal_pdf(latent, mean, logvar))
            * self.specification["beta"]
        )

        regularization = tf.add_n(self.losses)

        return (
            fit_metric,
            logpz,
            logqz_x,
            regularization,
        )

    # Run the autoencoder for one batch, calculate the errors, calculate the
    #  gradients and update the layer weights.
    @tf.function
    def train_on_batch(self, x, optimizer):
        with tf.GradientTape() as tape:
            loss_values = self.compute_loss(x, training=True)
            overall_loss = (
                tf.math.reduce_mean(loss_values[0], axis=0)  # RMSE
                + loss_values[1]  # logpz
                + loss_values[2]  # logqz_x
                + loss_values[3]  # Regularization
            )
        gradients = tape.gradient(overall_loss, self.trainable_variables)
        # Clip the gradients - helps against sudden numerical problems
        if self.specification["maxGradient"] is not None:
            gradients = [
                tf.clip_by_norm(g, self.specification["maxGradient"]) for g in gradients
            ]
        optimizer.apply_gradients(zip(gradients, self.trainable_variables))

    # Update the metrics
    def update_metrics(self, trainDS, testDS):
        self.train_rmse.assign(tf.zeros([self.specification["nOutputChannels"]]))
        self.train_logpz.assign(0.0)
        self.train_logqz_x.assign(0.0)
        self.train_loss.assign(0.0)
        validation_batch_count = 0
        for batch in trainDS:
            per_replica_losses = self.specification["strategy"].run(
                self.compute_loss, args=(batch, False)
            )
            batch_losses = self.specification["strategy"].reduce(
                tf.distribute.ReduceOp.MEAN, per_replica_losses, axis=None
            )
            self.train_rmse.assign_add(batch_losses[0])
            self.train_logpz.assign_add(batch_losses[1])
            self.train_logqz_x.assign_add(batch_losses[2])
            self.train_loss.assign_add(
                tf.math.reduce_mean(batch_losses[0], axis=0)
                + batch_losses[1]
                + batch_losses[2]
                + batch_losses[3]
            )
            validation_batch_count += 1
        self.train_rmse.assign(self.train_rmse / validation_batch_count)
        self.train_logpz.assign(self.train_logpz / validation_batch_count)
        self.train_logqz_x.assign(self.train_logqz_x / validation_batch_count)
        self.train_loss.assign(self.train_loss / validation_batch_count)

        # Same, but for the test data
        self.test_rmse.assign(tf.zeros([self.specification["nOutputChannels"]]))
        self.test_logpz.assign(0.0)
        self.test_logqz_x.assign(0.0)
        self.test_loss.assign(0.0)
        test_batch_count = 0
        for batch in testDS:
            per_replica_losses = self.specification["strategy"].run(
                self.compute_loss, args=(batch, False)
            )
            batch_losses = self.specification["strategy"].reduce(
                tf.distribute.ReduceOp.MEAN, per_replica_losses, axis=None
            )
            self.test_rmse.assign_add(batch_losses[0])
            self.test_logpz.assign_add(batch_losses[1])
            self.test_logqz_x.assign_add(batch_losses[2])
            self.regularization_loss.assign(batch_losses[3])
            self.test_loss.assign_add(
                tf.math.reduce_mean(batch_losses[0], axis=0)
                + batch_losses[1]
                + batch_losses[2]
                + batch_losses[3]
            )
            test_batch_count += 1
        self.test_rmse.assign(self.test_rmse / test_batch_count)
        self.test_logpz.assign(self.test_logpz / test_batch_count)
        self.test_logqz_x.assign(self.test_logqz_x / test_batch_count)
        self.test_loss.assign(self.test_loss / test_batch_count)

    # Save metrics to a log file
    def updateLogfile(self, logfile_writer, epoch):
        with logfile_writer.as_default():
            tf.summary.write(
                "Train_RMSE",
                self.train_rmse,
                step=epoch,
            )
            tf.summary.scalar("Train_logpz", self.train_logpz, step=epoch)
            tf.summary.scalar("Train_logqz_x", self.train_logqz_x, step=epoch)
            tf.summary.scalar("Train_loss", self.train_loss, step=epoch)
            tf.summary.write(
                "Test_RMSE",
                self.test_rmse,
                step=epoch,
            )
            tf.summary.scalar("Test_logpz", self.test_logpz, step=epoch)
            tf.summary.scalar("Test_logqz_x", self.test_logqz_x, step=epoch)
            tf.summary.scalar("Test_loss", self.test_loss, step=epoch)
            tf.summary.scalar(
                "Regularization_loss", self.regularization_loss, step=epoch
            )

    # Print out the current metrics
    def printState(self):
        for i in range(self.specification["nOutputChannels"]):
            print(
                "{:<10s}: {:>9.3f}, {:>9.3f}".format(
                    self.specification["outputNames"][i],
                    self.train_rmse.numpy()[i],
                    self.test_rmse.numpy()[i],
                )
            )
        print(
            "logpz     : {:>9.3f}, {:>9.3f}".format(
                self.train_logpz.numpy(),
                self.test_logpz.numpy(),
            )
        )
        print(
            "logqz_x   : {:>9.3f}, {:>9.3f}".format(
                self.train_logqz_x.numpy(),
                self.test_logqz_x.numpy(),
            )
        )
        print(
            "regularize:            {:>9.3f}".format(
                self.regularization_loss.numpy(),
            )
        )
        print(
            "loss      : {:>9.3f}, {:>9.3f}".format(
                self.train_loss.numpy(),
                self.test_loss.numpy(),
            )
        )


# Load model and initial weights
def getModel(specification, epoch=1):
    # Instantiate the model
    autoencoder = DCVAE(specification)

    # If we are doing a restart, load the weights
    if epoch > 1:
        weights_dir = ("%s/MLP/%s/weights/Epoch_%04d") % (
            os.getenv("SCRATCH"),
            specification["modelName"],
            epoch,
        )
        load_status = autoencoder.load_weights("%s/ckpt" % weights_dir)
        load_status.assert_existing_objects_matched()

    return autoencoder
