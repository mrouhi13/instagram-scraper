import json
import os
import sys
import time
from urllib import request
from urllib.parse import urljoin

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from utils import generate_file_name


class Instagram:
    POST_LIMIT_COUNT = 12

    base_url = 'https://instagram.com'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    download_dir = os.path.join(base_dir, 'photos')
    target_username = None
    target_url = None
    driver = None
    all_posts_count = None
    post_limit = POST_LIMIT_COUNT
    delay = 3

    post_class_name = 'v1Nh3'
    photo_class_name = 'FFVAD'
    caption_class_name = 'C4VMK'
    posts_count_class_name = 'g47SY'
    error_container_class_name = 'error-container'

    def __init__(self, target_username):
        """Create a Chrome Driver instance."""
        sys.stdout.write(f'\nStarting...')

        self.driver = webdriver.Chrome()

        assert target_username and not target_username == '', (
            '`target_username` must be set.'
        )

        self.target_username = target_username

        sys.stdout.write(f'\n\nTarget username:\t{self.target_username}\n')

    def open_target_url(self, uri=None):
        """Use this method to open the target URL."""
        if not self.target_url == urljoin(self.base_url, uri):
            self.target_url = urljoin(self.base_url, uri)
            self.driver.get(self.target_url)

    def load_more_posts(self):
        """Use this method to load more posts."""
        body_element = self.driver.find_element_by_tag_name('body')
        last_height = self.driver.execute_script(
            'return document.body.scrollHeight')

        while True:
            loaded_posts = self.driver.find_elements_by_class_name(
                self.post_class_name)
            loaded_post_count = len(loaded_posts)

            sys.stdout.write(
                f'\rLoading posts: \t\t{loaded_post_count} of '
                f'{self.all_posts_count}')
            sys.stdout.flush()

            if loaded_post_count >= self.post_limit:
                break

            body_element.send_keys(Keys.END)
            time.sleep(self.delay)
            self.driver.execute_script(
                'document.body.style.overflow = "scroll";')

            new_height = self.driver.execute_script(
                'return document.body.scrollHeight')

            if new_height == last_height:
                break

            last_height = new_height

        sys.stdout.write(
            f'\rLoading posts: \t\t{loaded_post_count} of '
            f'{self.all_posts_count}\t\tDone\n')

    def _set_post_limit(self, post_limit):
        """Use this method to validate posts limit count."""
        try:
            post_limit = int(post_limit)
        except ValueError as e:
            raise e
        except TypeError:
            post_limit = self.POST_LIMIT_COUNT

        posts_count = self.driver.find_element_by_class_name(
            self.posts_count_class_name).text
        self.all_posts_count = int(posts_count.replace(',', ''))
        self.post_limit = post_limit

        if self.post_limit > self.all_posts_count or self.post_limit <= 0:
            self.post_limit = self.all_posts_count

    def check_username(self):
        sys.stdout.write(f'\nChecking username...\n')

        self.open_target_url(self.target_username)

        try:
            error_element = self.driver.find_element_by_class_name(
                self.error_container_class_name)

            if error_element:
                return False
        except NoSuchElementException:
            pass

        return True

    def get_user_posts(self, username):
        """
        Use this method to get a bunch of posts for the given username.
        :parameter
         string: username
        :return list posts_id
        """
        posts_id = []

        self.open_target_url(username)
        self.load_more_posts()
        posts = self.driver.find_elements_by_class_name(self.post_class_name)[
                :self.post_limit]

        for post in posts:
            sys.stdout.write(
                f'\rFetching post ids: \t{len(posts_id)} of {self.post_limit}')
            sys.stdout.flush()

            link_element = post.find_element_by_tag_name('a')
            post_url = link_element.get_attribute('href')
            post_id = post_url.split('/')[-2]
            posts_id.append(post_id)

        sys.stdout.write(
            f'\rFetching post ids: \t{len(posts_id)} of '
            f'{self.post_limit}\t\tDone\n\n')

        return posts_id

    def get_post_photos(self, post_id):
        """Use this method to get the photo(s) URL for
        the given post id."""
        photos_url = []
        self.open_target_url(f'p/{post_id}')

        try:
            photo_element = self.driver.find_element_by_class_name(
                self.photo_class_name)
            photos_url.append(photo_element.get_attribute('src'))
        except NoSuchElementException:
            pass

        return photos_url

    def get_post_caption(self, post_id):
        """Use this method to get the caption of post for
        the given post id."""
        self.open_target_url(f'p/{post_id}')
        caption_element = self.driver.find_element_by_class_name(
            self.caption_class_name).find_element_by_tag_name('span')
        caption = caption_element.text
        metadata = self.export_metadata(caption)

        return caption, metadata

    def export_metadata(self, caption):
        """Return a dict include character name and
        quote of the given caption.
        This method specifically used for '__nitch' username posts."""
        character_name, quote = '', ''

        if caption and self.target_username == '__nitch':
            try:
                character_name, quote = caption.split(' // ')
            except ValueError:
                pass

        return {
            'character_name': character_name.title(),
            'quote': quote.replace('"', '')
        }

    def download_photo(self, urls, preferred_file_name):
        """Use this method to download the photo(s)
        for the given URLs list."""
        files = []

        for url in urls:
            file_name = generate_file_name(preferred_file_name,
                                           self.download_dir)

            if url:
                request.urlretrieve(url,
                                    os.path.join(self.download_dir, file_name))
                files.append(file_name)

        return files

    def clone(self, post_limit=None):
        """Use this method to clone all posts for
        the given username in one call."""
        i = 0
        posts = []

        self._set_post_limit(post_limit)
        self.download_dir = os.path.join(self.download_dir,
                                         self.target_username)

        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir, 0o775)

        sys.stdout.write(f'\nPost limit:\t\tlast {self.post_limit} post(s)')
        sys.stdout.write(f'\nDownload Dir:\t\t{self.download_dir}\n\n')

        posts_ids = self.get_user_posts(self.target_username)
        posts_count = len(posts_ids)

        for post_id in posts_ids:
            i += 1
            sys.stdout.write(
                f'\rCloning\t\t\t{post_id} ({i} of {posts_count})')

            caption, metadata = self.get_post_caption(post_id)
            photos_url = self.get_post_photos(post_id)

            if photos_url:
                files = self.download_photo(photos_url,
                                            metadata.get('character_name',
                                                         post_id))
                metadata.update({'files': files})
                post_object = {
                    'post_id': post_id,
                    'post_url': self.target_url,
                    'photos_url': photos_url,
                    'caption': caption,
                    'metadata': metadata
                }
                posts.append(post_object)
                sys.stdout.flush()

        with open(os.path.join(self.download_dir, 'data.json'), 'w') as fp:
            json.dump(posts, fp)

        fetched_count = len(posts)
        sys.stdout.write(
            f'\n\n{fetched_count} post(s) cloned successfully.\n\n')
