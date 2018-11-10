import os.path
import base64
try:
    from io import StringIO
except ImportError:
    from io import StringIO
from django.core.cache import cache
from django.core.files import File
from django.core.files.storage import Storage
from django.utils.encoding import filepath_to_uri
import requests

from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from django.utils.deconstruct import deconstructible


from .settings import (CONSUMER_ID,
                       CONSUMER_SECRET,
                       ACCESS_TOKEN,
                       ACCESS_TOKEN_REFRESH,
                       USERNAME)
import logging

logger = logging.getLogger(__name__)

@deconstructible
class ImgurStorage(Storage):
    """
    A storage class providing access to resources in a Dropbox Public folder.
    """

    def __init__(self, location='/'):
        self.client = ImgurClient(
            CONSUMER_ID,
            CONSUMER_SECRET,
            ACCESS_TOKEN,
            ACCESS_TOKEN_REFRESH)
        logger.info("Logged in Imgur storage")
        self.account_info = self.client.get_account(USERNAME)
        self.albums = self.client.get_account_albums(USERNAME)
        self.location = location
        self.base_url = 'https://api.imgur.com/3/account/{url}/'.format(url=self.account_info.url)

    def _get_abs_path(self, name):
        return os.path.join(self.location, name)

    def _open(self, name, mode='rb'):
        remote_file = self.client.get_image(name, self, mode=mode)
        return remote_file

    def _save(self, name, content):
        name = self._get_abs_path(name)
        directory = os.path.dirname(name)
        logger.info([a.title for a in self.albums])
        logger.info(name)
        logger.info(directory)
        if not self.exists(directory) and directory:
            album = self.client.create_album({"title": directory})
            self.albums = self.client.get_account_albums(USERNAME)
        album = [a for a in self.albums if a.title == directory][0]
        #if not response['is_dir']:
        #     raise IOError("%s exists and is not a directory." % directory)
        response = self._client_upload_from_fd(content, {"album": album.id, "name": name, "title": name}, False)
        return response["name"]

    def _client_upload_from_fd(self, fd, config=None, anon=True):
        """ use a file descriptor to perform a make_request """
        if not config:
            config = dict()

        contents = fd.read()
        b64 = base64.b64encode(contents)

        data = {
            'image': b64,
            'type': 'base64',
        }

        data.update({meta: config[meta] for meta in set(self.client.allowed_image_fields).intersection(list(config.keys()))})
        return self.client.make_request('POST', 'upload', data, anon)

    def delete(self, name):
        name = self._get_abs_path(name)
        self.client.delete_image(name)

    def exists(self, name):
        name = self._get_abs_path(name)
        if len([a for a in self.albums if a.title == name]) > 0:
            return True
        try:
            album = [a for a in self.albums if a.title == os.path.dirname(name)][0]
            images = self.client.get_album_images(album.id)
            metadata = self.client.get_image(name)
            if len([im for im in images if im.name == name]) > 0:
                logger.info(dir(metadata))
                return True
        except ImgurClientError as e:
            if e.status_code == 404: # not found
                return False
            raise e
        except IndexError as e:
            return False
        else:
            return True
        return False

    def listdir(self, path):
        path = self._get_abs_path(path)
        response = self.client.get_image(path)
        directories = []
        files = []
        for entry in response.get('contents', []):
            if entry['is_dir']:
                directories.append(os.path.basename(entry['path']))
            else:
                files.append(os.path.basename(entry['path']))
        return directories, files

    def size(self, path):
        cache_key = 'django-imgur-size:%s' % filepath_to_uri(path)
        size = cache.get(cache_key)

        if not size:
            directory = os.path.dirname(path)
            name = os.path.basename(path)
            album = [a for a in self.albums if a.title == directory][0]
            images = self.client.get_album_images(album.id)
            image = [im for im in images if im.name == path][0]
            size = self.client.get_image(image.id).size
            cache.set(cache_key, size)

        return size

    def url(self, path):
        cache_key = 'django-imgur-url:%s' % filepath_to_uri(path)
        url = cache.get(cache_key)

        if not url:
            directory = os.path.dirname(path)
            name = os.path.basename(path)
            album = [a for a in self.albums if a.title == directory][0]
            images = self.client.get_album_images(album.id)
            image = [im for im in images if im.name == path][0]
            url = self.client.get_image(image.id).link
            cache.set(cache_key, url)

        return url

    def get_available_name(self, name, max_length=None):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        #name = self._get_abs_path(name)
        #dir_name, file_name = os.path.split(name)
        #file_root, file_ext = os.path.splitext(file_name)
        ## If the filename already exists, add an underscore and a number (before
        ## the file extension, if one exists) to the filename until the generated
        ## filename doesn't exist.
        #count = itertools.count(1)
        #while self.exists(name):
        #    # file_ext includes the dot.
        #    name = os.path.join(dir_name, "%s_%s%s" % (file_root, count.next(), file_ext))

        return name

@deconstructible
class ImgurFile(File):
    def __init__(self, name, storage, mode):
        self._storage = storage
        self._mode = mode
        self._is_dirty = False
        self.file = StringIO()
        self.start_range = 0
        self._name = name

    @property
    def size(self):
        if not hasattr(self, '_size'):
            self._size = self._storage.size(self._name)
        return self._size

    def read(self, num_bytes=None):
        return requests.get(self._storage.url(self._name)).content

    def write(self, content):
        if 'w' not in self._mode:
            raise AttributeError("File was opened for read-only access.")
        self.file = StringIO(content)
        self._is_dirty = True

    def close(self):
        #if self._is_dirty:
        #    self._storage.client.put_file(self._name, self.file.getvalue())
        self.file.close()
