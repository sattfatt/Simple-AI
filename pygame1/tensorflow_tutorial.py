import tensorflow as tf
NEURONSPERLAYER = 5



# input vector will be 5 long vector
x = tf.placeholder(tf.float32, [5,1])

# layer 1
w1 = tf.Variable(tf.random_normal([5, NEURONSPERLAYER], 0, 1))
b1 = tf.Variable(tf.random_normal([NEURONSPERLAYER,1], 0, 1))

# layer 2
w2 = tf.Variable(tf.random_normal([NEURONSPERLAYER, NEURONSPERLAYER], 0, 1))
b2 = tf.Variable(tf.random_normal([NEURONSPERLAYER,1], 0, 1))

# layer 3
w3 = tf.Variable(tf.random_normal([NEURONSPERLAYER, 5], 0, 1))
b3 = tf.Variable(tf.random_normal([5, 1], 0, 1))


out1 = tf.nn.tanh(tf.matmul(w1, x) + b1)
out2 = tf.nn.tanh(tf.matmul(w2, out1) + b2)
out3 = tf.nn.tanh(tf.matmul(w3, out2) + b3)





sess = tf.InteractiveSession()
tf.global_variables_initializer().run()

print(sess.run(out3, {x: [[1],[2],[3],[4],[5]]}))