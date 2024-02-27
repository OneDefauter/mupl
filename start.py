import os
import subprocess
from io import BytesIO
from zipfile import ZipFile


namespace = "OneDefauter"

def install_modules():
    required_modules = [
        'requests',
        'natsort',
        'Pillow',
        'tqdm',
        'asyncio',
        'packaging',
        'flask',
    ]

    for module in required_modules:
        try:
            if module == 'Pillow':
                __import__('PIL')
            else:
                __import__(module)
        except ImportError:
            subprocess.run(['pip', 'install', module])

    os.system('cls' if os.name == 'nt' else 'clear')

def download_and_execute():
    temp_folder = os.environ.get('TEMP', '') if os.name == 'nt' else os.environ.get('TMPDIR', '')
    app_folder = os.path.join(temp_folder, "MangaDex Uploader (APP)")
    path_file = os.path.join(temp_folder, "MangaDex Uploader (APP)", "run.py")
    folder_executed = os.getcwd()
    
    os.makedirs(app_folder, exist_ok=True)
    os.makedirs(os.path.join(app_folder, "to_upload"), exist_ok=True)
    os.makedirs(os.path.join(app_folder, "uploaded"), exist_ok=True)
    os.chdir(app_folder)
    
    if os.path.exists(os.path.join(app_folder, "__init__.py")):
        with open(os.path.join(app_folder, "__init__.py"), 'r') as file:
            for line in file:
                if line.startswith('__version__'):
                    __version__ = line.split('=')[1].strip().strip('"\'')
    else:
        __version__ = "2.0.1" # Initial version

    remote_release = requests.get(f"https://api.github.com/repos/{namespace}/mupl/releases/latest")
    local_version = version.parse(__version__)
    
    if remote_release.ok:
        remote_release_json = remote_release.json()
        remote_version = version.parse(remote_release_json["tag_name"])
        zip_resp = requests.get(remote_release_json["zipball_url"])
        if zip_resp.ok:
            myzip = ZipFile(BytesIO(zip_resp.content))
            zip_root = [z for z in myzip.infolist() if z.is_dir()][0].filename
            zip_files = [z for z in myzip.infolist() if not z.is_dir()]
        
        if not os.path.exists(path_file):
            for fileinfo in zip_files:
                filename = os.path.join(app_folder, fileinfo.filename.replace(zip_root, ""))
                dirname = os.path.dirname(filename)
                os.makedirs(dirname, exist_ok=True)
                file_data = myzip.read(fileinfo)

                with open(filename, "wb") as fopen:
                    fopen.write(file_data)
        else:
            if remote_version > local_version:
                print(f"MangaDex Uploader (APP) is up to date.\nVersion: {remote_version}\nLocal: {local_version}")
                for fileinfo in zip_files:
                    filename = os.path.join(app_folder, fileinfo.filename.replace(zip_root, ""))
                    dirname = os.path.dirname(filename)
                    os.makedirs(dirname, exist_ok=True)
                    file_data = myzip.read(fileinfo)

                    with open(filename, "wb") as fopen:
                        fopen.write(file_data)
    
    if os.path.exists(path_file):
        command = ['python', path_file, folder_executed] if os.name == 'nt' else ['python3', path_file, folder_executed]

        subprocess.run(command)


if __name__ == "__main__":
    install_modules()
    import requests
    from packaging import version
    download_and_execute()
