import os.path
import json
from werkzeug.serving import run_simple
from werkzeug.wrappers import Response
from aureus.wsgi_adapter import wsgi_app
from aureus.helper import parse_static_key
from aureus.route import Route
from aureus.template_engine import replace_template
from aureus.session import create_session_id, session
import aureus.exceptions as exceptions


# 定义文件类型
TYPE_MAP = {
    'css':  'text/css',
    'js': 'text/js',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg'
}

# 处理函数数据结构
class ExecFunc:
    def __init__(self, func, func_type, **options):
        self.func = func            # 处理函数
        self.options = options      # 附带参数
        self.func_type = func_type  # 函数类型

class AUREUS:            

    # 实例化方法
    def __init__(self, static_folder='static', template_folder='template', session_path=".session"):
        self.host = '127.0.0.1'  # 默认主机
        self.port = 8080  # 默认端口
        self.url_map = {} # 存放 URL 与 Endpoint 的映射
        self.static_map = {} # 存放 URL 与 静态资源的映射
        self.function_map = {} # 存放 Endpoint 与请求处理函数的映射
        self.static_folder = static_folder # 静态资源本地存放路径，默认放在应用所在目录的 static 文件夹下
        self.template_folder = template_folder # 模版文件本地存放路径，默认放在应用所在目录的 template 目录下
        AUREUS.template_folder = self.template_folder # 为类的 template_folder 也初始化，供上面的置换模版引擎调用
        self.session_path = session_path   # 会话记录默认存放在应用同目录下的 .session 文件夹中
        self.route = Route(self)  # 路由装饰器

    # 添加视图规则
    def bind_view(self, url, view_class, endpoint):
        self.add_url_rule(url, func=view_class.get_func(endpoint), func_type='view')

    # 控制器加载
    def load_controller(self, controller):

        # 获取控制器名字
        name = controller.__name__()

        # 遍历控制器的 `url_map` 成员
        for rule in controller.url_map:
            # 绑定 URL 与 视图对象，最后的节点名格式为 `控制器名` + "." + 定义的节点名
            self.bind_view(rule['url'], rule['view'], name + '.' + rule['endpoint'])



    # 添加路由规则
    @exceptions.capture
    def add_url_rule(self, url, func, func_type, endpoint=None, **options):

        # 如果节点未命名，使用处理函数的名字
        if endpoint is None:
            endpoint = func.__name__

        # 抛出 URL 已存在异常
        if url in self.url_map:
            raise exceptions.URLExistsError

        # 如果类型不是静态资源，并且节点已存在，则抛出节点已存在异常
        if endpoint in self.function_map and func_type != 'static':
            raise exceptions.EndpointExistsError

        # 添加 URL 与节点映射
        self.url_map[url] = endpoint

        # 添加节点与请求处理函数映射
        self.function_map[endpoint] = ExecFunc(func, func_type, **options)

    # 静态资源调路由
    @exceptions.capture
    def dispatch_static(self, static_path):
        # 判断资源文件是否在静态资源规则中，如果不存在，返回 404 状态页
        if os.path.exists(static_path):
            # 获取资源文件后缀
            key = parse_static_key(static_path)

            # 获取文件类型
            doc_type = TYPE_MAP.get(key, 'text/plain')

            # 获取文件内容
            with open(static_path, 'rb') as f:
                rep = f.read()

            # 封装并返回响应体
            return Response(rep, content_type=doc_type)
        else:
            # 抛出页面未找到异常
            raise exceptions.PageNotFoundError

    # 路由
    @exceptions.capture
    def dispatch_request(self, request):

        # 去掉 URL 中 域名部分，也就从 http://xxx.com/path/file?xx=xx 中提取 path/file 这部分
        url = "/" + "/".join(request.url.split("/")[3:]).split("?")[0]

        # 通过 URL 寻找节点名
        if url.find(self.static_folder) == 1 and url.index(self.static_folder) == 1:
            # 如果 URL 以静态资源文件夹名首目录，则资源为静态资源，节点定义为 static
            endpoint = 'static'
            url = url[1:]
        else:  
            # 若不以 static 为首，则从 URL 与 节点的映射表中获取节点
            endpoint = self.url_map.get(url, None)

        # 如果节点为空，抛出页面未找到异常
        if endpoint is None:
            raise exceptions.PageNotFoundError

        # 获取节点对应的执行函数
        exec_function = self.function_map[endpoint]

        # 判断执行函数类型
        if exec_function.func_type == 'route':
            """ 路由处理 """  

            # 判断请求方法是否支持
            if request.method in exec_function.options.get('methods'):
                """ 路由处理结果 """

                # 判断路由的执行函数是否需要请求体进行内部处理
                argcount = exec_function.func.__code__.co_argcount

                if argcount > 0:
                    # 需要附带请求体进行结果处理
                    rep = exec_function.func(request)
                else:
                    # 不需要附带请求体进行结果处理
                    rep = exec_function.func()
            else:
                """ 未知请求方法 """

                # 抛出请求方法不支持异常
                raise exceptions.InvalidRequestMethodError

        elif exec_function.func_type == 'view':
            """ 视图处理结果 """

            # 所有视图处理函数都需要附带请求体来获取处理结果
            rep = exec_function.func(request)
        elif exec_function.func_type == 'static':
            """ 静态逻辑处理 """

            # 静态资源返回的是一个预先封装好的响应体，所以直接返回
            return exec_function.func(url)
        else:
            """ 未知类型处理 """

            # 抛出未知处理类型异常
            raise exceptions.UnknownFuncError

        # 定义 200 状态码表示成功
        status = 200
        # 定义响应体类型
        content_type = 'text/html'

        # 从请求中取出 Cookie
        cookies = request.cookies

        # 如果 session_id 这个键不在 cookies 中，则通知客户端设置 Cookie
        if 'session_id' not in cookies:
            headers = {
                'Set-Cookie': 'session_id=%s' % create_session_id(), # 定义 Set-Cookie属性，通知客户端记录 Cookie，create_session_id 是生成一个无规律唯一字符串的方法
                'Server': 'AUREUS Web 0.1'   # 定义响应报头的 Server 属性
            }
        else:
            # 定义响应报头的 Server 属性
            headers = {
                'Server': 'AUREUS Web 0.1'
            }

        # 判断如果返回值是一个 Response 类型，则直接放回
        if isinstance(rep, Response):
            return rep

        # 回传实现 WSGI 规范的响应体给 WSGI 模块
        return Response(rep, content_type='%s; charset=UTF-8' % content_type, headers=headers, status=status)
        
    # 启动入口
    def run(self, host=None, port=None, **options):
        # 如果有参数进来且值不为空，则赋值
        for key, value in options.items():
          if value is not None:
            self.__setattr__(key, value)

        # 如果 host 不为 None，替换 self.host
        if host:
            self.host = host

        # 如果 port 不为 None，替换 self.port    
        if port:
            self.port = port

        # 映射静态资源处理函数，所有静态资源处理函数都是静态资源路由
        self.function_map['static'] = ExecFunc(func=self.dispatch_static, func_type='static')

         # 如果会话记录存放目录不存在，则创建它
        if not os.path.exists(self.session_path):
            os.mkdir(self.session_path)

        # 设置会话记录存放目录
        session.set_storage_path(self.session_path)

        # 加载本地缓存的 session 记录
        session.load_local_session()

        # 把框架本身也就是应用本身和其它几个配置参数传给 werkzeug 的 run_simple
        run_simple(hostname=self.host, port=self.port, application=self, **options)
      
    # 框架被 WSGI 调用入口的方法
    def __call__(self, environ, start_response):
        return wsgi_app(self, environ, start_response)

# 模版引擎接口
def simple_template(path, **options):
    return replace_template(AUREUS, path, **options)

# URL 重定向方法
def redirect(url, status_code=302):
    # 定义一个响应体
    response = Response('', status=status_code)

    # 为响应体的报头中的 Location 参数与 URL 进行绑定 ，通知客户端自动跳转
    response.headers['Location'] = url

    # 返回响应体
    return response

# 封装 JSON 数据响应包
def render_json(data):
    # 定义默认文件类型为纯文本
    content_type = "text/plain"

    # 如果是 Dict 或者 List 类型，则开始转换为 JSON 格式数据
    if isinstance(data, dict) or isinstance(data, list):

        # 将 data 转换为 JSON 数据格式
        data = json.dumps(data)

        # 定义文件类型为 JSON 格式
        content_type = "application/json"

    # 返回封装完的响应体
    return Response(data, content_type="%s; charset=UTF-8" % content_type, status=200)

# 返回让客户端保存文件到本地的响应体
@exceptions.capture
def render_file(file_path, file_name=None):

    # 判断服务器是否有该文件，抛出文件不存在异常
    if os.path.exists(file_path):

        # 判断是否有读取权限，没有则抛出权限不足异常
        if not os.access(file_path, os.R_OK):
            raise exceptions.RequireReadPermissionError

        # 读取文件内容
        with open(file_path, "rb") as f:
            content = f.read()

        # 如果没有设置文件名，则以 “/” 分割路径取最后一项最为文件名
        if file_name is None:
            file_name = file_path.split("/")[-1]

        # 封装响应报头，指定为附件类型，并定义下载的文件名
        headers = {
            'Content-Disposition': 'attachment; filename="%s"' % file_name
        }

        # 返回响应体
        return Response(content, headers=headers, status=200)

    # 如果不存在该文件，抛出文件不存在异常
    raise exceptions.FileNotExistsError
