import lutorpy as lua
import os


lua.LuaRuntime(zero_based_index=True)


## 导入指定的模块
require('image')
require('nngraph')
require("nn")
require('torch')

netfile = 'genColor/colornet.t7'
netfile_imagenet = 'genColor/colornet_imagenet.t7'

# 模型1
_d = torch.load(netfile)  # 所有需求的包自动导入到全局变量
normal_datamean = _d.mean
normal_model = _d.model._float()
# 模型2
_f = torch.load(netfile_imagenet)
imagenet_datamean = _f.mean
imagenet_model = _f.model._float()


def pred2rgb(x, data):
    # I = torch.cat(data[0][{{1}, {}, {}}]._float(),
    #                                      data[0]._clone()._float()._mul(2)._add(-1), 1)
    I = torch.cat(data[0][lua.table(lua.table(1), lua.table(), lua.table())]._float(),
                  data[0]._clone()._float()._mul(2)._add(-1), 1)
    O = image.scale(I,x._size(3), x._size(2))
    X = image.rgb2lab(image.yuv2rgb(torch.repeatTensor(x, 3, 1, 1)))
    O = O._mul(100)  # 可能有问题
    O[0] = X[0]
    O = image.rgb2yuv(image.lab2rgb(O))
    # return image.yuv2rgb(torch.cat(x, O[{{2, 3}, {}, {}}], 1))
    return image.yuv2rgb(torch.cat(x, O[lua.table(lua.table(2, 3), lua.table(), lua.table())], 1))


def generateColorImage(infile, outfile, modelIndex):
    if modelIndex == 0:
        datamean = normal_datamean
        model = normal_model
    elif modelIndex == 1:
        datamean = imagenet_datamean
        model = imagenet_model
    I = image.load(infile)
    if I._size(1) == 3:
        I = image.rgb2y(I)
    X2 = image.scale(I, torch.round(I._size(3)/8)*8, torch.round(I._size(2)/8)*8 )._add(-datamean)._float()
    X1 = image.scale(X2, 224, 224 )._float()
    X1 = X1._reshape( 1, X1._size(1), X1._size(2), X1._size(3) )
    X2 = X2._reshape( 1, X2._size(1), X2._size(2), X2._size(3) )
    model.forwardnodes[8].data.module.modules[2].nfeatures = X2._size(3)/8
    model.forwardnodes[8].data.module.modules[3].nfeatures = X2._size(4)/8
    preData = model._forward(lua.table(X1, X2))  # https://pypi.org/project/lupa/#lua-tables
    image.save(outfile, pred2rgb(I._float(), preData))
    if not os.path.exists(outfile):
        raise FileNotFoundError('没有找到对应的生成的文件：%s' % outfile)

if __name__ == '__main__':
    # 测试的代码
    generateColorImage('./genColor/test/dog.jpeg', './genColor/test/dog_test_output.jpeg')