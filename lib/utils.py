#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import base64
import io
import matplotlib.image as mpimg
import numpy as np

def png2rgb(b64png):
    b = base64.b64decode(b64png)
    i = io.BytesIO(b)
    img = mpimg.imread(i, format='PNG')
    # # Pretty slow
    # img = Image.open(i)
    # i = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)
    return img

def rgb2gray(rgb):
    return np.dot(rgb[..., :3], [0.299, 0.587, 0.114]).clip(0, 255).round().astype(np.uint8)

class Recorder():
    def __init__(self):
        self.buffer = []

    def add(self, frame):
        self.buffer.append(frame)

    def save(self, file):
        # command = 'ffmpeg -framerate 30 -i recording_temp/temp_%%06d.jpg -r 30 -pix_fmt yuv420p %s' % (name)
        # print(command)
        # system(command)

        ext = file.rsplit('.', 1)[1]
        fourcc = ''
        if ext == 'mp4':
            fourcc = 'MP4V'
        elif ext == 'avi':
            fourcc = 'MJPG'
            # fourcc = 'XVID'
        else:
            assert False, 'Please save the video as ".mp4" or ".avi" format.'

        import cv2 
        size = self.buffer[0].shape[1::-1] # shape (300, 400, 4) -> size (400, 300)
        writer = cv2.VideoWriter(file, cv2.VideoWriter_fourcc(*fourcc), 25, size, True)
        for img in self.buffer:
            img = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2RGB)
            writer.write(img) 
        # cv2.destroyAllWindows()
        writer.release()
        
    def clear(self):
        self.buffer = []

def print_and_save(msg, file):
    print(msg)
    with open(file, 'a') as f:
        f.write('{0}\n'.format(msg))

""" Visualizing Conv Layer """
# https://medium.com/@awjuliani/visualizing-neural-network-layer-activation-tensorflow-tutorial-d45f8bf7bbc4

def get_activations(sess, layer, input, stimuli, title=None, save=None):
    units = sess.run(layer, feed_dict={input: np.expand_dims(stimuli, axis=0)})
    plot_NN_filter(units, title, save)

def plot_NN_filter(units, title=None, save=None):
    import matplotlib.pyplot as plt
    import math

    filters = units.shape[3]
    plt.figure(1, figsize=(20,20))
    n_columns = 6
    n_rows = math.ceil(filters / n_columns) + 1
    # print(filters, n_columns, n_rows)
    for i in range(filters):
        plt.subplot(n_rows, n_columns, i+1)
        plt.title('Filter ' + str(i))
        plt.imshow(units[0,:,:,i], interpolation="nearest", cmap="gray")
        # print(units[0,:,:,i].shape)
    if title is not None:
        plt.suptitle(title)
    if save:
        plt.savefig(save)
    else:
        plt.show()