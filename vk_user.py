import requests
from datetime import datetime


class VkUser:
    initial_url = 'https://api.vk.com/method/'
    def __init__(self, token, version='5.131') -> None:
        self.params = {
            'access_token' : token,
            'v' : version,
        }
    
    def get_user_id(self, user_name: str) -> int:
        response = requests.get(
            f'{self.initial_url}users.get', 
            params=(self.params | {'user_ids': user_name})
        ).json()['response']
        if not response:
            return
        return response[0]['id']

    def get_list_of_max_size_photos_for_upload(self, photos_owner_id: str, 
            album_of_photos_id: str, count=5) -> list:
        params_for_phtos_get = {
            'owner_id' : photos_owner_id,
            'album_id' : album_of_photos_id,
            'extended' : 1,
            'photo_sizes' : 1,
            'count' : count
        }
        list_of_photos_of_all_sizes = requests.get(
            f'{self.initial_url}photos.get', 
            params=self.params | params_for_phtos_get
        ).json()['response']['items']
        
        list_of_max_size_photos = []
        for photo in list_of_photos_of_all_sizes:
            post_date = datetime.fromtimestamp(photo['date']).date()
            photo_name = str(photo['likes']['count']) + '.jpg'
            for record in list_of_max_size_photos:
                if record['photo_name'] == photo_name:
                    photo_name = photo_name[0:-4] + f' [{post_date}].jpg'            
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
            list_of_max_size_photos.append({
                'photo_name': photo_name, 
                'photo_url_and_size_info': max_size_photo,
            })
        return list_of_max_size_photos