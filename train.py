import os
import tensorflow as tf
from tensorflow.keras.callbacks import ReduceLROnPlateau

import config
import models
from dataprep import generate_train_dataset

def get_model(model_name, input_shape, num_classes, optimizer_fn):
 
    if model_name == "cnn":
        model = models.CNN(input_shape, num_classes)
    elif model_name == "alexnet":
        model = models.AlexNet(input_shape, num_classes)
    elif model_name == "resnet":
        model = models.Resnet(input_shape, num_classes)
    elif model_name == "inceptionv1":
        model = models.InceptionNet(input_shape, num_classes, num_filters=64, problem_type="Classification", dropout_rate=0.4)
    elif model_name == "inceptionv2":
        model = models.Inception(input_shape, num_filters=32, problem_type="Classification", output_nums=num_classes, pooling='avg', dropout_rate=False, auxilliary_outputs=False).Inception_v2()
    elif model_name == "inceptionv3":
        model = models.Inception(input_shape, num_filters=64, problem_type="Classification", output_nums=num_classes, pooling='avg', dropout_rate=False, auxilliary_outputs=False).Inception_v3()
    elif model_name == "inceptionv4":
        model = models.Inception(input_shape, num_filters=64, problem_type="Classification", output_nums=num_classes, pooling='avg', dropout_rate=False, auxilliary_outputs=False).Inception_v4()
    # model.summary()
    if optimizer_fn == 'sgd':
        optimizer = tf.keras.optimizers.SGD(config.learning_rate, config.momentum)
    elif optimizer_fn == 'adam':
        optimizer = tf.keras.optimizers.Adam(config.learning_rate, config.momentum)
    elif optimizer_fn == 'rmsprop':
        optimizer = tf.keras.optimizers.RMSprop(config.learning_rate, config.momentum)
    else:
        print("add another optimizer")
    
    model.compile(optimizer= optimizer,
                    loss='categorical_crossentropy',
                    metrics=['accuracy'])
  

    return model

if __name__ == '__main__':
    # GPU settings
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)

    # load configs and resolve paths
    train_data_config = (config.train_dir, config.valid_dir, config.image_height, config.image_width, config.TRAIN_BATCH_SIZE, config.VALID_BATCH_SIZE)
    print(train_data_config)
    result_save_path = os.path.join(config.result_dir, config.model)
    if not os.path.exists(result_save_path):
        os.mkdir(result_save_path)
    log_dir = os.path.join(result_save_path, "logs_{}".format(config.version))
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    # get the original_dataset
    train_dataset, valid_dataset = generate_train_dataset(train_data_config)
    print(config.optimizer_fn)
    # create model
    model = get_model(config.model, (config.image_height, config.image_width, config.num_channels), config.num_classes, config.optimizer_fn)
    
    # set the callbacks
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir)

    rlrop = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=10)

    callback_list = [rlrop, tensorboard_callback]

    # start training
    model.fit(train_dataset,
                epochs= config.EPOCHS,
                steps_per_epoch= train_dataset.samples // config.TRAIN_BATCH_SIZE,
                validation_data=valid_dataset,
                validation_steps= valid_dataset.samples // config.TEST_BATCH_SIZE,
                callbacks=callback_list,
                verbose=1)

    # save model
    if config.data == "DogvCat":
        model_name="{}_{}_dogcat".format(config.model, config.version)
    elif config.data == "mnist":
        model_name="{}_{}_mnist".format(config.model, config.version)    
    
    model_save_path = os.path.join(result_save_path, model_name)
    model.save(model_save_path)
