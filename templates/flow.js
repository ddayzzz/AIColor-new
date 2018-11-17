// axios: https://github.com/axios/axios

Vue.component('post-flow-item', {
    template: '#post_item_template',
    delimiters: ['{[', ']}'],
    props: ['post', 'logined'],
    computed: {
        getUserLink: function () {
            return '/zone?username=' + this.post.username;

        },
        getImageSrc: function () {
            return '/api/v1/getImage?imageId=' + this.post.imageId + '&imageSource=' + this.post.imageSourceIndex;
        },
        post_like: function () {
            if (this.post.likedCount <= 1) {
                // 注意有默认用户点的赞
                return '<i class="uk-icon-thumbs-o-up" title="点赞"></i>';
            }
            else {
                return '<i class="uk-icon-thumbs-up" title="' + (this.post.likedCount - 1) + '人攒了"></i>';
            }
        },
        LikeCssObj: function(){
            return 'background-image: url(/static/images/icon-i-like-it.svg); cursor: pointer';
            if(!this.logined){
                if(this.post.likedCount <= 1){
                    // 没有登录，同时没人点赞
                    return {backgroundImage: 'url(/static/images/icon-noone-like-it.svg)', cursor: 'hand'};
                }else{
                    // 有人点赞
                }
                
            }
        }
    },
    methods: {
        flipLikeStatus: function () {
            console.log("LikedStatus:" + this.post.likedStatus);
            console.log("LikeId:" + this.post.likeId);
            var that = this;
            // 反转点赞的状态
            if (this.logined == false) {
                alert('请您先登录');
            } else {
                // 处理点怎逻辑
                var rdata = null;
                if (this.post.likeId != null) {
                    // 新的点赞信息
                    rdata = { postId: this.post.postId, likeId: this.post.likeId, };

                } else {
                    rdata = { postId: this.post.postId } // 新建新的属性
                }
                axios.post('/api/v1/flipLikeStatus', rdata)  // 注意第二个参数的传递的数据
                    .then(function (json_response) {
                        json_response = json_response.data;
                        if (json_response.status == 0) {
                            // 修改点赞的状态
                            var delta = json_response.data.liked ? 1 : -1;
                            if (that.post.likeId == null) {
                                // 之前没有id, 修改ID
                                that.post.likeId = json_response.data.likeId;
                            }
                            that.post.likedCount += delta;
                            that.post.likedStatus = json_response.data.liked;
                            console.log(json_response.data.liked);
                        }
                    })
                    .catch(function (error) {
                        if(error.status == 403){
                            alert("请您先登录");
                        }else{
                            alert('无法喜欢这个帖子:\n' + JSON.stringify(error.data.data));
                        }
                    });
            }
        },
        viewPost: function(){
            window.open('/viewPost?postId=' + this.post.postId);
        }
    },
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
    }
});

var post_app = new Vue({
    el: '#postFlow',
    data: function () {
        return { posts: null, logined: false };
    },
    mounted: function () {
        this.$nextTick(function () {
            var data_to_render = this;
            axios.get('/api/v1/getPostTimeLine')
            .then(function(rp){
                json_response = rp.data;
                if (json_response.status == 0) {
                    var desc_list = json_response.data.sorted_desc;
                    data_to_render.posts = desc_list;
                    axios.get('/api/v1/getUserLikedPosts')
                        .then(function(rp){
                            var json_response = rp.data;
                            if (json_response.status == 0) {
                                var likedPosts = json_response.data;
                                for (var i in desc_list) {
                                    var postItem = desc_list[i];
                                    var postId = postItem.postId;
                                    if (likedPosts.hasOwnProperty(postId)) { //判断属性是否存在
                                        postItem['likeId'] = likedPosts[postId].likeId;
                                        postItem['likedStatus'] = likedPosts[postId].liked;
                                    } else {
                                        postItem['likeId'] = null;
                                        postItem['likedStatus'] = false;
                                    }
                                }
                            }
                            data_to_render.logined = true;
                            console.log("User login");
                        })
                        .catch(function(error){
                            if(error.status == 403){
                                console.error("No user login");
                                data_to_render.logined = false;
                            }
                        });
                }
            })
            .catch(function(error){
                console.error(error);
            });
        })
    },

});