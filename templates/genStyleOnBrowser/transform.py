from keras.layers import Input, merge
from keras.models import Model,Sequential
from keras.preprocessing.image import ImageDataGenerator
from keras import backend as K
from scipy.misc import imsave
from keras.layers.merge import concatenate
import time
import numpy as np 
import argparse
import h5py
import tensorflow as tf
from scipy import ndimage
from VGG16 import VGG16
import nets
from scipy.misc import imread, imresize, imsave, fromimage, toimage
from sklearn.feature_extraction.image import reconstruct_from_patches_2d, extract_patches_2d
from PIL import Image
import numpy as np
import os
from keras.preprocessing import image

def preprocess_reflect_image(image_path, size_multiple=4):
    img = imread(image_path, mode="RGB")  # Prevents crashes due to PNG images (ARGB)
    org_w = img.shape[0]
    org_h = img.shape[1]

    aspect_ratio = org_h/org_w
    
    sw = (org_w // size_multiple) * size_multiple # Make sure width is a multiple of 4
    sh = (org_h // size_multiple) * size_multiple # Make sure width is a multiple of 4


    size  = sw if sw > sh else sh

    pad_w = (size - sw) // 2
    pad_h = (size - sh) // 2

    tf_session = K.get_session()
    kvar = K.variable(value=img)

    paddings = [[pad_w,pad_w],[pad_h,pad_h],[0,0]]
    squared_img = tf.pad(kvar,paddings, mode='REFLECT', name=None)
    img = K.eval(squared_img)

    
    img = imresize(img, (size, size),interp='nearest')
    img = img.astype(np.float32)

    img = np.expand_dims(img, axis=0)
    img = img /255.
    return (aspect_ratio  ,img)

def load_weights(model,file_path):
    f = h5py.File(file_path)

    layer_names = [name for name in f.attrs['layer_names']]

    for i, layer in enumerate(model.layers[:31]):
        g = f[layer_names[i]]
        weights = [g[name] for name in g.attrs['weight_names']]
        layer.set_weigh
        ts(weights)

    f.close()
    
    print('Pretrained Model weights loaded.')

def main(args):
    style= args.style
    #img_width = img_height =  args.image_size
    output_file =args.output
    input_file = args.input
    original_color = args.original_color
    blend_alpha = args.blend
    media_filter = args.media_filter

    aspect_ratio, x = preprocess_reflect_image(input_file, size_multiple=4)

    img_width  = x.shape[1]
    img_height = x.shape[2]

    net = nets.image_transform_net(img_width,img_height)
    z = concatenate([net.output, net.input], axis=0)
    model = VGG16(include_top=False,input_tensor=z)
    #model.summary()

    #model.compile(Adam(),  dummy_loss)  # Dummy loss since we are learning from regularizes

    model.load_weights("pretrained/"+style+'_weights.h5',by_name=False)

    
    t1 = time.time()
    y = net.predict(x)[0] 

    print("process: %s" % (time.time() -t1))

    imsave('%s_output.png' % output_file, y)
    net.save('keras.h5')    
 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Real-time style transfer')

    parser.add_argument('--style', '-s', type=str, required=True,
                        help='style image file name without extension')

    parser.add_argument('--input', '-i', default=None, required=True,type=str,
                        help='input file name')

    parser.add_argument('--output', '-o', default=None, required=True,type=str,
                        help='output file name without extension')

    parser.add_argument('--original_color', '-c', default=0, type=float,
                        help='0~1 for original color')

    parser.add_argument('--blend', '-b', default=0, type=float,
                        help='0~1 for blend with original image')

    parser.add_argument('--media_filter', '-f', default=3, type=int,
                        help='media_filter size')
    parser.add_argument('--width', default=256, type=int)
    parser.add_argument('--height', default=256, type=int)
    args = parser.parse_args()
    main(args)
