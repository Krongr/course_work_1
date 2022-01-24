import requests
import json
from pprint import pprint
from datetime import date
from vk_user import VkUser
from ya_disk_user import YaDiskUser


def get_token_from_file(file_name: str) -> str:
    """Возвращает авторизационный токен 
    сохраненный в отдельном файле 'file_name'.
    """
    with open(file_name, 'rt', encoding='utf-8') as file:
        return file.read().strip()

def creat_folder_for_vk_photo_backups_on_ya_disk(
        ya_disk_user: YaDiskUser, owner: str) -> dict:
    """Создает папку на Яндекс.Диск для фотографий из ВКонтакте.
    Имя папки генерируется автоматически.
    """
    folder_name = f'vk photos of {owner} [uploaded-{str(date.today())}]/'
    response = ya_disk_user.create_folder_on_ya_disk(folder_name)
    return {'folder_name' : folder_name, 'response' : response}

def creat_backups_for_vk_photos_on_ya_disk(
        photos_owner: str, photo_album_id: str, vk_user: VkUser, 
        ya_disk_user: YaDiskUser, count=5, ya_disk_path_to_file='default'
    ) -> dict:
    """Копирует файлы из альбома 'photo_album_id' 
    пользователя ВКонтакте 'photos_owner_id', 
    ссылки на которые получает методом 
    'get_list_of_max_size_photos_for_upload' класса 'VkUser', 
    в папку 'ya_disk_path_to_file' на Яндекс.Диск методом 
    'upload_file_to_disk' класса 'YaDiskUser'.
    """
    photos_owner_id = vk_user.get_user_id(photos_owner)
    if not photos_owner_id:
        print('Пользователь не найден')
        return
    list_of_photos_to_upload = vk_user.get_list_of_max_size_photos_for_upload(
        photos_owner_id, photo_album_id, count)
    if ya_disk_path_to_file == 'default':
        ya_disk_path_to_file = creat_folder_for_vk_photo_backups_on_ya_disk(
            ya_disk_user, photos_owner_id)['folder_name']
    responses_log = []
    log_to_write = []
    print('Uploading...')
    for i, photo in enumerate(list_of_photos_to_upload, 1):
        photo_data = requests.get(
            photo['photo_url_and_size_info']['url']).content
        upload_response = ya_disk_user.upload_file_to_ya_disk(
            photo_data, ya_disk_path_to_file, photo['photo_name'])

        responses_log.append({photo['photo_name'] : upload_response})
        log_to_write.append({
            'file_name': photo['photo_name'], 
            'size': photo['photo_url_and_size_info']['type']
        })
        print(f'{i} of {len(list_of_photos_to_upload)}')
    print('All files uploaded successfully.')
    with open(f'upload_from_vk_{str(date.today())}.log.json', 'w') as file:
            json.dump(log_to_write, file, ensure_ascii=False, indent=2)
    return responses_log


if __name__ == "__main__":
    vk_user = VkUser(get_token_from_file('vk_token.txt'))
    ya_disk_user = YaDiskUser(get_token_from_file('ya_disk_token.txt'))


    creat_backups_for_vk_photos_on_ya_disk(
        'begemot_korovin', 'profile', vk_user, ya_disk_user
    )