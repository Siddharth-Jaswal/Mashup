from flask import Flask, request, jsonify, send_from_directory, render_template
import subprocess
import os
import sys
import threading
import time


app = Flask(__name__)


def delete_file_later(filepath, delay=300):
    def delete():
        time.sleep(delay)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Deleted file after delay: {filepath}")

    thread = threading.Thread(target=delete)
    thread.daemon = True
    thread.start()



@app.route("/")
def index():
    return render_template("index.html")



@app.route("/create-mashup", methods=["POST"])
def create_mashup():
    data = request.get_json()

    singer = data.get("singer")
    n = data.get("number_of_videos")
    duration = data.get("duration")
    output_file = data.get("output_file")

    if not all([singer, n, duration, output_file]):
        return jsonify({"error": "Missing parameters"}), 400

    try:

        command = [
            sys.executable,
            "102303592.py",
            singer,
            str(n),
            str(duration),
            output_file
        ]

        subprocess.run(command, check=True)

        return jsonify({
            "message": "Mashup created successfully!",
            "file": f"output/{output_file}"
        })

    except subprocess.CalledProcessError:
        return jsonify({"error": "Mashup creation failed"}), 500


@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    output_folder = os.path.join(os.getcwd(), "output")
    file_path = os.path.join(output_folder, filename)

    if not os.path.exists(file_path):
        return {"error": "File not found"}, 404

    delete_file_later(file_path, delay=60)

    return send_from_directory(
        directory=output_folder,
        path=filename,
        as_attachment=True
    )




if __name__ == "__main__":
    app.run(debug=True)
