import requests
import json
from pprint import pprint
from datetime import date


class VkUser:
    initial_url = 'https://api.vk.com/method/'
    def __init__(self, token, version='5.131') -> None:
        self.params = {
            'access_token' : token,
            'v' : version,
        }
        self.user_id = requests.get(f'{self.initial_url}users.get', params=self.params).json()['response'][0]['id']

    def get_list_of_max_size_photos_for_upload(self, photos_owner_id: str, album_of_photos_id: str) -> list:
        params_for_phtos_get = {
            'owner_id' : photos_owner_id,
            'album_id' : album_of_photos_id,
            'extended' : 1,
            'photo_sizes' : 1
        }
        list_of_photos_of_all_sizes = requests.get(f'{self.initial_url}photos.get', params=self.params | params_for_phtos_get).json()['response']['items']
        
        list_of_max_size_photos = []
        for photo in list_of_photos_of_all_sizes:
            photo_name = str(photo['likes']['count']) + '.jpg'
            max_size_photo = photo['sizes'][-1]
            flag = 0
            for size in photo['sizes']:        
                if size['type'] == 'w':
                    max_size_photo = size
                    flag = 7
                elif size['type'] == 'z' and flag < 7:
                    max_size_photo = size
                    flag = 6
                elif size['type'] == 'y' and flag < 6:
                    max_size_photo = size
                    flag = 5
                elif size['type'] == 'x' and flag < 5:
                    max_size_photo = size
                    flag = 4
                elif size['type'] == 'r' and flag < 4:
                    max_size_photo = size
                    flag = 3
                elif size['type'] == 'q' and flag < 3:
                    max_size_photo = size
                    flag = 2
                elif size['type'] == 'p' and flag < 2:
                    max_size_photo = size
                    flag = 1        
                elif size['type'] == 'm' and flag < 1:
                    max_size_photo = size
            list_of_max_size_photos.append({'photo_name': photo_name, 'photo_url_and_size_info': max_size_photo})
        return list_of_max_size_photos


class YaDiskUser:
    initial_url = 'https://cloud-api.yandex.net/v1/disk/'
    def __init__(self, token) -> None:
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {token}'
        }

    def get_upload_link_for_file(self, ya_disk_path_to_file: str, file_name: str) -> dict:
        upload_url = f'{self.initial_url}resources/upload'       
        params = {"path": ya_disk_path_to_file + file_name, "overwrite": "true"}
        return requests.get(upload_url, headers=self.headers, params=params).json()

    def upload_file_to_disk(self, photo_to_upload: bytes, ya_disk_path_to_file: str, file_name: str) -> None:
        href = self.get_upload_link_for_file(ya_disk_path_to_file, file_name).get("href")
        response = requests.put(href, data=photo_to_upload)
        response.raise_for_status()


def get_token_from_file(file_name: str) -> str:
    """Возвращает авторизационный токен сохраненный в отдельном файле 'file_name'."""
    with open(file_name, 'rt', encoding='utf-8') as file:
        return file.read().strip()

def creat_backups_for_vk_photos_on_ya_disk(photos_owner_id: str, photo_album_id: str, vk_user: VkUser, ya_disk_uploader: YaDiskUser, ya_disk_path_to_file='photo_backups/') -> None:
    """Копирует файлы из альбома 'photo_album_id' пользователя ВКонтакте 'photos_owner_id', 
    ссылки на которые получает методом 'get_list_of_max_size_photos_for_upload' класса 'VkUser', 
    в папку 'ya_disk_path_to_file' на Яндекс.Диск методом 'upload_file_to_disk' класса 'YaDiskUser'.
    """
    list_of_photos_to_upload = vk_user.get_list_of_max_size_photos_for_upload(photos_owner_id, photo_album_id)
    log_to_write = []
    print('Uploading...')
    for i, photo in enumerate(list_of_photos_to_upload, 1):
        photo_data = requests.get(photo['photo_url_and_size_info']['url'])
        ya_disk_uploader.upload_file_to_disk(photo_data, ya_disk_path_to_file, photo['photo_name'])
        log_to_write.append({'file_name': photo['photo_name'], 'size': photo['photo_url_and_size_info']['type']})
        print(f'{i} of {len(list_of_photos_to_upload)}')
    print('All files uploaded successfully.')
    with open(f'upload_from_vk_{str(date.today())}.log.json', 'w') as file:
            json.dump(log_to_write, file, ensure_ascii=False, indent=2)


vk_user = VkUser(get_token_from_file('vk_token.txt'))
ya_disk_uploader = YaDiskUser(get_token_from_file('ya_disk_token.txt'))

creat_backups_for_vk_photos_on_ya_disk(vk_user.user_id, 'profile', vk_user, ya_disk_uploader)