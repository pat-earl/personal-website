from personal import app

@app.route("/")
@app.route("/index")
def index():
    return "<h1 style='color:red'>Test</h1>"