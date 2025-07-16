import os
import threading
import time
import uuid
import io
from flask import Flask, render_template, request, send_file, jsonify
from nt import process_nt
from qld import process_qld
from nsw import process_nsw
from wa import process_wa
from act import process_act
import subprocess

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

progress_map = {}
result_buffer_map = {}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/progress/<task_id>')
def progress(task_id):
    return jsonify({"progress": progress_map.get(task_id, 0)})

@app.route('/download/<task_id>')
def download(task_id):
    result = result_buffer_map.get(task_id)
    if result:
        return send_file(
            io.BytesIO(result.encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='result.csv'
        )
    return "Result not ready", 404

@app.route('/start', methods=['POST'])
def start():
    file = request.files['file']
    state = request.form['state']
    task_id = str(uuid.uuid4())
    progress_map[task_id] = 0

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}_{file.filename}")
    file.save(filepath)

    thread = threading.Thread(target=process_with_progress, args=(filepath, state, task_id))
    thread.start()

    return jsonify({"task_id": task_id})

def process_with_progress(filepath, state, task_id):
    try:
        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        total = len(lines)

        buffer = io.StringIO()
        header_written = False

        for i, line in enumerate(lines):
            temp_file = os.path.join(UPLOAD_FOLDER, f"{task_id}_temp.csv")
            with open(temp_file, "w") as sf:
                sf.write(line + "\n")

            if state == 'nt':
                result_file = process_nt(temp_file)
            elif state == 'qld':
                result_file = process_qld(temp_file)
            elif state == 'nsw':
                result_file = process_nsw(temp_file)
            elif state == 'wa':
                result_file = process_wa(temp_file)
            elif state == 'act':
                result_file = process_act(temp_file)
            else:
                progress_map[task_id] = 100
                return

            with open(result_file, "r") as rf:
                rows = rf.readlines()
                if not header_written:
                    buffer.write(rows[0])
                    header_written = True
                if len(rows) > 1:
                    buffer.write(rows[1])

            progress_map[task_id] = int(((i + 1) / total) * 100)
            time.sleep(0.2) 

        result_buffer_map[task_id] = buffer.getvalue()
        buffer.close()
        progress_map[task_id] = 100

    except Exception as e:
        print(f"Error: {e}")
        progress_map[task_id] = 100

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)