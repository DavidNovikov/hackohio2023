from flask import Flask
import socket

app = Flask(__name__)

@app.route('/')
def index():
  return 'Hello, World!'

if __name__ == '__main__':
    # find available port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()

    # print port
    print(">>", port)

    # run app
    app.run(port=port)