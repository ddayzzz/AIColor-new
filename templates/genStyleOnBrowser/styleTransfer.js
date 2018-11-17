async function tf_loadModel(path) {
    let model = await tf.loadModel(path);
    return model;
}


function tf_changeImageSize(img) {
    // 调整大小
    // const [bs, height, width, channel] = img.shape;
    // var ratio = width / height;

    // sw = parseInt(width / 4) * 4; // 满足 4 的倍数
    // sh = parseInt(height / 4) * 4;
    // size = sw > sh ? sw : sh;
    // pad_w = parseInt((size - sw) / 2);
    // pad_h = parseInt((size - sh) / 2);

    // kvar = tf.variable(img);

    // padings = [[0,0], [pad_w, pad_w], [pad_h, pad_h], [0, 0]];

    // squared_img = tf.pad(kvar, padings);
    img = tf.image.resizeNearestNeighbor(img, [256, 256]).asType('float32');
    console.log(img.shape);

    // x = tf.variable(paded_tensor);


    return img;
}
function tf_deprocess(x) {

    return tf.tidy(() => {

        const offset = tf.scalar(127.5);
        // 图片标准化
        const denormalized = x.mul(offset).add(offset).toInt();
        const reduced = denormalized.squeeze()
        return reduced
    })
}
function tf_preprocess(imgData) {
    return tf.tidy(() => {
        let tensor = tf.fromPixels(imgData).toFloat();

        const offset = tf.scalar(127.5);
        // 图片标准化
        const normalized = tensor.sub(offset).div(offset);

        // 一批图像数据。在 tensorflow 中 BATCH_SIZE 部分
        const batched = normalized.expandDims(0)
        return batched;
    })
}


function tf_toPixels(tensor, canvas) {
    const ctx = canvas.getContext('2d');
    const [height, width] = tensor.shape;

    const buffer = new Uint8ClampedArray(width * height * 4)
    const imageData = new ImageData(width, height);
    const data = tensor.dataSync();
    var cnt = 0;
    for (var y = 0; y < height; y++) {
        for (var x = 0; x < width; x++) {
            var pos = (y * width + x) * 4; // position in buffer based on x and y
            buffer[pos] = data[cnt]           // some R value [0, 255]
            buffer[pos + 1] = data[cnt + 1]           // some G value
            buffer[pos + 2] = data[cnt + 2]           // some B value
            buffer[pos + 3] = 255;           // set alpha channel
            cnt += 3
        }
    }
    imageData.data.set(buffer)
    canvas.width = width;
    canvas.height = height;
    ctx.putImageData(imageData, 0, 0);
    return imageData;
}

var styleImageApp = new Vue({
    el: '#style-changer-app',
    delimiters: ['{[', ']}'],
    data: {
        model: null,  // 加载的模型
        modelJsonUrl: null,
        imageObj: null,
        generated: null,
        dataUrl: ''
    },
    computed: {
        toDisableProceeBtn: function () {
            return this.imageObj ? false : true;
        },
        downloadLink: function(){
            return this.dataUrl;
        }
    },
    methods: {
        changeSelectedImageFile: async function (event) {
            var that = this;
            event.preventDefault();
            if (this.$refs.localImageFile.files && this.$refs.localImageFile.files.length == 1) {
                selectedImage = this.$refs.localImageFile.files[0];

                var canvsObj = document.getElementById('canvasLocalImage');
                var ctx = canvsObj.getContext('2d')
                    , img = new Image()
                    , f = selectedImage
                    , url = window.URL || window.webkitURL
                    , src = url.createObjectURL(f);

                ctx.clearRect(0, 0, 256, 256);
                img.src = src;
                img.onload = function () {
                    that.imageObj = img;

                    canvsObj.width = 256;
                    canvsObj.height = 256;
                    ctx.drawImage(img, 0, 0, 256, 256);
                    url.revokeObjectURL(src);
                }
            }
        },
        getStyledImage: function () {
            if (this.imageObj == null) {
                console.error("请选择一张图片");
                return;
            }
            if (this.model == null) {
                console.error("请等待模型加载完成");
                return;
            }
            var canvas = document.getElementById('canvasProcessedImage');
            var cImg = this.imageObj;
            var cT = tf_preprocess(cImg);
            const model = this.model;
            z = model.predict(tf_changeImageSize(cT));
            imgData = tf_toPixels(tf_deprocess(z), canvas)
            console.log('风格化成功');
            this.generated = imgData;
        },
        saveToFile: function () {
            var canvas = document.getElementById('canvasProcessedImage');
            var dt = canvas.toDataURL('image/jpeg').replace("image/jpeg", "image/octet-stream");;
            this.dataUrl = dt;
        },
        upload: function(){
            // 将处理的结果发送到服务器上
            
        }
    },
    mounted: async function () {
        this.$nextTick(function () {
            this.modelJsonUrl = document.getElementById('style-changer-app').getAttribute('modelJsonUrl');
            var that = this;
            tf_loadModel(this.modelJsonUrl)
                .then(function (model) {
                    that.model = model;
                })
                .catch(function (error) {
                    console.error('加载模型出错:', error);
                })

        });
    }
});