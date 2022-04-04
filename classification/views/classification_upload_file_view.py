import os
import re
import django
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpResponseRedirect, HttpRequest, StreamingHttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from classification.models.uploaded_classifications_unmapped import UploadedClassificationsUnmapped, UploadedFileLabStatus
from library.django_utils import get_url_from_view_path
from library.log_utils import NotificationBuilder
from library.utils import filename_safe
from snpdb.models import Lab, UserSettings
from snpdb.views.datatable_view import DatatableConfig, RichColumn, SortOrder


class UploadedClassificationsUnmappedColumns(DatatableConfig[UploadedClassificationsUnmapped]):

    def __init__(self, request):
        super().__init__(request)

        self.rich_columns = [
            RichColumn(key="id", label="ID", orderable=True, default_sort=SortOrder.DESC),
            RichColumn(key="filename", orderable=True, client_renderer='fileDownloaderRenderer'),
            RichColumn(key="created", label='Created', orderable=True, client_renderer='TableFormat.timestamp'),
            RichColumn(key="status", label="Status", orderable=True, renderer=lambda x: UploadedFileLabStatus(x["status"]).label),
            RichColumn(key="comment", client_renderer='TableFormat.text')
        ]

    def get_initial_queryset(self) -> QuerySet[UploadedClassificationsUnmapped]:
        if lab_id := self.get_query_param("lab_id"):
            return UploadedClassificationsUnmapped.objects.filter(lab=int(lab_id))
        else:
            raise ValueError("Must pass in lab_id")


def download_classification_unmapped_fiile(request: HttpRequest, upload_file_lab_id: int):
    user = request.user
    record = UploadedClassificationsUnmapped.objects.filter(pk=upload_file_lab_id).filter(lab__in=Lab.valid_labs_qs(user, admin_check=True)).first()
    if not record:
        raise PermissionDenied("You do not have access to this file")

    file_info = record.file_data()

    response = StreamingHttpResponse(file_info.stream(), content_type='streaming_content')
    response['Content-Disposition'] = f'attachment; filename="{file_info.filename()}"'
    return response


class UploadedClassificationsUnmappedView(View):

    def get(self, request, **kwargs):
        user: User = request.user
        if lab_id := kwargs.get('lab_id'):
            selected_lab = Lab.valid_labs_qs(user=user, admin_check=True).get(pk=lab_id)
            return render(request, 'classification/classification_upload_file_unmapped.html', {
                "selected_lab": selected_lab
            })
        else:
            selected_lab = UserSettings.get_for_user(user).default_lab_safe()
            return HttpResponseRedirect(reverse("classification_upload_unmapped_lab", kwargs={"lab_id": selected_lab.pk}))

    def post(self, requests, **kwargs):
        # lazily have s3boto3 requirements

        django.utils.encoding.force_text1 = django.utils.encoding.force_str
        django.utils.encoding.smart_text = django.utils.encoding.smart_str

        from storages.backends.s3boto3 import S3Boto3Storage
        lab_id: int
        try:
            lab_id = kwargs.get('lab_id')
            if not lab_id:
                raise ValueError("Lab required")

            lab = Lab.objects.get(pk=lab_id)
            if not lab.is_member(user=requests.user, admin_check=True):
                raise PermissionError("User does not have access to lab")

            protocol, path = lab.upload_location.split("://", maxsplit=1)

            if protocol == "s3":
                parts = path.split("/", maxsplit=1)
                bucket = parts[0]
                file_directory_within_bucket = parts[1] if len(parts) > 1 else None

                file_obj = requests.FILES.get('file')
                if not file_obj:
                    raise ValueError("No Upload File attached")

                # if not file_obj.name.endswith('.json'):
                #    raise ValueError("Only MVL .json uploads are supported")

                # do your validation here e.g. file size/type check

                # organize a path for the file in bucket
                file_path_within_bucket: str
                # synthesize a full file path; note that we included the filename
                if file_directory_within_bucket:
                    file_path_within_bucket = os.path.join(
                        file_directory_within_bucket,
                        filename_safe(file_obj.name)
                    )
                else:
                    file_path_within_bucket = filename_safe(file_obj.name)

                media_storage = S3Boto3Storage(bucket_name=bucket)

                media_storage.save(file_path_within_bucket, file_obj)
                file_url = media_storage.url(file_path_within_bucket)

                status = UploadedFileLabStatus.Pending
                user: User = requests.user
                uploaded_file = UploadedClassificationsUnmapped.objects.create(
                    url=file_url,
                    filename=file_obj.name,
                    user=requests.user,
                    lab=lab,
                    status=status
                )

                admin_url = get_url_from_view_path(f"/admin/classification/uploadedfilelab/{uploaded_file.pk}/change")
                notifier = NotificationBuilder(
                    message="File Uploaded"
                ).add_header(":file_folder: File Uploaded").\
                    add_field("For Lab", lab.name).\
                    add_field("By User", user.username).\
                    add_field("Path", "s3://" + bucket + "/" + file_path_within_bucket).\
                    add_markdown(f"*URL:* <{admin_url}>")

                # Soon going to replace this with automated import
                notifier.add_markdown("This file will need to be handled manually!")
                messages.add_message(requests, messages.INFO,
                                     f"File {file_obj.name} uploaded for {lab.name}. This file will be uploaded after manual review.")

                notifier.send()

            else:
                raise ValueError("Only s3 storage is currently supported for lab uploads")
        except ValueError as ve:
            messages.add_message(requests, messages.ERROR, str(ve))

        if lab_id := lab_id:
            return HttpResponseRedirect(reverse("classification_upload_unmapped_lab", kwargs={"lab_id": lab_id}))
        else:
            return HttpResponseRedirect(reverse("classification_upload_unmapped"))