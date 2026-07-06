from flask import Flask, render_template
import psutil
import platform
import socket
import sys

app = Flask(__name__)

@app.route("/")
def index():

    cpu = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()

    disk = psutil.disk_usage("/")

    hostname = socket.gethostname()

    system = platform.system()

    release = platform.release()

    return render_template(
        "index.html",
        hostname=hostname,
        system=system,
        release=release,
        cpu=cpu,
        ram_total=round(memory.total / (1024**3),2),
        ram_used=round(memory.used / (1024**3),2),
        ram_percent=memory.percent,
        disk_total=round(disk.total / (1024**3),2),
        disk_used=round(disk.used / (1024**3),2),
        disk_percent=disk.percent
    )

if __name__ == "__main__":
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host="0.0.0.0", port=puerto) # nosec
    # The nosec mean that we are going to ignore the bandit error code since we are using a local tests environment