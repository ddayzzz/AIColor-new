var create_post_app = new Vue({
    el: '#create-post-form',
    data: {
        imageSrcIndex: '',
        imageId: '',
        imageModel: null,
        postId: null,
        imageVueCompoent: null, // 这个是用于修改组建的 postid 属性
        title:''
    },
    computed:{
        getImageSrc: function(){
            return '/api/v1/getImage?imageId=' + this.imageId + '&imageSource=' + this.imageSrcIndex;
        },
        appendMarkTags: function () {
            if (this.imageSrcIndex == '0') {
                return '<span class="uk-badge">用户上传的图片</span>';
            } else if (this.imageSrcIndex == '1') {
                return '<span class="uk-badge">风格化的图片</span><span class="uk-badge uk-badge-success">采用 ' + this.imageModel + '</span>';
            } else if (this.imageSrcIndex == '2') {
                return '<span class="uk-badge">彩色化的图片</span><span class="uk-badge uk-badge-success">采用 ' + this.imageModel + '</span>';
            }
        },
    },
    methods:{
        showDialog: function(imageObj, imgSrcIndex, vuec){
            this.imageSrcIndex = imgSrcIndex; // 由于返回的数据库中不包含来源
            this.imageId = imageObj.imageId;
            this.postId = null; // 创建新的
            this.title = '';
            this.imageVueCompoent = vuec; // 组件绑定
            // 根据来源类型判断，图片的model 属性
            if (this.imageSrcIndex == '1') {
                this.imageModel = imageObj.styledModel;
            } else if (this.imageSrcIndex == '2') {
                this.imageModel = imageObj.colorizedModel;
            }else{
                this.imageModel = null;
            }
            UIkit.modal('#create-post-modal').show();
        },
        submit: function(event){
            event.preventDefault();
            // 添加帖子
            var that = this;
            var post_title = this.title == null ? '' : this.title.trim();
            if (post_title.length > 0 && post_title.length <= 100) {
                axios.post('/api/v1/createPost',{
                    imgSrcIndex: that.imageSrcIndex, imgId: that.imageId, title: post_title
                })
                .then(function(rp){
                    var json_response = rp.data;
                    if (json_response.status == 0) {
                        // alert(json_response.data.postInfo.postId)
                        alert("发布成功!");
                        var modal = UIkit.modal("#create-post-modal");
                        modal.hide();
                        // 需要设置编辑的属性吗？防止多次创建
                        that.imageVueCompoent.changePostId(json_response.data.postInfo.postId); // 不要直接修改属性。
                    }
                })
                .catch(function(error){
                    if(error.status == 403){
                        alert('无法创建帖子。请您先登录');
                    }else{
                        alert('无法创建帖子：' + error.status);
                    }
                });
            }
            else {
                alert('请输入大于1且不大于100的字符串');
            }
        }
    }
});


Vue.component('image-flow-unit-item', {
    template: '#image-flow-unit-template',
    delimiters: ['{[', ']}'],
    props: ['image_item_created_time', 'image_item_id', 'image_item_index', 'image_item', 'image_item_model'],
    filters: {
        convertDateTimeFromEra: function (time) {
            var d = new Date();
            var delta = Math.round((d.getTime() - time * 1000) / 1000.0);
            if (delta < 60)
                return '1分钟前'
            if (delta < 3600)
                return Math.round(delta / 60) + '分钟前';
            if (delta < 86400)
                return Math.round(delta / 3600) + '小时前';
            if (delta < 604800)
                return Math.round(delta / 86400) + '天前';
            var unixTimestamp = new Date(time * 1000);
            commonTime = unixTimestamp.toLocaleString();
            return commonTime;
        }
    },
    computed: {
        getImageSrc: function () {
            return '/api/v1/getImage?imageId=' + this.image_item_id + '&imageSource=' + this.image_item_index;
        }
    },
    methods: {
        createPost: function(){
            create_post_app.showDialog(this.image_item, this.image_item_index, this); // 为了修改状态
        },
        viewPost: function(){
            if(this.image_item.postId != null){
                window.open('/viewPost?postId=' + this.image_item.postId);
            }
        },
        changePostId: function(postId){
            this.image_item.postId = postId;
        },
        processImage: function(){
            window.open('/processer?imageId=' + this.image_item_id + '&imageSrcIndex=' + this.image_item_index);
        }
    }
});


var upload_images_flow_app = new Vue({
    el: '#upload-image-flow',
    data: function () {
        return { imagesList: null };
    },
    mounted: function () {
        this.$nextTick(function () {
            var data_to_render = this;
            axios.get('/api/v1/getImageTimeline', {params: { imageSrc: 0 }})
            .then(function(rp){
                var json_response = rp.data;
                if (json_response.status == 0) {
                    var desc_list = json_response.data.sorted_desc;
                    data_to_render.imagesList = desc_list;
                }
            });
        })
    }
});

var styled_images_flow_app = new Vue({
    el: '#styled-image-flow',
    data: function () {
        return { imagesList: null };
    },
    mounted: function () {
        this.$nextTick(function () {
            var data_to_render = this;
            axios.get('/api/v1/getImageTimeline', {params:{ imageSrc: 1 }})
            .then(function(rp){
                var json_response = rp.data;
                if (json_response.status == 0) {
                    var desc_list = json_response.data.sorted_desc;
                    data_to_render.imagesList = desc_list;
                }
            });
        })
    }
});
var colored_images_flow_app = new Vue({
    el: '#colored-image-flow',
    data: function () {
        return { imagesList: null };
    },
    mounted: function () {
        this.$nextTick(function () {
            var data_to_render = this;
            axios.get('/api/v1/getImageTimeline', {params:{ imageSrc: 2 }})
            .then(function(rp){
                var json_response = rp.data;
                if (json_response.status == 0) {
                    var desc_list = json_response.data.sorted_desc;
                    data_to_render.imagesList = desc_list;
                }
            });
        })
    }
});