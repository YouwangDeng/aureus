import os
import json
import base64
import time


# 创建 Session ID
def create_session_id():
    # 首先获取当前时间戳，转换为字符串，编码为字节流，在 Base64 编码，在解码为字符串，然后去掉 Base64 编码会出现的“=”号，取到倒数第二位，最后再进行倒序排列
    return base64.encodebytes(str(time.time()).encode()).decode().replace("=", '')[:-2][::-1]

# 从请求中获取 Session ID
def get_session_id(request):
    return request.cookies.get('session_id', '')

# 会话
class Session:

    # Session 实例对象
    __instance = None

    # 初始化方法
    def __init__(self):

        # 会话映射表
        self.__session_map__ = {}

         # 会话本地存放目录
        self.__storage_path__ = None

     # 设置会话保存目录
    def set_storage_path(self, path):
        self.__storage_path__ = path

    # 单例模式，实现全局公用一个 Session 实例对象
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(Session, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

	# 保存会话记录到本地
    def storage(self, session_id):
        # 构造 Session 会话的本地文件路径，文件名为 Session ID
        session_path = os.path.join(self.__storage_path__, session_id)

        # 如果已设置 Session 会话存放路径，则开始缓存到本地
        if self.__storage_path__ is not None:
            with open(session_path, 'wb') as f:
                # 将会话记录序列化为字符串
                content = json.dumps(self.__session_map__[session_id])

                # 进行 base64 编码再写入文件中，防止一些特定二进制数据无法正确写入
                f.write(base64.encodebytes(content.encode()))

    # 获取当前会话记录
    def map(self, request):
        return self.__session_map__.get(get_session_id(request), {})

    # 获取当前会话的某个项
    def get(self, request, item):
        return self.__session_map__.get(get_session_id(request), {}).get(item, None)

    # 更新或添加记录
    def push(self, request, item, value):

        # 从请求中获取客户端的 Session ID
        session_id = get_session_id(request)

        # 如果这个 Session ID 已存在与映射表中，则直接为其添加新的数据键值对，如果不存在，则先初始化为空的字典，再添加数据键值对
        if session_id in self.__session_map__:
            # 直接对当前会话添加数据
            self.__session_map__[session_id][item] = value
        else:
            # 初始化当前会话
            self.__session_map__[session_id] = {}

            # 对当前会话添加数据
            self.__session_map__[session_id][item] = value

        # 会话发生变化，更新缓存到本地
        self.storage(session_id)

    # 删除当前会话的某个项
    def pop(self, request, item, value=True):

        # 获取当前会话
        session_id = get_session_id(request)
        current_session = self.__session_map__.get(session_id, {})

        # 判断数据项的键是否存在于当前的会话中，如果存在则删除
        if item in current_session:
            current_session.pop(item, value)

        # 会话发生变化，更新缓存到本地
        self.storage(session_id)

    # 加载本地会话记录
    def load_local_session(self):

        # 如果已设置 Session 会话存放路径，则开始从本地加载缓存
        if self.__storage_path__ is not None:

            # 从本地存放目录获取所有 Session 会话记录文件列表，文件名其实就是 Session ID
            session_path_list = os.listdir(self.__storage_path__)

            # 遍历会话记录文件列表
            for session_id in session_path_list:

                # 构造会话记录文件目录
                path = os.path.join(self.__storage_path__, session_id)

                # 读取文件中的内容
                with open(path, 'rb') as f:
                    content = f.read()

                # 把文件内容进行 base64 解码
                content = base64.decodebytes(content)

                # 把 Session ID 于对应的会话内容绑定添加到会话映射表中
                self.__session_map__[session_id] = json.loads(content.decode())

# 单例全局对象
session = Session()

class AuthSession:

    # Session 校验装饰器
    @classmethod
    def auth_session(cls, f, *args, **options):

        def decorator(obj, request):
            return f(obj, request) if cls.auth_logic(request, *args, **options) else cls.auth_fail_callback(request, *args, **options)
        return decorator

    # 验证逻辑的接口，返回一个布尔值
    @staticmethod
    def auth_logic(request, *args, **options):
        raise NotImplementedError

    # 验证失败的回调接口
    @staticmethod
    def auth_fail_callback(request, *args, **options):
        raise NotImplementedError
