class Evaluation:
    """
    评价AI能力的工具
    V1：目前仅支持，自定义目标，无法使用客观目标
    """

    def __init__(self):
        self._register_buffer = []

    def register(self, name, callback_get_params, template):
        """

        :param name: 指标名字
        :param callback_get_params: 获取参数,参数以dict的形式返回
        :param template: 参数展示的模板
        :return:
        """
        self._register_buffer.append({
            "name": name,
            "callback": callback_get_params,
            "template": template
        })

    def get_eval(self):
        eval_list = ["对话能力:"]
        for item in self._register_buffer:
            name = item["name"]
            params = item["callback"]()
            template = item["template"]
            eval_list.append(name)
            eval_list.append(template.format(**params))
            eval_list.append("\n")
        return eval_list
