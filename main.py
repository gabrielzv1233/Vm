import os
from flask import Flask, render_template, request, redirect, send_from_directory, current_app, abort, make_response

app = Flask(__name__)
allowed_directory = r".\ftp" #use .\ for relitive directorys on windows and use ./ for relitive directorys in linux, for windows use backslashes(\) and linux use normal slashes (/)
current_directory = allowed_directory

if not os.path.exists(allowed_directory):
    exit(f"Error: Directory \"{allowed_directory}\" does not exist")
    
def get_files_and_directories(directory):
    items = os.listdir(directory)
    files = []
    directories = []
    for item in items:
        if os.path.isfile(os.path.join(directory, item)):
            files.append(item)
        else:
            directories.append(item)
    return files, directories

@app.route('/')
def file_explorer():
    # Replace the allowed_directory path with "HOME"
    censored_directory = current_directory.replace(allowed_directory, "HOME")
    
    files, directories = get_files_and_directories(current_directory)
    return render_template('file_explorer.html', current_directory=censored_directory, files=files, directories=directories)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        filename = file.filename
        file_path = os.path.join(current_directory, filename)
        if os.path.exists(file_path):
            print(f"File '{filename}' already exists, not uploading")
            return "File already exists on the server."
        else:
            file.save(file_path)
            print("File saved successfully!")
            return redirect('/')
    else:
        print("No file received.")
        return "No file received."

@app.route('/create_directory', methods=['POST'])
def create_directory():
    directory_name = request.form['directory_name']
    if directory_name:
        os.makedirs(os.path.join(current_directory, directory_name))
    return redirect('/')

@app.route('/rename', methods=['POST'])
def rename_file_or_directory():
    item_name = request.form['item_name']
    new_name = request.form['new_name']
    if item_name and new_name:
        os.rename(os.path.join(current_directory, item_name), os.path.join(current_directory, new_name))
    return redirect('/')

@app.route('/delete', methods=['POST'])
def delete_file_or_directory():
    item_name = request.form['item_name']
    if item_name:
        path = os.path.join(current_directory, item_name)
        if os.path.isfile(path):
            os.remove(path)
        else:
            os.rmdir(path)
    return redirect('/')

@app.route('/change_directory', methods=['POST'])
def change_directory():
    global current_directory
    directory_name = request.form['directory_name']
    if directory_name == '..':
        if current_directory != allowed_directory:
            current_directory = os.path.dirname(current_directory)
    else:
        directory_path = os.path.join(current_directory, directory_name)
        if os.path.isdir(directory_path):
            current_directory = directory_path

    # Replace the allowed_directory path with "HOME" in the new current_directory
    censored_directory = current_directory.replace(allowed_directory, "HOME")
    
    return redirect('/')

    # Replace the allowed_directory path with "HOME" in the new current_directory
    censored_directory = current_directory.replace(allowed_directory, "HOME")
    
@app.route('/download/<path:filename>')
def download_file(filename):
    # Get the file extension
    file_extension = filename.rsplit('.', 1)[-1].lower()

    # Define the allowed file types to open in a new tab
    allowed_types = ['jpg', 'jpeg', 'png', 'gif', 'txt']

    # Check if the file extension is in the allowed types
    if file_extension in allowed_types:
        # Get the file path
        file_path = os.path.join(current_directory, filename)

        # Try to open the file
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # Create a response with appropriate content type
            response = make_response(file_content)
            content_type = f'image/{file_extension}' if file_extension in ['jpg', 'jpeg', 'png', 'gif'] else 'text/plain'
            response.headers['Content-Type'] = content_type

            # Open the file in a new tab
            response.headers['Content-Disposition'] = 'inline'

            return response
        except FileNotFoundError:
            abort(404)
    else:
        # If the file extension is not in the allowed types, download the file
        return send_from_directory(current_directory, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)