from flask import Flask, request, render_template
import main

#name是什么?
app = Flask(__name__)

#装饰器是什么鬼? 接受一个函数作为参数，不影响函数本身的功能,执行自己的功能route(home())
@app.route('/', methods=['GET'])
def home():
    return 'Home'

#这里要制作了一个api.html显示
@app.route('/api', methods=['GET'])
def api():
    apifrommain = main.API()
    return render_template('api.html',proxyies = apifrommain.get_all())

if __name__ == '__main__':
    app.run()
