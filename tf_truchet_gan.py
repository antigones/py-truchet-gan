import tensorflow as tf
import glob
import imageio
import matplotlib.pyplot as plt
import numpy as np
import os
import PIL
from tensorflow.keras import layers
from tensorflow.keras.callbacks import TensorBoard
import time
from PIL import Image
from matplotlib import pyplot

def read_images(dir):
    working_dir = os.curdir + dir
    out = []
    for filename in os.listdir(working_dir):
        with open(working_dir+filename, 'r'): # open in readonly mode
            img = imageio.imread(working_dir+filename)
            out.append(np.asarray(img))
    return np.asarray(out)

def make_animation():
  anim_file = './output_gan/dcgan.gif'
  from skimage.transform import resize
  with imageio.get_writer(anim_file, mode='I') as writer:
    filenames = glob.glob('./output_gan/image*.png')
    filenames = sorted(filenames)
    for filename in filenames:
      image = imageio.imread(filename)
      image = resize(image, (256, 256), order=0)
      writer.append_data(image)

def plot_history(d1_hist, d2_hist, g_hist):
	# plot loss
	pyplot.subplot(2, 1, 1)
	pyplot.plot(d1_hist, label='d-real')
	pyplot.plot(d2_hist, label='d-fake')
	pyplot.plot(g_hist, label='gen')
	pyplot.legend()
	pyplot.savefig('plot_line_plot_loss.png')
	pyplot.close()

size = 32

train_images = read_images("/imgs/train/")
train_images = train_images.reshape(train_images.shape[0], size, size, 1).astype('float32')
train_images = (train_images - 127.5) / 127.5  # Normalize the images to [-1, 1]


EPOCHS = 300
BUFFER_SIZE = 1000
BATCH_SIZE = 128

# Batch and shuffle the data
train_dataset = tf.data.Dataset.from_tensor_slices(train_images).shuffle(BUFFER_SIZE).batch(BATCH_SIZE)

def make_generator_model():
    model = tf.keras.Sequential()
    
    model.add(layers.Dense(8*8*256, use_bias=False, input_shape=(100,))) # 8x8
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())

    model.add(layers.Reshape((8, 8, 256))) 
    assert model.output_shape == (None, 8, 8, 256)  # Note: None is the batch size

    model.add(layers.Conv2DTranspose(128, (5, 5), strides=(1, 1), padding='same', use_bias=False)) # 8x8
    assert model.output_shape == (None, 8, 8, 128)
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())

    model.add(layers.Conv2DTranspose(64, (5, 5), strides=(2, 2), padding='same', use_bias=False)) # 16x16
    assert model.output_shape == (None, 16, 16, 64)
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())

    model.add(layers.Conv2DTranspose(1, (5, 5), strides=(2, 2), padding='same', use_bias=False, activation='tanh')) # 32x32
    assert model.output_shape == (None, size, size, 1)

    return model

generator = make_generator_model()

noise = tf.random.normal([1, 100])
generated_image = generator(noise, training=False)

plt.imshow(generated_image[0, :, :, 0], cmap='gray')


def make_discriminator_model():
    model = tf.keras.Sequential()
    model.add(layers.Conv2D(64, (5, 5), strides=(2, 2), padding='same',
                                     input_shape=[size, size, 1]))
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))

    model.add(layers.Conv2D(128, (5, 5), strides=(2, 2), padding='same'))
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))

    model.add(layers.Flatten())
    model.add(layers.Dense(1))

    return model

discriminator = make_discriminator_model()
decision = discriminator(generated_image)

# This method returns a helper function to compute cross entropy loss
cross_entropy = tf.keras.losses.BinaryCrossentropy(from_logits=True)

def discriminator_loss(real_output, fake_output):
    # how well the discriminator is able to distinguish real images from fakes
    # fake_output: fake outputs, for the discriminator
    # real_output: real outputs, for the discriminator
    # real loss: real outputs for the discriminator vs real image (from training set)
    # fake_loss: fake outputs for the discriminator vs generated images
    real_loss = cross_entropy(tf.ones_like(real_output), real_output)
    fake_loss = cross_entropy(tf.zeros_like(fake_output), fake_output)
    total_loss = real_loss + fake_loss
    return total_loss

def generator_loss(fake_output):
    # the ability of the generator to produce realistic images
    g_loss = cross_entropy(tf.ones_like(fake_output), fake_output)
    return g_loss

generator_optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
discriminator_optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)

checkpoint_dir = './gan_training_checkpoints'
checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
checkpoint = tf.train.Checkpoint(generator_optimizer=generator_optimizer,
                                 discriminator_optimizer=discriminator_optimizer,
                                 generator=generator,
                                 discriminator=discriminator)


noise_dim = 100
num_examples_to_generate = 16

# You will reuse this seed overtime (so it's easier)
# to visualize progress in the animated GIF)
seed = tf.random.normal([num_examples_to_generate, noise_dim])

# Notice the use of `tf.function`
# This annotation causes the function to be "compiled".
@tf.function
def train_step(images):
    noise = tf.random.normal([BATCH_SIZE, noise_dim])

    with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:
      generated_images = generator(noise, training=True)

      real_output = discriminator(images, training=True)
      fake_output = discriminator(generated_images, training=True)

      gen_loss = generator_loss(fake_output)
      disc_loss = discriminator_loss(real_output, fake_output)
      total_loss = gen_loss + disc_loss

    gradients_of_generator = gen_tape.gradient(gen_loss, generator.trainable_variables)
    gradients_of_discriminator = disc_tape.gradient(disc_loss, discriminator.trainable_variables)

    generator_optimizer.apply_gradients(zip(gradients_of_generator, generator.trainable_variables))
    discriminator_optimizer.apply_gradients(zip(gradients_of_discriminator, discriminator.trainable_variables))

    return gen_loss, disc_loss, total_loss

def generate_and_save_images(model, epoch, test_input):
  # Notice `training` is set to False.
  # This is so all layers run in inference mode (batchnorm).
  predictions = model(test_input, training=False)
  # print(np.asarray(predictions[0, :, :, 0] * 127.5 + 127.5))
  im = Image.fromarray(np.asarray(predictions[0, :, :, 0] * 127.5 + 127.5))
  if im.mode != 'L':
    im = im.convert('L')
    imageio.imsave('./output_gan/image_at_epoch_{:04d}.png'.format(epoch), im)

def refine_image(pred):
  threshold = 250
  output = pred.copy()
  output[output>threshold] = 255
  output[output<=threshold] = 0
  img = Image.fromarray(output)
  return img

def train(dataset, epochs):
  writer = tf.summary.create_file_writer(log_path)
  for epoch in range(epochs):
    start = time.time()

    for i, image_batch in enumerate(dataset):
      gen_loss, disc_loss, tot_loss = train_step(image_batch)
      with writer.as_default():
        tf.summary.scalar('gen_loss', gen_loss, step=epoch)
        tf.summary.scalar('disc_loss', disc_loss, step=epoch) 
        tf.summary.scalar('total_loss', gen_loss+disc_loss, step=epoch)
  
      writer.flush()

    # Produce images for the GIF as you go
    # display.clear_output(wait=True)
      generate_and_save_images(generator,
                              epoch + 1,
                              seed)

    # Save the model every 15 epochs
    if (epoch + 1) % 15 == 0:
      checkpoint.save(file_prefix = checkpoint_prefix)

    print ('Time for epoch {} is {} sec'.format(epoch + 1, time.time()-start))

  # Generate after the final epoch
  # display.clear_output(wait=True)
    generate_and_save_images(generator,
                            epochs,
                            seed)

log_path = './logs'
# create the file writer object
# tensorboard --logdir logs


train(train_dataset, EPOCHS)
make_animation()
checkpoint.restore(tf.train.latest_checkpoint(checkpoint_dir))

# feed random image into generator
N_GEN_IMAGES = 50
for i in range(N_GEN_IMAGES):
  noise = tf.random.normal([1, 100])
  generated_image = generator(noise, training=False)
  pred = np.asarray(generated_image[0, :, :, 0] * 127.5 + 127.5)
  im = Image.fromarray(pred)
  # im = refine_image(pred)
  if im.mode != 'L':
    im = im.convert('L')
  imageio.imsave('./output/generated'+str(i)+'.png', im)

# Display a single image using the epoch number
def display_image(epoch_no):
  return PIL.Image.open('./output_gan/image_at_epoch_{:04d}.png'.format(epoch_no))

# display_image(EPOCHS)





