from werkzeug.wrappers import Request

# WSGI 调度框架入口
def wsgi_app(app, environ, start_response):
  """
   第一个参数是应用
   第二个参数就是服务器传过来的请求
   第三个参数则是响应载体，这个参数我们完全不会使用到，只需要连同处理结果一起传回给服务器就行
  """

  # 解析请求头
  request = Request(environ)

  # 把请求传给框架的路由进行处理，并获取处理结果
  response = app.dispatch_request(request)

  # 返回给服务器
  return response(environ, start_response)

