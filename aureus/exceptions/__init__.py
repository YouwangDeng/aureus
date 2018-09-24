from werkzeug.wrappers import Response

# 定义公用的报头参数 Content-Type 
content_type = 'text/html; charset=UTF-8'

# 异常编号与响应体的映射关系
ERROR_MAP = {
    '2': Response('<h1>E2 Not Found File</h1>', content_type=content_type, status=500),
    '13': Response('<h1>E13 No Read Permission</h1>', content_type=content_type, status=500),
    '401': Response('<h1>401 Unknown Or Unsupported Method</h1>', content_type=content_type, status=401),
    '404': Response('<h1>404 Source Not Found<h1>', content_type=content_type, status=404),
    '503': Response('<h1>503 Unknown Function Type</h1>', content_type=content_type, status=503)
}

# 框架异常基类
class AUREUSException(Exception):
    def __init__(self, code='', message='Error'):
        self.code = code        # 异常编号
        self.message = message  # 异常信息

    def __str__(self):
        return self.message     # 当作为字符串使用时，返回异常信息


# 节点已存在
class EndpointExistsError(AUREUSException):
    def __init__(self, message='Endpoint exists'):
        super(EndpointExistsError, self).__init__(message)


# URL 已存在异常
class URLExistsError(AUREUSException):
    def __init__(self, message='URL exists'):
        super(URLExistsError, self).__init__(message)


# 文件未找到
class FileNotExistsError(AUREUSException):
    def __init__(self, code='2', message='File not found'):
        super(FileNotExistsError, self).__init__(code, message)


# 权限不足
class RequireReadPermissionError(AUREUSException):
    def __init__(self, code='13', message='Require read permission'):
        super(RequireReadPermissionError, self).__init__(code, message)


# 不支持的请求方法
class InvalidRequestMethodError(AUREUSException):
    def __init__(self, code='401', message='Unknown or unsupported request method'):
        super(InvalidRequestMethodError, self).__init__(code, message)


# 页面未找到
class PageNotFoundError(AUREUSException):
    def __init__(self, code='404', message='Source not found'):
        super(PageNotFoundError, self).__init__(code, message)


# 未知处理类型
class UnknownFuncError(AUREUSException):
    def __init__(self, code='503', message='Unknown function type'):
        super(UnknownFuncError, self).__init__(code, message)


# 异常捕获
def capture(f):
    def decorator(*args, **options):
        # 开始捕获异常
        try:
            # 尝试执行函数
            rep = f(*args, **options)
        except AUREUSException as e:
            # 当捕获到 AUREUSException 这个分类的异常时，判断下异常的编号，如果不为空且关联再 ERROR_MAP 中，进行对应的处理，反之接着抛出
            if e.code in ERROR_MAP and ERROR_MAP[e.code]:

                # 获取异常关联的结果
                rep = ERROR_MAP[e.code]

                # 如果异常编号小于 100，响应状态码统一设置为 500 服务端错误
                status = int(e.code) if int(e.code) >= 100 else 500

                # 判断结果是否一个响应体，如果不是，则应该就是自定义异常处理函数，调用它并封装为响应体返回
                return rep if isinstance(rep, Response) or rep is None else Response(rep(), content_type=content_type, status=status)
            else:
                # 接着抛出没有对应处理的异常
                raise e
        # 返回函数执行正常的结果
        return rep
    # 返回装饰器
    return decorator

    
# 异常处理重载装饰器，参数为异常编号，需要注意的是这里的编号为了方便开发者所以用的是整形
def reload(code):
    def decorator(f):
        # 替换 ERROR_MAP 中 异常编号关联的处理逻辑为所装饰的函数
        ERROR_MAP[str(code)] = f

    # 返回装饰器
    return decorator


