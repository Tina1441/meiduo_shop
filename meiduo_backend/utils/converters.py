class UsernameConverter:
    # 匹配 5 到 20 位的字母、数字、下划线、连字符
    regex = r"[a-zA-Z0-9_-]{5,20}"

    def to_python(self, value):
        # 将 URL 中的字符串转换为 Python 对象（这里直接返回字符串即可）
        return str(value)

    def to_url(self, value):
        # 将 Python 对象转换为 URL 中使用的字符串
        return str(value)