from flask import Flask, request, render_template, redirect, send_from_directory

from title import TitleInformation
from table import TableInformation
from funcs import format_tables_info, format_date

import json
import zipfile

import shutil
import os

app = Flask(__name__)
folder_num = 0
app.config['UPLOAD_FOLDER'] = 'upload'
app.config['RESULT_FOLDER'] = 'result'
app.config['TEMP_FOLDER'] = 'temp'

if os.path.exists(app.config['UPLOAD_FOLDER']):
    shutil.rmtree(app.config['UPLOAD_FOLDER'])
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.mkdir(app.config['UPLOAD_FOLDER'])

if os.path.exists(app.config['RESULT_FOLDER']):
    shutil.rmtree(app.config['RESULT_FOLDER'])
if not os.path.exists(app.config['RESULT_FOLDER']):
    os.mkdir(app.config['RESULT_FOLDER'])

if not os.path.exists(app.config['TEMP_FOLDER']):
    os.mkdir(app.config['TEMP_FOLDER'])


@app.route('/')
def index():
    return redirect('upload')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    global folder_num
    if request.method == 'POST':
        files = request.files.getlist('file')
        folder_num += 1
        for file in files:
            if file:
                if file.filename[-4:] == '.zip':
                    file.save(f"{app.config['UPLOAD_FOLDER']}{os.sep}{file.filename}")
                    with zipfile.ZipFile(f"{app.config['UPLOAD_FOLDER']}{os.sep}{file.filename}", 'r') as zip_file:
                        zip_file.extractall(app.config['UPLOAD_FOLDER'])
                    os.rename(f"{app.config['UPLOAD_FOLDER']}{os.sep}{file.filename[:-4]}",
                              f"{app.config['UPLOAD_FOLDER']}{os.sep}zip{folder_num}")
                else:
                    file.save(f"{app.config['UPLOAD_FOLDER']}{os.sep}title{folder_num}.jpg")
        return redirect('form')
    return render_template('upload.html')


@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        data = {
            'service_record_series': request.form.get('service_record_series'),
            'service_record_number': request.form.get('service_record_number'),
            'last_name': request.form.get('last_name'),
            'first_name': request.form.get('first_name'),
            'middle_name': request.form.get('middle_name'),
            'education': request.form.get('education'),
            'birthday': request.form.get('birthday'),
            'fill_date': request.form.get('fill_date'),
            'entries': []
        }

        entries_count = int(request.form.get('entries_count'))
        for i in range(1, entries_count + 1):
            entry = {
                'entry_date': request.form.get(f'entry_date_{i}'),
                'entry_info': request.form.get(f'entry_info_{i}'),
                'entry_stamp': request.form.get(f'entry_stamp_{i}'),
            }
            if entry['entry_date'] is not None and entry['entry_info'] is not None and entry['entry_stamp'] is not None:
                data['entries'].append(entry)

        data = json.dumps(data)
        with open(f"{app.config['RESULT_FOLDER']}{os.sep}data{folder_num}.json", 'w') as outfile:
            json.dump(data, outfile)
        return send_from_directory(app.config['RESULT_FOLDER'], f'data{folder_num}.json', as_attachment=True)

    title_info = TitleInformation()
    model_data = title_info.get_full_info(f"{app.config['UPLOAD_FOLDER']}{os.sep}title{folder_num}.jpg")
    model_data['birthday'] = format_date(model_data['birthday'])
    model_data['fill_date'] = format_date(model_data['fill_date'])

    filepaths = [f"..{os.sep}{app.config['UPLOAD_FOLDER']}{os.sep}title{folder_num}.jpg"]
    table_info = TableInformation()
    table_data = []
    table_files = os.listdir(f"{app.config['UPLOAD_FOLDER']}{os.sep}zip{folder_num}")
    for fname in table_files:
        filepaths.append(f"..{os.sep}{app.config['UPLOAD_FOLDER']}{os.sep}zip{folder_num}{os.sep}{fname}")
        table_data.append(table_info.get_data(f"{app.config['UPLOAD_FOLDER']}{os.sep}zip{folder_num}{os.sep}{fname}"))
    table_data = format_tables_info(table_data)

    return render_template('form.html', model_data=model_data, table_data=table_data,
                           table_data_len=len(table_data), filepaths=filepaths)


if __name__ == '__main__':
    app.run()
