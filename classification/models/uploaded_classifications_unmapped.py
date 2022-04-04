import contextlib
from abc import ABC, abstractmethod
from os import PathLike
from pathlib import Path
from typing import Iterator, Union, Optional, Dict, List, Tuple
from zipfile import ZipFile

from django.contrib.auth.models import User
from django.db import models
from lazy import lazy
from model_utils.models import TimeStampedModel
from six import BytesIO

from snpdb.models import Lab
import re


class UploadedFileLabStatus(models.TextChoices):
    Pending = 'P', 'Pending'
    Processed = 'MP', 'Processed'
    Error = 'E', 'Error'

    Mapping = "M", "Mapping"
    Importing = "I", "Importing"


# e.g. https://shariant-temp.s3.amazonaws.com/test/hello.txt?AWSAccessKeyId=ASFDWEROMDEOLNZA&Signature=mxBuRkSDFDHgwZyfZYfxQPXE%3D&Expires=1647392831
UPLOADED_FILE_RE = re.compile(r"https:\/\/(?P<bucket>.*?)\.s3\.amazonaws\.com/(?P<file>.*?)(?:\?AWSAccessKeyId.*|$)")


class FileData(ABC):

    @abstractmethod
    def _data_handle(self):
        """
        Return handle to an open file or storage, anything that you can call .read() on
        """
        pass

    @property
    @abstractmethod
    def filename(self) -> str:
        pass

    @contextlib.contextmanager
    def open(self):
        handle = self._data_handle()
        try:
            yield handle
        finally:
            handle.close()

    def stream(self) -> Iterator[bytes]:
        handle = self._data_handle()
        while buffer := handle.read(4096):
            yield buffer
        handle.close()

    def download_to(self, filename: Union[str, PathLike]):
        with open(filename, 'wb') as output_file:
            with self.open() as input_file:
                output_file.write(input_file.read())

    def download_to_dir(self, download_dir: Path, extract_zip: bool = False):
        # this is pretty inefficient
        if extract_zip and self.filename.endswith(".zip"):
            with self.open() as input_file:
                zippy = ZipFile(BytesIO(input_file.read()))
                zippy.extractall(path=download_dir)
        else:
            with open(download_dir / self.filename, 'wb') as output_file:
                with self.open() as input_file:
                    output_file.write(input_file.read())


class FileDataS3(FileData):

    def __init__(self, bucket: str, file: str):
        self.bucket = bucket
        self.file = file

    @property
    def filename(self) -> str:
        segments = self.file.split("/")
        return segments[-1]

    def _data_handle(self):
        from storages.backends.s3boto3 import S3Boto3Storage
        media_storage = S3Boto3Storage(bucket_name=self.bucket)
        return media_storage.open(self.file)


class UploadedClassificationsUnmapped(TimeStampedModel):
    class Meta:
        verbose_name = "Classification upload file"

    url = models.TextField()
    filename = models.TextField()
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    comment = models.TextField(default="", blank=True)
    validation_summary = models.JSONField(null=True, blank=True)
    validation_list = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=2, choices=UploadedFileLabStatus.choices, default=UploadedFileLabStatus.Pending)

    @lazy
    def file_data(self) -> FileData:
        if match := UPLOADED_FILE_RE.match(self.url):
            bucket = match.group('bucket')
            file = match.group('file')
            return FileDataS3(bucket=bucket, file=file)
        raise ValueError(f"Don't know how to download {self.url}")

    @property
    def message_counts(self) -> Optional[List[Tuple[str, int]]]:
        if summary := self.validation_summary:
            entries = [(key, value) for key, value in summary.get("message_counts").items()]
            return sorted(entries, key=lambda x: x[0])

    @property
    def validation_summary_properties(self) -> Optional[List[Tuple[str, Union[int, str]]]]:
        if summary := self.validation_summary:
            entries = [(key, value) for key, value in summary.items() if isinstance(value, (str, int))]
            return sorted(entries, key=lambda x: x[0])