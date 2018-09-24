Aureus =====

Aureus is a lightweight web application framework. It supports
Model-View-Controller (MVC) architectural pattern. It is designed to
make getting started quick and easy, with the ability to scale up to
complex applications.

Installing
==========

Install and update using
[pip](https://pip.pypa.io/en/stable/quickstart/):

``` {.sourceCode .text}
pip install -U Aureus
```

A Simple Example
================

``` {.sourceCode .python}
from aureus import AUREUS

app = AUREUS()

@app.route('/index', methods=['GET'])
def index():
    return 'Hello Aureus!'

app.run()
```

``` {.sourceCode .text}
$ python3 main.py
 * Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)
```

A MVC pattern Example ----------------

``` {.sourceCode .python}
from aureus import AUREUS
from aureus.view import Controller

from core.base_view import BaseView


class Index(BaseView):
    def get(self, request):
        return 'Hello, Aureus!'


app = AUREUS()

aureus_url_map = [
    {
        'url': '/index',
        'view': Index,
        'endpoint': 'index'
    },
]

index_controller = Controller('index', aureus_url_map)
app.load_controller(index_controller)

app.run()
```

``` {.sourceCode .text}
$ python3 main.py
 * Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)
```

Links
=====

-   License:
    [BSD](https://github.com/YouwangDeng/Aureus/blob/master/LICENCE)
-   Releases: <https://pypi.org/project/Aureus/>
-   Code: <https://github.com/YouwangDeng/Aureus>
-   Issue tracker: <https://github.com/YouwangDeng/Aureus/issues>

