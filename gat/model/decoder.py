import tensorflow as tf

from gat.attention.multi_head_masked_attention import MultiHeadMaskedAttention
from gat.model.preprocessor import Preprocessor
import numpy as np


class Decoder(tf.keras.models.Model):
    def __init__(self, d_model, d_key, n_heads, th_range, weight_balancer=0.01):
        super().__init__()
        if (d_model % n_heads) != 0:
            raise Exception('割り切れる数字を入れてね！！')
        self.d_model = d_model
        self.d_key = d_key
        self.attention = MultiHeadMaskedAttention(
            d_model, d_key, n_heads, weight_balancer)
        self.th_range = th_range
        self.preprocesser = Preprocessor(d_model, d_key, n_heads)
        self.weight_balancer = weight_balancer

    def build(self, input_shape):

        initializer = tf.random_uniform_initializer(
            -np.sqrt(6/(self.d_model + self.d_key)) * self.weight_balancer,
            np.sqrt(6/(self.d_model + self.d_key)) * self.weight_balancer
        )

        self.wq = self.add_weight(name="wq", shape=(self.d_model, self.d_key),
                                  initializer=initializer,
                                  trainable=True)

        self.wk = self.add_weight(name="wk", shape=(self.d_model, self.d_key),
                                  initializer=initializer,
                                  trainable=True)

    def masked_softmax(self, inputs):
        Q, K, mask = inputs
        divide_const = tf.sqrt(tf.cast(tf.constant(K.shape[-1]), tf.float32))
        QK = tf.matmul(Q, K, transpose_b=True)
        shape = tf.shape(QK)
        QK = tf.reshape(QK, (shape[1], shape[0], shape[-1]))

        masked_QK = tf.reshape(tf.where(mask, tf.float32.min, QK), shape)

        return tf.nn.softmax(self.th_range *
                             tf.keras.activations.tanh(tf.divide(masked_QK, divide_const)))

    @tf.function
    def call(self, inputs, training=None):
        '''
        inputs ===[H (BATCH_SIZE, n_nodes, d_model), trajectory(BATCH_SIZE, n_nodes)]
        outputs === (BATCH_SIZE, n_nodes)
        '''
        inputs = self.preprocesser(inputs)
        output = self.attention(inputs)
        return self.masked_softmax([tf.matmul(output, self.wq), tf.matmul(
            inputs[0], self.wk), inputs[2]])
