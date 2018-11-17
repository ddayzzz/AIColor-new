// 获取 url 参数中的 key name 的值
function getQueryString(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) return unescape(r[2]); return null;
}

var colorImageApp = new Vue({
    el: '#colored-images-page',
    delimiters: ['{[', ']}'],
    data: {
        'selectedModel': '',
        'imageId': null, // 原图ID
        'imageSrcIndex': null, // 原图的信息
        'status': 'no-select', // 状态：no-select 未选择;processing 已经提交需求，用户可以编辑帖子等信息; finished：完成; failed: 处理过程出现了偏差
        'postTitle': '',
        'postRequire': true,
        'returnImageData': null, // 返回的结果。用于判断是否是 cached
        'imgSrcIndex': '2' // 彩色化，返回的结果
    },
    methods:{
        selectModel: function(modelName){
            this.selectedModel = modelName;
            this.status = 'processing';
            this.processImage();
        },
        processImage: function(){
            // 将当前的文件提交处理
            // 提交并修改状态
            var that = this;
            this.returnImageData = null;
            this.status = "processing";
            console.log('Processing...');
            axios.get('/api/v1/getColorized', {params: { originalImageId: this.imageId, colorizedModel: this.selectedModel, originalImageIndex: this.imageSrcIndex}})
            .then(function(rp){
                var json_response = rp.data;
                if (json_response.status == 0) {
                    // 正常的情况
                    if(json_response.data.cached){
                        console.log("Finished, used cached");
                    }else{
                        console.log("Finished, used newly created");
                    }
                    that.returnImageData = json_response.data;
                    that.status = "finished";
                }else{
                    // 出错，属于服务器本身的错误
                    console.error('Falied:' + json_response.data.messages);
                    that.status = 'failed';
                }
            })
            .catch(function(error){
                // 出错误。通信之间的故障
                console.error('Falied:' + error.status);
                that.status = 'failed';
            });
        },
        processPostAfterFinished: function(){
            var that = this;
            // 当处理的完成之后，确认是否插入新的帖子
            if(this.status != 'finished'){
                console.error('Only accept status: finish instead of ' + this.status);
                return;
            }
            if(this.returnImageData == null || this.returnImageData.postId != null){
                console.error('Invalid image object or existed post');
                return;
            }
            if(this.postTitle.length > 0 && this.postTitle.length <= 200){
                // 合法的帖子标题
                axios.post('/api/v1/createPost',{
                    imgSrcIndex: that.imgSrcIndex, imgId: that.returnImageData.imageId, title: that.postTitle
                })
                .then(function(rp){
                    var json_response = rp.data;
                    if (json_response.status == 0) {
                        alert("提交成功!");
                        console.log('Server: ' + json_response.data.postInfo);
                        // 这里直接修改属性
                        that.returnImageData.postId = json_response.data.postInfo.postId;
                    }
                })
                .catch(function(error){
                    if(error.status == 403){
                        alert('无法创建帖子。请您先登录');
                    }else{
                        alert('无法创建帖子：' + error.status);
                    }
                });
            }else{
                alert('请输入合法的标题');
            } 
        },
        viewPost: function(){
            if(this.returnImageData && this.returnImageData.postId){
                window.open('/viewPost?postId=' + this.returnImageData.postId);
            }
        }
    },
    computed: {
        toDisableFinishBtn: function(){
            // 是否已经存在相同的图片（不允许再次处理上传和发帖）
            if(this.returnImageData !=null && this.returnImageData.postId != null){
                return true;// 关闭
            }
            // 是否处理完
            if(this.status != 'finished'){
                return true;
            }
            // 验证显示的结果
            if(!this.postRequire){
                // 不要发帖子
                return true;
            }
            return false;
        },
        getProcessedImageSrcInCss: function(){
            if(this.returnImageData && this.status == 'finished'){
                return 'background-image: url(\'/api/v1/getImage?imageId=' + this.returnImageData.imageId + '&imageSource=' + this.imgSrcIndex + '\');'
            }
        }
    },
    mounted: function () {
        this.$nextTick(function () {
            this.imageId = getQueryString('imageId');
            this.imageSrcIndex = getQueryString('imageSrcIndex')
        });
    }
})

// 这个目前还无法复用。主要是模型不好做判断
var styleImageApp = new Vue({
    el: '#styled-images-page',
    delimiters: ['{[', ']}'],
    data: {
        'selectedModel': '',
        'imageId': null, // 原图ID
        'imageSrcIndex': null, // 原图的信息
        'status': 'no-select', // 状态：no-select 未选择;processing 已经提交需求，用户可以编辑帖子等信息; finished：完成; failed: 处理过程出现了偏差
        'postTitle': '',
        'postRequire': true,
        'returnImageData': null, // 返回的结果。用于判断是否是 cached
        'imgSrcIndex': '1' // 风格化，返回的结果
    },
    methods:{
        selectModel: function(modelName){
            this.selectedModel = modelName;
            this.status = 'processing';
            this.processImage();
        },
        processImage: function(){
            // 将当前的文件提交处理
            // 提交并修改状态
            var that = this;
            this.returnImageData = null;
            this.status = "processing";
            console.log('Processing...');
            axios.get('/api/v1/getStyled', {params: { originalImageId: this.imageId, styledModel: this.selectedModel, originalImageIndex: this.imageSrcIndex}})
            .then(function(rp){
                var json_response = rp.data;
                if (json_response.status == 0) {
                    // 正常的情况
                    if(json_response.data.cached){
                        console.log("Finished, used cached");
                    }else{
                        console.log("Finished, used newly created");
                    }
                    that.returnImageData = json_response.data;
                    that.status = "finished";
                }else{
                    // 出错，属于服务器本身的错误
                    console.error('Falied:' + json_response.data.messages);
                    that.status = 'failed';
                }
            })
            .catch(function(error){
                // 出错误。通信之间的故障
                console.error('Falied:' + error.status);
                that.status = 'failed';
            });
        },
        processPostAfterFinished: function(){
            var that = this;
            // 当处理的完成之后，确认是否插入新的帖子
            if(this.status != 'finished'){
                console.error('Only accept status: finish instead of ' + this.status);
                return;
            }
            if(this.returnImageData == null || this.returnImageData.postId != null){
                console.error('Invalid image object or existed post');
                return;
            }
            if(this.postTitle.length > 0 && this.postTitle.length <= 200){
                // 合法的帖子标题
                axios.post('/api/v1/createPost',{
                    imgSrcIndex: that.imgSrcIndex, imgId: that.returnImageData.imageId, title: that.postTitle
                })
                .then(function(rp){
                    var json_response = rp.data;
                    if (json_response.status == 0) {
                        alert("提交成功!");
                        console.log('Server: ' + json_response.data.postInfo);
                        // 这里直接修改属性
                        that.returnImageData.postId = json_response.data.postInfo.postId;
                    }
                })
                .catch(function(error){
                    if(error.status == 403){
                        alert('无法创建帖子。请您先登录');
                    }else{
                        alert('无法创建帖子：' + error.status);
                    }
                });
            }else{
                alert('请输入合法的标题');
            } 
        },
        viewPost: function(){
            if(this.returnImageData && this.returnImageData.postId){
                window.open('/viewPost?postId=' + this.returnImageData.postId);
            }
        }
    },
    computed: {
        toDisableFinishBtn: function(){
            // 是否已经存在相同的图片（不允许再次处理上传和发帖）
            if(this.returnImageData !=null && this.returnImageData.postId != null){
                return true;// 关闭
            }
            // 是否处理完
            if(this.status != 'finished'){
                return true;
            }
            // 验证显示的结果
            if(!this.postRequire){
                // 不要发帖子
                return true;
            }
            return false;
        },
        getProcessedImageSrcInCss: function(){
            if(this.returnImageData && this.status == 'finished'){
                return 'background-image: url(\'/api/v1/getImage?imageId=' + this.returnImageData.imageId + '&imageSource=' + this.imgSrcIndex + '\');'
            }
        }
    },
    mounted: function () {
        this.$nextTick(function () {
            this.imageId = getQueryString('imageId');
            this.imageSrcIndex = getQueryString('imageSrcIndex')
        });
    }
})