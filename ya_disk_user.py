import requests


class YaDiskUser:
    initial_url = 'https://cloud-api.yandex.net/v1/disk/'
    def __init__(self, token) -> None:
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {token}'
        }

    def create_folder_on_ya_disk(self, folder_name: str) -> dict:
        upload_url = f'{self.initial_url}resources'       
        params = {"path": folder_name}
        return requests.put(upload_url, headers=self.headers, 
            params=params).json()

    def get_upload_link_for_file(self, ya_disk_path_to_file: str, 
            file_name: str) -> dict:
        if ya_disk_path_to_file[-1] != '/':
            ya_disk_path_to_file += '/'
        upload_url = f'{self.initial_url}resources/upload'       
        params = {
            "path": ya_disk_path_to_file + file_name, 
            "overwrite": "true"
        }
        return requests.get(upload_url, headers=self.headers, 
            params=params).json()

    def upload_file_to_ya_disk(self, photo_to_upload: bytes, 
            ya_disk_path_to_file: str, file_name: str) -> None:
        if ya_disk_path_to_file[-1] != '/':
            ya_disk_path_to_file += '/'
        href = self.get_upload_link_for_file(
            ya_disk_path_to_file, 
            file_name
        ).get("href")
        response = requests.put(href, data=photo_to_upload)
        response.raise_for_status()
        return response