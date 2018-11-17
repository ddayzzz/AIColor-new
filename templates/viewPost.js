// 获取 url 参数中的 key name 的值
function getQueryString(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) return unescape(r[2]); return null;
}

Vue.component('comment-component',{
    template:'#comment-template',
    delimiters: ['{[', ']}'],
    props:['co', 'po'],  // 很奇怪，无法进用鸵峰命名，co=comment Obj, po=post Obj
    computed:{
        getUserStatus: function(){
            // 获取用户的级别
            if(this.co.username == this.po.username){
                return '(作者)';
            }else if(this.co.username == 'default'){
                return '(系统账户)';
            }else{
                return '';
            }
        },

        getUserLink: function(){
            return '/zone?username=' + this.co.username;
        },
        replyText: function(){
            if(this.co.to_username){
                return ' 回复 ' + this.co.to_username;
            }
            return '';
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
        },
        filteUsername: function(username){
            // 获取用户的显示的名称
            if(username == 'default'){
                return '系统账户';
            }else{
                return username;
            }
        }
    },
    methods:{
        commitReply: function(){
            comment_adder.showDialog(this.co);
        }
    }
});

var comments_viewer = new Vue({
    el: '#comments-app',
    data: {
        post: null,
        comments: null,
        newCommentContent: null
    },
    mounted: function () {
        this.init();
    },
    methods: {
        addANewComment: function(comment){
            // 添加了新评论或者是回复，由子组建触发
            this.init();
        },
        init: function(){
            this.$nextTick(function () {
                this.postId = getQueryString('postId');
                // 设置 post 属性
                var root = document.getElementById('postDetail');
                this.post = {
                    postId: root.getAttribute('postid'),
                    title: root.getAttribute('posttitle'),
                    imageId: root.getAttribute('imageid'),
                    imageSourceIndex: root.getAttribute('imagesourceindex'),
                    created_time: root.getAttribute('createdtime'),
                    username: root.getAttribute('username')
                };
                // 从后端的读取评论的信息
                var that = this;
                axios.get('/api/v1/getComments',{
                    params:{
                        postId: this.post.postId
                    }
                })
                .then(function(rp){
                    that.comments = rp.data.data.comments;
                })
                .catch(function(error){
                    console.error(error);
                })
            });
        }
    }
});

// 添加评论
var comment_adder = new Vue({
    el: '#add-comment-modal',
    delimiters:['{[', ']}'],
    data:{
        comment: '',
        title: '',
        commentObj: null
    },
    methods:{
        submit: function(event){
            event.preventDefault();
            var replyTo = this.commentObj.username;
            var comment = this.comment;
            var postId = this.commentObj.postId;
            // 检查
            if(comment == undefined || comment == null){
                alert("请输入一个合法的字符串");
                return;
            }
            comment = comment.trim();
            if(comment.length <= 0 || comment.length > 200){
                alert("请输入长度大于1小于200的字符串");
                return;
            }
            // 先发送请求
            axios.post('/api/v1/insertComment',{
                postId: postId,
                comment: comment,
                replyUsername: replyTo
            })
            .then(function(rp){
                if(rp.data.status == 0){
                    var json_comment = rp.data.data.comment;
                    comments_viewer.addANewComment(json_comment);
                }else{
                    alert("回复失败");
                }
            })
            .catch(function(error){
                if(error.status == 403){
                    alert('回复失败：请您先登录');
                }else{
                    alert("回复失败:" + error.status);
                }
            });
            UIkit.modal(document.getElementById('add-comment-modal')).hide();
        },
        showDialog: function(co){
            if(co == undefined || co == null){
                this.title = '添加新评论';
            }else{
                this.title = '回复：' + co.username;
            }
            this.commentObj = co;
            this.comment = '';
            UIkit.modal(document.getElementById('add-comment-modal')).show();
        }
    }
})
// 快速评论口
var fast_comment_adder = new Vue({
    el: '#fast-comment-info',
    data:{
        comment: '',
    },
    methods:{
        submit: function(event){
            var that = this;
            event.preventDefault();
            var comment = this.comment;
            var postId = getQueryString('postId');
            // 检查
            if(comment == undefined || comment == null){
                alert("请输入一个合法的字符串");
                return;
            }
            comment = comment.trim();
            if(comment.length <= 0 || comment.length > 200){
                alert("请输入长度大于1小于200的字符串");
                return;
            }
            // 先发送请求
            axios.post('/api/v1/insertComment',{
                postId: postId,
                comment: comment,
            })
            .then(function(rp){
                if(rp.data.status == 0){
                    var json_comment = rp.data.data.comment;
                    comments_viewer.addANewComment(json_comment);
                    that.comment = '';
                }else{
                    alert("添加评论失败");
                }
            })
            .catch(function(error){
                if(error.status == 403){
                    alert('添加评论失败：请您先登录');
                }else{
                    alert("添加评论失败：" + error.status);
                }
            });
        }
    }
})