# py-truchet-gan
A generative adversarial network to generate Truchet tiling images

## Installing requirements in virtual environment

After creating/activating the virtual environment:

```shell
pip install -r requirements.txt
```

## Generating training set

The training set is generated using the script augment_dataset.py:

```shell
python augment_dataset.py
```

Training images are generated in folder "imgs/train".

## Train the GAN

To train the GAN, lauch:

```shell
python tf_truchet_gan.py
```

### Accessing Tensorboard

Launch Tensorboard server and follow on-screen instructions:

```shell
tensorboard --logdir logs
```

### Using saved model weights

If weights are already available, comment the following two lines in tf_truchet_gan.py:

```shell
train(train_dataset, EPOCHS)
make_animation()
```

and launch the script again to generate a new set of images:

```shell
python tf_truchet_gan.py
```