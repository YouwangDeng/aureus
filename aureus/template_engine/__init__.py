import os
import re


# 模版标记
pattern = r'{{(.*?)}}'

# 解析模版
def parse_args(obj):
    # 获取匹配对象
    comp = re.compile(pattern)

    # 查找所有匹配的结果
    ret = comp.findall(obj)

    # 如果匹配结果不为空，返回它，为空则返回一个空的 tuple
    return ret if ret else ()

# 返回模版内容
def replace_template(app, path, **options):
    # 默认返回内容，当找不到本地模版文件时返回
    content = '<h1>Not Found Template</h1>'

    # 获取模版文件本地路径
    path = os.path.join(app.template_folder, path)

    # 如果路径存在，则开始解析置换
    if os.path.exists(path):

        # 获取模版文件内容
        with open(path, 'rb') as f:
            content = f.read().decode()

        # 解析出所有的标记
        args = parse_args(content)

        # 如果置换内容不为空，开始置换
        if options:
            # 遍历所有置换数据，开始置换
            for arg in args:
                # 从标记中获取键
                key = arg.strip()

                # 如果键存在于置换数据中，则进行数据替换，反之替换为空
                content = content.replace("{{%s}}" % arg, str(options.get(key, '')))

    # 返回模版内容
    return content