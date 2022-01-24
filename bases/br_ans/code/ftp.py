from typing import Generator, Tuple
from datetime import datetime
from ftputil import FTPHost
import tempfile
import zipfile
from io import BytesIO
import logging

logger = logging.getLogger()

class ReaderFtp:
    host: FTPHost

    @property
    def path(self):
        return self.host.path

    def __init__(self, uri):
        self.host = FTPHost(uri, 'anonymous')

    def is_newer(self, path: str, time: datetime):
        file_mtime = datetime.fromtimestamp(self.host.path.getmtime(path))
        return file_mtime > time

    def is_file(self, path: str):
        return self.host.path.isfile(path)

    def list_newer(self, basepath: str = '.', time: datetime = datetime.fromtimestamp(0)):
        logger.info(f'list newer {basepath}')
        for path in  self.host.listdir(basepath)[::-1]:
            complete_path = self.host.path.join(basepath, path)
            if self.is_newer(complete_path, time):
                yield complete_path

    def list_recursive_newer(self, basepath: str = '.', time: datetime = datetime.fromtimestamp(0)):
        for path in  self.list_newer(basepath, time):
            if self.is_file(path):
                yield path
            else:
                yield from self.list_recursive_newer(path, time)

    def read(self, path: str) -> bytes:
        filename, file_extension = self.host.path.splitext(self.host.path.basename(path))
        with tempfile.NamedTemporaryFile(prefix=filename, suffix=file_extension) as tmp:
            logger.info(f'ftp download {path}')
            self.host.download(path, tmp.name)
            return BytesIO(tmp.read())


    def read_csv_zip(self, path) -> Tuple[str, bytes]:
        zfile = self.read(path)
        with zipfile.ZipFile(zfile) as zref:
                for filename in zref.namelist():
                    if not filename.endswith('.csv'):
                        continue
                    path = self.host.path.join(self.host.path.dirname(path), filename)
                    return path, BytesIO(zref.read(filename))
