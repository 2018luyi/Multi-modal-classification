import os

import tensorflow as tf
from tflearn.data_utils import pad_sequences

from BestDataHelperEverCreated import BestDataHelperEverCreated
from dataManagement.DataLoader import DataLoader
from parameterManager.TrainingParameters import TrainingParameters
from trainer.ModelTrainer import ModelTrainer

tf.flags.DEFINE_integer("embedding_dim", 128, "Dimensionality of character embedding (default: 128)")
tf.flags.DEFINE_string("filter_sizes", "3,4,5", "Comma-separated filter sizes (default: '3,4,5')")
tf.flags.DEFINE_integer("num_filters", 128, "Number of filters per filter size (default: 128)")
tf.flags.DEFINE_float("dropout_keep_prob", 0.5, "Dropout keep probability (default: 0.5)")
tf.flags.DEFINE_float("l2_reg_lambda", 0.0, "L2 regularization lambda (default: 0.0)")

tf.flags.DEFINE_integer("batch_size", 32, "Batch Size (default: 64)")
tf.flags.DEFINE_integer("num_epochs", 200, "Number of training epochs (default: 200)")
tf.flags.DEFINE_integer("evaluate_every", 500, "Evaluate model on dev set after this many steps (default: 100)")
tf.flags.DEFINE_integer("num_checkpoints", 1, "Number of checkpoints to store (default: 5)")
tf.flags.DEFINE_integer("patience", 100, "Stop criteria (default: 100)")
tf.flags.DEFINE_integer("output_image_width", 100, "Size of output Image plus embedding  (default: 100)")
tf.flags.DEFINE_integer("encoding_height", 10, "Height of the output embedding  (default: 10)")

tf.flags.DEFINE_string("train_path", "/home/superior/tmp/test-accuracy/train.csv",
                       "csv file containing text|class|image_path")
tf.flags.DEFINE_string("val_path", "/home/superior/tmp/test-accuracy/test.csv",
                       "csv file containing text|class|image_path")
tf.flags.DEFINE_string("save_model_dir_name", "/home/superior/tmp/test-accuracy/food101-100-10",
                       "dir used to save the model")

tf.flags.DEFINE_string("gpu_id", "0", "ID of the GPU to be used")

FLAGS = tf.flags.FLAGS

os.environ['CUDA_VISIBLE_DEVICES'] = FLAGS.gpu_id


def main():
    num_words_to_keep = 30000
    num_words_x_doc = 100

    output_image_width = FLAGS.output_image_width
    encoding_height = FLAGS.encoding_height

    parameters = TrainingParameters(num_words_to_keep, output_image_width, encoding_height, FLAGS.patience,
                                    FLAGS.dropout_keep_prob, FLAGS.embedding_dim, FLAGS.batch_size, FLAGS.filter_sizes,
                                    FLAGS.num_filters)

    data_helper = BestDataHelperEverCreated(parameters.get_no_of_words_to_keep(), FLAGS.save_model_dir_name)

    data_loader = DataLoader()
    data_loader.load_data(FLAGS.train_path, FLAGS.val_path, delimiter='|', shuffle_data=True)

    training_data = data_loader.get_training_data()
    val_data = data_loader.get_val_data()

    data_helper.train_one_hot_encoder(training_data.get_labels())
    train_y = data_helper.labels_to_one_hot(training_data.get_labels())
    val_y = data_helper.labels_to_one_hot(val_data.get_labels())

    data_helper.train_tokenizer(training_data.get_texts())

    train_x = data_helper.texts_to_indices(training_data.get_texts())
    val_x = data_helper.texts_to_indices(val_data.get_texts())

    train_x = pad_sequences(train_x, maxlen=num_words_x_doc, value=0.)
    val_x = pad_sequences(val_x, maxlen=num_words_x_doc, value=0.)

    data_loader.set_training_data(train_x, train_y, training_data.get_images())
    data_loader.set_val_data(val_x, val_y, val_data.get_images())

    trainer = ModelTrainer(data_loader.get_training_data(), data_loader.get_val_data(), parameters)
    trainer.train()


if __name__ == '__main__':
    main()