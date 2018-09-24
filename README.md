# Aureus

Aureus is a lightweight web application framework. It supports
Model-View-Controller (MVC) architectural pattern. It is designed to
make getting started quick and easy, with the ability to scale up to
complex applications.

## Installing

Install and update using
[pip](https://pip.pypa.io/en/stable/quickstart/):

```bash
pip install -U aureus
```

## A Simple Example

```Python
from aureus import AUREUS

app = AUREUS()

@app.route('/', methods=['GET'])
def hello():
    return '<h1>Hello Aureus!</h1>'

app.run()
```

```bash
$ python3 main.py
 * Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)
```

## A MVC pattern Example

```Python
from aureus import AUREUS
from aureus.view import View, Controller


class BaseView(View):
    
    methods = ['GET, POST']

    def post(self, request, *args, **options):
        pass

    def get(self, request, *args, **options):
        pass

    def dispatch_request(self, request, *args, **options):

        methods_meta = {
            'GET': self.get,
            'POST': self.post,
        }

        if request.method in methods_meta:
            return methods_meta[request.method](request, *args, **options)
        else:
            return '<h1>Unknown or unsupported require method</h1>'

class Hello(BaseView):
    def get(self, request):
        return '<h1>Hello, Aureus!</h1>'


app = AUREUS()

aureus_url_map = [
    {
        'url': '/',
        'view': Hello,
        'endpoint': 'hello'
    },
]

hello_controller = Controller('hello', aureus_url_map)
app.load_controller(hello_controller)

app.run()
```

```bash
$ python3 main.py
 * Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)
```

## Links

-   License:
    [BSD](https://github.com/YouwangDeng/Aureus/blob/master/LICENCE)
-   Releases: <https://pypi.org/project/Aureus/>
-   Code: <https://github.com/YouwangDeng/Aureus>
-   Issue tracker: <https://github.com/YouwangDeng/Aureus/issues>

