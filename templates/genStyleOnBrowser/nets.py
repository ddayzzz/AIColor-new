from keras.layers import Input
from keras.layers.merge import concatenate
from keras.models import Model,Sequential
from keras.engine.topology import Layer
from keras.engine import InputSpec
from keras import backend as K
from VGG16 import VGG16
from keras.layers.merge import add
from keras.layers.core import Activation
from keras.layers import ZeroPadding2D,Lambda
from keras.layers.normalization import BatchNormalization
# import img_util
from keras.layers.convolutional import Conv2D,Cropping2D,UpSampling2D

import tensorflow as tf 

def image_transform_net(img_width,img_height,tv_weight=1):
    x = Input(shape=(img_width,img_height,3))
    a = ZeroPadding2D(padding=(40, 40))(x)
    a = Conv2D(32, (9, 9), strides=(1,1),padding='same')(a)
    a = BatchNormalization()(a)
    a = Activation("relu")(a)
    a = Conv2D(64, (9, 9), strides=(2,2),padding='same')(a)
    a = BatchNormalization()(a)
    a = Activation("relu")(a)
    a = Conv2D(128, (3, 3), strides=(2,2),padding='same')(a)
    a = BatchNormalization()(a)
    a = Activation("relu")(a)

    
    for i in range(5):
        nb_filter = 128
        (nb_row,nb_col) = (3,3)
        stride=(1,1)
        identity = Cropping2D(cropping=((2,2),(2,2)))(a)
        a = Conv2D(nb_filter, (nb_row, nb_col), strides=stride, padding='valid')(a)
        a = BatchNormalization()(a)
        a = Activation("relu")(a)
        a = Conv2D(nb_filter, (nb_row, nb_col), strides=stride, padding='valid')(a)
        y = BatchNormalization()(a)
        a = add([identity, y])

    (nb_row, nb_col) = (3,3)
    stride = (2,2)
    nb_filter = 64
    activation = "relu"
    a = UpSampling2D(size=stride)(a)
    #a = ZeroPadding2D(padding=(32,32))(a) 
    a = ZeroPadding2D(padding=stride)(a)
    a = Conv2D(nb_filter, (nb_row, nb_col), padding='valid')(a)
    a = BatchNormalization()(a)
    a = Activation(activation)(a)

    nb_filter = 32
    
    a = UpSampling2D(size=stride)(a)
    K.print_tensor(a)
    #a = ZeroPadding2D(padding=(65,65))(a)
    a = ZeroPadding2D(padding=stride)(a)
    a = Conv2D(nb_filter, (nb_row, nb_col), padding='valid')(a)
    a = BatchNormalization()(a)
    a = Activation(activation)(a)
    
    (nb_row, nb_col) = (9,9)
    stride = (1,1)
    nb_filter = 3
    activation = "tanh"
    

    a = UpSampling2D(size=stride)(a) 
    a = ZeroPadding2D(padding=stride)(a)
    a = Conv2D(nb_filter, (nb_row, nb_col), padding='valid')(a)
    a = BatchNormalization()(a)
    a = Activation(activation)(a)

    model = Model(inputs=x, outputs=a)  
    return model 



def loss_net(x_in, trux_x_in,width, height,style_image_path,content_weight,style_weight):
    # Append the initial input to the FastNet input to the VGG inputs
    x = concatenate([x_in, trux_x_in], axis=0)
    vgg = VGG16(include_top=False,input_tensor=x)
    return vgg
