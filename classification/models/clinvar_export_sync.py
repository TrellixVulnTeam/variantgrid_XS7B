from enum import Enum, auto
from typing import TypedDict, Optional, Tuple

import requests
from django.conf import settings
from django.db import transaction
from lazy import lazy
from requests import Response

from classification.json_utils import JsonObjType
from classification.models import ClinVarExportBatch, ClinVarExportRequest, ClinVarExportRequestType, \
    ClinVarExportBatchStatus, ClinVarExportSubmission, ClinVarExportSubmissionStatus
from library.log_utils import report_message


class _ClinVarExportConfigDic(TypedDict):
    enabled: bool
    api_key: str


class ClinVarRequestExceptionType(Enum):
    OUR_DATA_ISSUE = auto()  # note this is
    API_KEY_ISSUE = auto()
    TOO_MANY_REQUESTS = auto()
    CLINVAR_SERVER_ISSUE = auto()
    RESPONSE_MISSING_KEY_DATA = auto()


class ClinVarRequestException(Exception):

    def __init__(self, exception_type: ClinVarRequestExceptionType, message: Optional[str] = None):
        super().__init__(message)
        self.exception_type = exception_type
        self.message = message

    def __str__(self):
        if self.exception_type == ClinVarRequestExceptionType.OUR_DATA_ISSUE:
            return "Our data format was rejected by ClinVar - internal admin review required"
        elif self.exception_type == ClinVarRequestExceptionType.API_KEY_ISSUE:
            return "API key is not provided correctly or not authorised - internal admin review required"
        elif self.exception_type == ClinVarRequestExceptionType.TOO_MANY_REQUESTS:
            return "Too many requests, need to wait before trying again"
        elif self.exception_type == ClinVarRequestExceptionType.CLINVAR_SERVER_ISSUE:
            return "ClinVar server returned an error code, maybe wait before trying again"
        elif self.exception_type == ClinVarRequestExceptionType.RESPONSE_MISSING_KEY_DATA:
            return self.message

    @staticmethod
    def raise_for_status_code(code: int):
        if code == 400:
            raise ClinVarRequestException(exception_type=ClinVarRequestExceptionType.OUR_DATA_ISSUE)
        elif code == 401:
            raise ClinVarRequestException(exception_type=ClinVarRequestExceptionType.API_KEY_ISSUE)
        elif code == 429:
            raise ClinVarRequestException(exception_type=ClinVarRequestExceptionType.TOO_MANY_REQUESTS)
        elif 500 <= code <= 599:
            raise ClinVarRequestException(exception_type=ClinVarRequestExceptionType.CLINVAR_SERVER_ISSUE)
        # all good
        return True


class ClinVarResponseOutcome(Enum):
    ASK_AGAIN_NOW = auto()
    ASK_AGAIN_LATER = auto()
    COMPLETE = auto()


class ClinVarExportSync:

    @lazy
    def _config(self) -> _ClinVarExportConfigDic:
        return settings.CLINVAR_EXPORT or {"enabled": False, "test": True, "api_key": None}

    @property
    def is_enabled(self) -> bool:
        return self._config.get('enabled')

    @property
    def is_test(self) -> bool:
        return self._config.get('test')

    @property
    def api_key(self) -> Optional[str]:
        return self._config.get('api_key')

    def _send_data(self,
                   batch: ClinVarExportBatch,
                   request_type: ClinVarExportRequestType,
                   url: str,
                   json_data: Optional[JsonObjType] = None) -> ClinVarExportRequest:
        if not self.is_enabled or not self.api_key:
            raise ValueError("ClinVarExports is not enabled or not ClinVarExport key is provided")
        response: Response = requests.request(
            url=url,
            method="POST",
            headers={
                "Content-type": "application/json",
                "SP-API-KEY": self.api_key
            },
            json=json_data
        )
        response_json: Optional[JsonObjType] = None
        try:
            response_json = response.json()
        except ValueError:
            # ValueError implies
            pass

        return ClinVarExportRequest.objects.create(
            submission_batch=batch,
            request_type=request_type,
            request_json=json_data,
            url=url,
            response_json=response_json,
            response_status_code=response.status_code
        )

    def next_request(self, batch: ClinVarExportBatch) -> Tuple[ClinVarExportRequest, ClinVarResponseOutcome]:
        clinvar_request: ClinVarExportRequest
        if not batch.submission_identifier:
            batch.status = ClinVarExportBatchStatus.UPLOADING
            batch.save()
            url = "https://submit.ncbi.nlm.nih.gov/api/v1/submissions/"
            if self.is_test:
                url += "?dry-run=true"

            clinvar_request = self._send_data(
                batch=batch,
                request_type=ClinVarExportRequestType.INITIAL_SUBMISSION,
                json_data=batch.to_json(),
                url=url)

        else:
            if not self.is_test:
                raise ValueError("ClinVarExport test is set to True, but attempted to perform an action other than initial submission")

            if not batch.file_url:
                clinvar_request = self._send_data(
                    batch=batch,
                    request_type=ClinVarExportRequestType.POLLING_SUBMISSION,
                    url=f"https://submit.ncbi.nlm.nih.gov/api/v1/submissions/{batch.submission_identifier}/actions/")
            else:
                clinvar_request = self._send_data(
                    batch=batch,
                    request_type=ClinVarExportRequestType.RESPONSE_FILES,
                    url=batch.file_url)

        handle_outcome = self.handle_request_response(clinvar_request)
        batch.refresh_from_db()  # just in case we've indirectly modified it
        return clinvar_request, handle_outcome

    def _handle_initial_submission(self, clinvar_request: ClinVarExportRequest) -> ClinVarResponseOutcome:

        if clinvar_request.response_status_code in {200, 201} and \
                (response_json := clinvar_request.response_json) and \
                (actions := response_json.get('actions')) and \
                (submission_identifier := actions[0].get('id')):
            clinvar_request.submission_batch.submission_identifier = submission_identifier
            clinvar_request.submission_batch.save()
            return ClinVarResponseOutcome.ASK_AGAIN_LATER

        elif clinvar_request.response_status_code == 204:
            # means it's just test? not really sure what the best thing to do about this is
            clinvar_request.submission_batch.status = ClinVarExportBatchStatus.SUBMITTED
            clinvar_request.submission_batch.save()
            return ClinVarResponseOutcome.COMPLETE
        else:
            raise ValueError(f"Processing of JSON for request {clinvar_request.pk} couldn't find actions[0].id submission ID")

    def _handle_polling(self, clinvar_request: ClinVarExportRequest) -> ClinVarResponseOutcome:
        if (response_json := clinvar_request.response_json) and (actions := response_json.get("actions")):
            for action_json in actions:
                for response_json in action_json.get("responses"):
                    status = response_json.get('status')
                    if status == "processing":
                        return ClinVarResponseOutcome.ASK_AGAIN_LATER
                    elif files := response_json.get("files"):
                        for file_json in files:
                            if url := file_json.get('url'):
                                clinvar_request.submission_batch.file_url = url
                                clinvar_request.submission_batch.save()
                                # don't need to wait before requesting the file
                                return ClinVarResponseOutcome.ASK_AGAIN_NOW

        # couldn't find "processing" or still in progress, this is unexpected
        raise ValueError(f"Processing of JSON for request {clinvar_request.pk} couldn't find status of processing or file")

    def _handle_response_file(self, clinvar_request: ClinVarExportRequest) -> ClinVarResponseOutcome:
        if (response_json := clinvar_request.response_json) and (submissions_json := response_json.get('submissions')):

            submission_set = clinvar_request.submission_batch.clinvarexportsubmission_set

            for submission_json in submissions_json:
                identifiers_json = submission_json.get("identifiers")

                clinvar_export_submission: ClinVarExportSubmission
                local_key = identifiers_json.get("localKey")
                if clinvar_export_submission := submission_set.filter(localKey=local_key).first():
                    clinvar_export = clinvar_export_submission.clinvar_export
                    # TODO, do we want to do anything with the submission? e.g. around status?

                    if scv := identifiers_json.get("clinvarAccession"):
                        clinvar_export.scv = scv
                        clinvar_export.save()

                        clinvar_export_submission.scv = scv

                    new_status: Optional[ClinVarExportSubmissionStatus] = None
                    if processing_status := submission_json.get("processingStatus"):
                        if processing_status == "Success":
                            clinvar_export_submission.status = ClinVarExportSubmissionStatus.SUCCESS
                        elif processing_status == "Error":
                            clinvar_export_submission.status = ClinVarExportSubmissionStatus.ERROR
                        # expect statuses of Success or Error

                    clinvar_export_submission.response_json = submission_json
                    if new_status:
                        clinvar_export_submission.status = new_status
                    else:
                        report_message(f"ClinVarExportSubmission - could not determine status", level='error', extra_data={"target": clinvar_export_submission.pk})
                    clinvar_export_submission.save()
                else:
                    report_message(f"ClinVarExportRequest - could not find localKey", level='error', extra_data={"target": clinvar_request.pk, "localKey": local_key})
            else:
                report_message(f"Expected submissions in ClinVarRequest", level='error', extra_data={"target": clinvar_request.pk})

            clinvar_request.submission_batch.status = ClinVarExportBatchStatus.SUBMITTED
            clinvar_request.submission_batch.save()

            return ClinVarResponseOutcome.COMPLETE

    def handle_request_response(self, clinvar_request: ClinVarExportRequest) -> ClinVarResponseOutcome:
        if clinvar_request.handled:
            raise ValueError("ClinVarExport has already been handled")
        try:
            ClinVarRequestException.raise_for_status_code(clinvar_request.response_status_code)
        except ClinVarRequestException as clinvar_except:
            if clinvar_except.exception_type == ClinVarRequestExceptionType.OUR_DATA_ISSUE:
                submission_batch = clinvar_request.submission_batch
                submission_batch.status = ClinVarExportBatchStatus.REJECTED
                submission_batch.save()
            raise

        return self._handle_request_response_extra(clinvar_request)

    @transaction.atomic()
    def _handle_request_response_extra(self, clinvar_request: ClinVarExportRequest) -> ClinVarResponseOutcome:
        try:
            if clinvar_request.request_type == ClinVarExportRequestType.INITIAL_SUBMISSION:
                return self._handle_initial_submission(clinvar_request)

            elif clinvar_request.request_type == ClinVarExportRequestType.POLLING_SUBMISSION:
                return self._handle_polling(clinvar_request)

            elif clinvar_request.request_type == ClinVarExportRequestType.RESPONSE_FILES:
                return self._handle_response_file(clinvar_request)

            else:
                raise ValueError(f'Unexpected request type "{clinvar_request.request_type}"')
        finally:
            clinvar_request.handled = True
            clinvar_request.save()


clinvar_export_sync = ClinVarExportSync()
