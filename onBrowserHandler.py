from bases import avaiableModelsForBrowser
from bases import just_get_username


async def browser_get_style_transfer(request, modelId=-1):
    """
    获取风格转换的页面
    :param request: 请求
    :param modelId: 模型ID编号（如果为 -1 表示显示选择页面）
    :return:
    """
    username = just_get_username(request)
    modelId = int(modelId)
    if modelId == -1:
        return {'__template__': 'browserProcess.html', 'username': username, 'models': avaiableModelsForBrowser.get(1)}
    else:
        if modelId < 0 or modelId >= len(avaiableModelsForBrowser.get(1)):
            raise ValueError('非法的模型编号')

        return {'__template__': 'genStyleOnBrowser/styleTransfer.html',
                'model': avaiableModelsForBrowser.get(1)[modelId], 'username': username}


async def browser_post_upload(request):
    pass