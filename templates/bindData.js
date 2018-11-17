// 设置数据绑定
// 设置状态属性
//var routerIdToVue = new Array();
//var routerStausToVue = new Array();
//var sysStatusVue = null;
//
//function init_addRequestCount() {
//
//    // 描述组建关系
//    Vue.component('request-counter-comp', {
//        props: ['counter'],
//        template: '<span>{{counter}}&nbsp;&nbsp;</span>'
//    });
//    // 路由的启动信息
//    Vue.component('router-btn-comp', {
//        props: ['renable', 'rchange'],
//        template: '<button class="uk-button">{{renable ? "禁用": "启用"}}</button>'
//    });
//    // 遍历所有模块的组件，添加关联的数据绑定
//    var packages = document.getElementsByClassName('packageStatus');
//    for (var i = 0; i < packages.length; ++i) {
//        // 对于每一个模块中的每一个路由都设置新的 Vue 实例
//        var router_tag_main = packages[i].getElementsByClassName('requestCounter_class');
//        for (var j = 0; j < router_tag_main.length; ++j) {
//            var router_main = router_tag_main[j];
//            var vm = new Vue({
//                el: '#' + router_main.id,
//                data: {
//                    routerStatus_counter: 0,
//                    routerStatus_enable: false,
//                    enableChangedCallStr: ''
//                },
//                methods: {
//                    update: function (counter, enabled, flagName) {
//                        this.routerStatus_counter = counter;
//                        this.routerStatus_enable = enabled;
//                        if (enabled) {
//                            this.enableChangedCallStr = '"false","' + flagName + '")';
//                        }
//                        else {
//                            this.enableChangedCallStr = '"true","' + flagName + '")';
//                        }
//                    }
//                }
//            });
//            routerIdToVue[router_main.id] = vm;
//        }
//    }
//    // 初始化全局运行信息
//    sysStatusVue = new Vue({
//        el: '#main_sysStatusMgr',
//        data: {
//            status_cpuRate: '不可用',
//            status_memoryUsage: '不可用',
//            status_runnningTime: '不可用',
//            status_bindHost: '不可用',
//            status_bindPort: '不可用'
//        },
//        methods: {
//            update: function (cpurate, mem, rtime, bindHost, bindPort) {
//                this.status_cpuRate = cpurate;
//                this.status_memoryUsage = mem;
//                this.status_bindHost = bindHost;
//                this.status_bindPort = bindPort;
//                this.status_runnningTime = rtime;
//            }
//        }
//    });
//}
//function getRuntimeInfo(notMaintenance) {
//    axios.get('/api/maintenance/getStatus')
//        .then(function (response) {
//            var runtimeInfo = response.data.data.runningTimeInfo;
//            if (notMaintenance) {
//                var reqCount = runtimeInfo.routerInfo;
//                for (var router_info in reqCount) {
//                    routerIdToVue[router_info].update(reqCount[router_info].count, reqCount[router_info].enable, router_info);
//                }
//            }
//            // 更新其他的信息
//            sysStatusVue.update(runtimeInfo.cpuRate, runtimeInfo.memoryUsage, runtimeInfo.runningTime, runtimeInfo.bindHost, runtimeInfo.bindPort);
//        })
//        .catch(function (error) {
//            alert(error);
//        })
//}
//
//function toClose() {
//    UIkit.modal.confirm("确定要关闭服务？", function () {
//        $.ajax({
//            type: "GET",
//            url: '/api/main_close',
//            success: function (str_response) {
//                var newDoc = document.open("text/html", "replace");
//                var txt = "<html><script type=\"text/javascript\" >window.onload = function () {setTimeout(() => { window.location.href = 'about:blank';}, 2000);}</script><body>服务关闭。</body></html>";
//                newDoc.write(txt);
//                newDoc.close();
//            }
//        });
//    });
//}
//function toRestart() {
//    UIkit.modal.confirm("确定要重启服务？", function () {
//        $.ajax({
//            type: "GET",
//            url: '/api/main_restart',
//            success: function (str_response) {
//                var newDoc = document.open("text/html", "replace");
//                var txt = "<html><script type=\"text/javascript\" >window.onload = function () {setTimeout(() => { location.reload();}, 2000);}</script><body>服务正在重启。2 秒后自动刷新。</body></html>";
//                newDoc.write(txt);
//                newDoc.close();
//            }
//        });
//    });
//}
//function toRestartAndEnterMaintenance() {
//    UIkit.modal.confirm("确定要重启服务并进入到维护模式？进入维护模式后可以对模块进行管理。", function () {
//        // 点击OK确认后开始执行
//        $.ajax({
//            type: "GET",
//            url: '/api/main_restart/enterMaintenance',
//            success: function (str_response) {
//                var newDoc = document.open("text/html", "replace");
//                var txt = "<html><script type=\"text/javascript\" >window.onload = function () {setTimeout(() => { location.reload();}, 2000);}</script><body>服务正在重启并进入维护模式。2 秒后自动刷新。</body></html>";
//                newDoc.write(txt);
//                newDoc.close();
//            }
//        });
//    });
//}
//function changeRouterEnableStatus(packageName, targetStatus, routerFlag) {
//    // 需要启用
//    axios.get('/api/maintenance/setRouterStatus/' + packageName + '/' + routerFlag + '?enable=' + targetStatus)
//        .then(function (response) {
//            alert('设置成功！');
//            getRuntimeInfo(true);
//        })
//        .catch(function (error) {
//            alert(error);
//        })
//
//}
// ------------ NOT USED---------------

// 全局组建
Vue.component('so-unit-imageitem', {
    template: `<article class="uk-article">
  <h1 class="uk-article-title"><i class="uk-icon-user"></i> {[image_item_username]}{[image_item_title]}</h1>
  <div><span class="uk-badge">{[markTag]}</span><span class="uk-badge uk-badge-success"><a v-bind:href="originalImageURI" target="_blank">打开原始图像</a></span></div>
  <p class="uk-article-meta">{[image_item_created_time|convertDateTimeFromEra]}</p>
  <div class="uk-thumbnail uk-thumbnail-expand"><img v-bind:src="genImageSrc" alt=""></div>
  <div class="uk-button-group">
  <a href="#" class="uk-button uk-button-large"><i class="uk-icon-share-alt"></i> 分享</a>
  <a v-html="image_item_like" v-on:click="flipLikeStatus(image_item_id)" class="uk-button uk-button-large"></a>
  <a href="#" class="uk-button uk-button-large"><i class="uk-icon-comment-o"></i> 评论</a></div><hr class="uk-article-divider"></article>`,
    delimiters: ['{[', ']}'],
    props: ['image_item_username', 'image_item_created_time', 'image_item_id', 'image_item_index', 'image_item', 'image_item_likes_data', 'image_item_comments_data'],
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
        genImageSrc: function () {
            return '/api/v1/getImage?imageId=' + this.image_item_id + '&imageSource=' + this.image_item_index;
        },
        markTag: function () {
            switch (this.image_item_index) {
                case 1:
                    // 风格化的版本：显示上色风格模型、来源图片链接
                    return '使用的模型：' + this.image_item.styledModel;
                case 0:
                    // 原始图片：显示原始标签
                    return '用户上传的原始图片';
                case 2:
                    return '使用的模型：' + this.image_item.colorizedModel;
            }
        },
        image_item_title: function () {
            switch (this.image_item_index) {
                case 1:
                    return '的风格化图片';
                case 0:
                    return '上传的图片';
                case 2:
                    return '的彩色化图片';
            }
        },
        originalImageURI: function () {
            if (this.image_item_index == 0) {
                return '/api/v1/getImage?imageId=' + this.image_item_id + '&imageSource=' + this.image_item_index;
            }
            else {
                return '/api/v1/getImage?imageId=' + this.image_item.originalImageId + '&imageSource=' + this.image_item.imageSourceIndex;
            }
        },
        image_item_like: function () {
            if (this.image_item_likes_data.total > 0) {
                return '<i class="uk-icon-thumbs-up"></i>' + this.image_item_likes_data.total + ' 人赞了';
            }
            else {
                return '<i class="uk-icon-thumbs-o-up"></i> 赞';
            }
        }
    },
    methods: {
        flipLikeStatus: function (imgId) {
            if(document.getElementById('signout-btn') == null){
                alert('请您先登录或者注册新账户。');
                window.location.href = '/signin?redirect=/zone';
            }
            var self = this;
            $.ajax({
                type: "POST",
                url: '/api/v1/flipLikeStatus',
                dataType: "json",
                data: { imageId: imgId },
                success: function (json_response) {
                    if (json_response.status == 0) {
                        // 重新设置属性
                        var total = self.image_item_likes_data.total;
                        var returned = json_response.data.flipped;
                        var delta = returned ? 1 : -1;
                        self.image_item_likes_data.total = total + delta;
                    }
                }
            });
        }
    }
});

var images_flow_app = new Vue({
    el: '#imagesFlow',
    data: function () {
        return { imagesList: null };
    },
    mounted: function () {
        this.$nextTick(function () {
            var data_to_render = this;
            $.ajax({
                type: "get",
                url: '/api/v1/getImageTimeline',
                dataType: "json",
                success: function (json_response) {
                    if (json_response.status == 0) {
                        var desc_list = json_response.data.sorted_desc;
                        for (var index in desc_list) {
                            var imageId = desc_list[index].imageId; // 获取JSON中的对象
//                            $.ajax({ // 发出获取点赞的信息
//                                type: "get",
//                                url: '/api/v1/getLikes',
//                                data: { 'imageId': imageId },
//                                dataType: "json",
//                                async: false,// 同步
//                                success: function (json_response1) {
//                                    if (json_response1.status == 0) {
//                                        desc_list[index].likes = json_response1.data;
//                                    }
//                                }
//                            });
//                            $.ajax({ // 发出获取评论的信息
//                                type: "get",
//                                url: '/api/v1/getComments',
//                                data: { 'imageId': imageId },
//                                dataType: "json",
//                                async: false,
//                                success: function (json_response1) {
//                                    if (json_response1.status == 0) {
//                                        desc_list[index].comments = json_response1.data;
//                                    }
//                                }
//                            });
                        }
                        data_to_render.imagesList = desc_list;

                    }
                }
            });
        })
    }
});

function getComments(imageId) {
    // 需要启用
    $.ajax({
        type: "POST",
        url: '/api/v1/getComments',
        data: { 'imageId': imageId },
        dataType: "json",
        contentType:"application/json;charser=utf-8",
        success: function (json_response) {
            if (json_response.status == 0) {
                console.log(json_response)
                // 显示评论
                for (var i in json_response.data) {
                    console.log(json_response.data[i]);
                }
            }
        }
    });
}
function insertComment(imageId, comment) {
    $.ajax({
        type: "POST",
        url: '/api/v1/insertComment',
        data: { 'imageId': imageId, 'comment': comment },
        success: function (json_response) {
            // TODO
        }
    });
}
function getLikes(imageId) {
    // 需要启用
    $.ajax({
        type: "GET",
        url: '/api/v1/getComments',
        data: { 'imageId': imageId },
        dataType: "json",
        success: function (json_response) {
            if (json_response.status == 0) {
                console.log(json_response)
                // 显示评论
                for (var i in json_response.data) {
                    console.log(json_response.data[i]);
                }
            }
        }
    });
}