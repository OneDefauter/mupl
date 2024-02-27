import os
import sys
import json
import webbrowser
import subprocess
from flask import Flask, render_template, request, jsonify

try:
    folder_executed = sys.argv[1]
except:
    folder_executed = os.getcwd()


app = Flask(__name__)

temp_folder = os.environ.get('TEMP', '') if os.name == 'nt' else os.environ.get('TMPDIR', '')
app_folder = os.path.join(temp_folder, "MangaDex Uploader (APP)")
mupl_app = os.path.join(app_folder, "mupl.py")
config_path = os.path.join(app_folder, 'config.json')
map_path_file = os.path.join(app_folder, 'name_id_map.json')

default_url = 'http://127.0.0.1:5000'


def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "options": {
                "number_of_images_upload": 10,
                "upload_retry": 3,
                "ratelimit_time": 2,
                "max_log_days": 30,
                "group_fallback_id": None,
                "number_threads": 3,
                "language_default": "en"
            },
            "credentials": {
                "mangadex_username": None,
                "mangadex_password": None,
                "client_id": None,
                "client_secret": None
            },
            "paths": {
                "name_id_map_file": "name_id_map.json",
                "uploads_folder": "to_upload",
                "uploaded_files": "uploaded",
                "mangadex_api_url": "https://api.mangadex.org",
                "mangadex_auth_url": "https://auth.mangadex.org/realms/mangadex/protocol/openid-connect",
                "mdauth_path": ".mdauth"
            }
        }

def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4, ensure_ascii=False)@app.route("/")

def create_map():
    data = {
        "manga": {
            "test1": "f9c33607-9180-4ba6-b85c-e4b5faee7192",
            "test2": "f9c33607-9180-4ba6-b85c-e4b5faee7192"
        },
        "group": {
            "test1": "6410209a-0f39-4f51-a139-bc559ad61a4f",
            "test2": "6410209a-0f39-4f51-a139-bc559ad61a4f"
        }
    }
    
    with open(map_path_file, 'w', encoding="utf-8") as arquivo:
        json.dump(data, arquivo, indent=4)

@app.route('/')
def index():
    def create_config_file(uploads_folder, uploaded_files):
        config_structure = {
            "options": {
                "number_of_images_upload": 10,
                "upload_retry": 3,
                "ratelimit_time": 2,
                "max_log_days": 30,
                "group_fallback_id": None,
                "number_threads": 3,
                "language_default": "en"
            },
            "credentials": {
                "mangadex_username": None,
                "mangadex_password": None,
                "client_id": None,
                "client_secret": None
            },
            "paths": {
                "name_id_map_file": "name_id_map.json",
                "uploads_folder": uploads_folder,
                "uploaded_files": uploaded_files,
                "mangadex_api_url": "https://api.mangadex.org",
                "mangadex_auth_url": "https://auth.mangadex.org/realms/mangadex/protocol/openid-connect",
                "mdauth_path": ".mdauth"
            }
        }

        # Create the config.json file
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(config_structure, file, indent=4)

    def check_config_paths():
        uploads_folder = os.path.join(folder_executed, 'to_upload')
        uploaded_files = os.path.join(folder_executed, 'uploaded')
        
        os.makedirs(uploads_folder, exist_ok=True)
        os.makedirs(uploaded_files, exist_ok=True)
        
        if not os.path.exists(config_path):
            create_config_file(uploads_folder, uploaded_files)

        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)

            if config['paths']['uploads_folder'] != uploads_folder:
                config['paths']['uploads_folder'] = uploads_folder

            if config['paths']['uploaded_files'] != uploaded_files:
                config['paths']['uploaded_files'] = uploaded_files

            config['paths']['uploads_folder'] = os.path.abspath(config['paths']['uploads_folder'])
            config['paths']['uploaded_files'] = os.path.abspath(config['paths']['uploaded_files'])

        # Update the config.json file if there are modifications
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=4)

    check_config_paths()
    
    if not os.path.exists(map_path_file):
        create_map()
    
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            config = json.load(file)
            if 'credentials' in config and all(config['credentials'].values()):
                return main_setup()
    except FileNotFoundError:
        pass
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_credential', methods=['POST'])
def login_credential():
    try:
        credentials = request.get_json()

        required_fields = ['mangadex_username', 'mangadex_password', 'client_id', 'client_secret', 'languageCode']
        if not all(field in credentials for field in required_fields):
            return jsonify({'error': 'Por favor, forneça todas as credenciais necessárias.'}), 400

        config = load_config()

        config['credentials'] = {key: value for key, value in credentials.items() if key != 'languageCode'}
        config['options']['language_default'] = credentials['languageCode']

        save_config(config)
        return '', 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/new_login')
def new_login():
    return render_template('index.html')

@app.route('/main_setup')
def main_setup():
    return render_template('main.html')

@app.route('/get_language', methods=['GET'])
def get_language():
    config = load_config()
    language_default = config['options']['language_default']
    return jsonify({'language_default': language_default})

@app.route('/open_folder1', methods=['POST'])
def open_folder1():
    uploads_folder = os.path.join(folder_executed, 'to_upload')
    if os.name == 'nt':  # Windows
        subprocess.Popen('explorer /select,' + uploads_folder)
    else:
        if sys.platform.startswith('darwin'):  # macOS
            subprocess.Popen(['open', uploads_folder])
        else:  # Linux
            subprocess.Popen(['xdg-open', uploads_folder])
    return '', 200

@app.route('/open_folder2', methods=['POST'])
def open_folder2():
    uploaded_files = os.path.join(folder_executed, 'uploaded')
    if os.name == 'nt':  # Windows
        subprocess.Popen('explorer /select,' + uploaded_files)
    else:
        if sys.platform.startswith('darwin'):  # macOS
            subprocess.Popen(['open', uploaded_files])
        else:  # Linux
            subprocess.Popen(['xdg-open', uploaded_files])
    return '', 200

@app.route('/open_file', methods=['POST'])
def open_file():
    try:
        subprocess.run(['notepad.exe', map_path_file])
        return '', 200
    except:
        return '', 400

@app.route('/clear_folder1', methods=['POST'])
def clear_folder1():
    uploaded_files = os.path.join(folder_executed, 'uploaded')
    
    def limpar_pasta(pasta):
        itens_na_pasta = os.listdir(pasta)
        
        for item in itens_na_pasta:
            caminho_item = os.path.join(pasta, item)
            
            if os.path.isdir(caminho_item):
                if item != 'uploaded':
                    limpar_pasta(caminho_item)
            else:
                os.remove(caminho_item)

        if pasta != uploaded_files:
            os.rmdir(pasta)

    limpar_pasta(uploaded_files)
    return '', 200

@app.route('/start_process', methods=['POST'])
def start_process():
    try:
        if sys.platform.startswith('win'):
            command = ['python', mupl_app]
        else:
            command = ['python3', mupl_app]
        subprocess.run(command)
        return '', 200
        
    except subprocess.CalledProcessError as e:
        print(f"Error mupl.py: {e}")
        return '', 400
    except Exception as e:
        print(f"Error: {e}")
        return '', 400
    



webbrowser.open(default_url)
app.run(debug=False)
