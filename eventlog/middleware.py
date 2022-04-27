from django.conf import settings
from django.http.response import HttpResponseRedirectBase
from django.urls import resolve
from eventlog.models import ViewEvent
import re

INGORE_SEGMENTS = {"api", "datatable", "citations_json"}
IGNORE_TEXT = {"detail", "metrics"}
IGNORE_VIEW_NAME_SUFFIX = {"_detail", "_autocomplete"}
IGNORE_PARAMETERS = {"csrfmiddlewaretoken"}

class PageViewsMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
        # don't record redirects, as the view that we're redirected to will be enough
        if not isinstance(response, HttpResponseRedirectBase):
            if hasattr(request, 'view_event'):
                if view_event := request.view_event:
                    view_event.save()

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        parts = request.path_info.split('/')
        if len(parts) > 1:
            if any(ignore_text in request.path_info for ignore_text in IGNORE_TEXT):
                return

            if not any(segment in INGORE_SEGMENTS for segment in parts):
                app = request.path_info.split('/')[1]  # FYI not guaranteed to be the app, but closest thing I can find that links it
                if app in settings.LOG_ACTIVITY_APPS:
                    if url_obj := resolve(request.path_info):
                        view_name = url_obj.view_name
                        if any(view_name.endswith(ignore_suffix) for ignore_suffix in IGNORE_VIEW_NAME_SUFFIX):
                            return

                        # but url_obj.app_name returns an empty string

                        all_params = {**view_kwargs}
                        for key, value in {**request.GET.dict(), **request.POST.dict()}.items():
                            key: str
                            value: str
                            if value.lower() == "true":
                                value = True
                            elif value.lower() == "false":
                                value = False
                            else:
                                try:
                                    value = int(value)
                                except ValueError:
                                    pass
                            all_params[key] = value

                        for ignore_me in IGNORE_PARAMETERS:
                            if ignore_me in all_params:
                                all_params.pop(ignore_me)

                        # hack to split up classification ID when it's in the form of "classification_id.modification_timestamp"
                        if classification_id := all_params.get("classification_id"):
                            if isinstance(classification_id, str) or isinstance(classification_id, float):
                                check_for_parts = str(classification_id)
                                parts = check_for_parts.split(".")
                                all_params["classification_id"] = int(parts[0])
                                if len(parts) > 1:
                                    all_params["modification_timestamp"] = float(parts[1])

                        request.view_event = ViewEvent(
                            user=request.user,
                            view_name=f"{app}:{url_obj.view_name}",
                            args=all_params,
                            path=request.get_full_path(),
                            method=request.method,
                            referer=request.headers.get('Referer')
                        )

        pass