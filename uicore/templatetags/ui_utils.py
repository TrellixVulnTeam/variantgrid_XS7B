import json
import re
import uuid
from html import escape
from typing import Optional, Any

from django import template
from django.contrib.auth.models import User
from django.db.models import Model
from django.forms.utils import ErrorList
from django.template.base import FilterExpression, kwarg_re
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import SafeString

from library.utils import diff_text
from variantgrid.perm_path import get_visible_url_names

register = template.Library()


@register.filter()
def append(suffix, postfix):
    # man django templates are lame that you need to make this
    # appends two things together to give you a string
    return_str = ""
    if suffix is not None:
        return_str += str(suffix)
    if postfix is not None:
        return_str += str(postfix)
    return return_str


@register.simple_tag(takes_context=True)
def update_django_messages(context):
    """
    Use when you've loaded messages in an ajax tab, and need to update the page messages with save etc messages
    """
    message_json = []
    if messages := context.get("messages"):
        for message in messages:
            tags = message.tags
            text = str(message)
            message_json.append({"tags": tags, "text": text})
    message_json_string = json.dumps(message_json)
    return SafeString(f"update_django_messages({message_json_string});")


# Taken from https://www.caktusgroup.com/blog/2017/05/01/building-custom-block-template-tag/
# how is this not built in?!
def parse_tag(token, parser):
    """
    Generic template tag parser.
    Returns a three-tuple: (tag_name, args, kwargs)
    tag_name is a string, the name of the tag.
    args is a list of FilterExpressions, from all the arguments that didn't look like kwargs,
    in the order they occurred, including any that were mingled amongst kwargs.
    kwargs is a dictionary mapping kwarg names to FilterExpressions, for all the arguments that
    looked like kwargs, including any that were mingled amongst args.
    (At rendering time, a FilterExpression f can be evaluated by calling f.resolve(context).)
    """
    # Split the tag content into words, respecting quoted strings.
    bits = token.split_contents()

    # Pull out the tag name.
    tag_name = bits.pop(0)

    # Parse the rest of the args, and build FilterExpressions from them so that
    # we can evaluate them later.
    args = []
    kwargs = {}
    for bit in bits:
        # Is this a kwarg or an arg?
        match = kwarg_re.match(bit)
        kwarg_format = match and match.group(1)
        if kwarg_format:
            key, value = match.groups()
            kwargs[key] = FilterExpression(value, parser)
        else:
            args.append(FilterExpression(bit, parser))

    return (tag_name, args, kwargs)


@register.tag(name='install-instructions')
def render_install_instructions(parser, token):
    tag_name, args, kwargs = parse_tag(token, parser)
    nodelist = parser.parse(('endinstall-instructions',))
    parser.delete_first_token()
    label = kwargs.get('label')
    installed = kwargs.get('installed')
    if not label:
        if len(args) > 0:
            label = args[0]
        else:
            raise ValueError("install-instructions required requires 'label' argument")

    return InstallInstructionsTag(nodelist, label=label, installed=installed)


class InstallInstructionsTag(template.Node):

    def __init__(self, nodelist, installed: FilterExpression, label: FilterExpression = None):
        self.nodelist = nodelist
        self.installed = installed
        self.label = label

    def render(self, context):
        if not context.request.user.is_superuser:
            return ""

        label_str = TagUtils.value_str(context, self.label)
        if not label_str:
            label_str = ""
            id_safe = str(uuid.uuid4()).replace("-", "_") + "_instructions"
        else:
            id_safe = re.sub(r"\W", "_", label_str).lower()

        div_css_classes = ["install-instructions", "collapse"]
        link_css_classes = ["toggle-link"]
        link_extra = ""
        if self.installed.resolve(context):
            link_css_classes.append("collapsed")
        else:
            link_extra = "aria-expanded='true'"
            div_css_classes.append("not-installed")
            div_css_classes.append("show")

        return f"""
        <div>
        <a class='{' '.join(link_css_classes)}' data-toggle='collapse' href='#{id_safe}' {link_extra}><i class="fas fa-key" aria-hidden="true"></i> {label_str} Install/Update Instructions</a>
        <div class='{' '.join(div_css_classes)}' id='{id_safe}'>
        {self.nodelist.render(context)}
        </div>
        </div>
        """


@register.tag(name='field_help')
def field_help(parser, token):
    tag_name, args, kwargs = parse_tag(token, parser)
    nodelist = parser.parse(('end_field_help',))
    parser.delete_first_token()
    return FieldHelpTag(nodelist)


class FieldHelpTag(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        return f'<div class="form-text text-muted">{output}</div>'


@register.tag(name='labelled')
def render_labelled(parser, token):
    tag_name, args, kwargs = parse_tag(token, parser)
    nodelist = parser.parse(('endlabelled',))
    parser.delete_first_token()
    return LabelledValueTag(nodelist,
                            id_prefix=kwargs.get('id_prefix'),
                            value_id=kwargs.get('id'),
                            label=kwargs.get('label'),
                            hint=kwargs.get('hint'),
                            label_css=kwargs.get('label_css'),
                            value_css=kwargs.get('value_css'),
                            row_css=kwargs.get('row_css'),
                            help=kwargs.get('help'),
                            admin_only=kwargs.get('admin_only'),
                            errors=kwargs.get('errors')
                            )


class LabelledValueTag(template.Node):
    def __init__(self, nodelist,
                 id_prefix: FilterExpression,
                 value_id: FilterExpression,
                 label: FilterExpression = None,
                 hint: FilterExpression = None,
                 label_css: FilterExpression = None,
                 value_css: FilterExpression = None,
                 row_css: FilterExpression = None,
                 help: FilterExpression = None,
                 admin_only: FilterExpression = None,
                 errors: FilterExpression = None):
        self.id_prefix = id_prefix
        self.nodelist = nodelist
        self.value_id = value_id
        self.label = label
        self.hint = hint
        self.label_css = label_css
        self.value_css = value_css
        self.row_css = row_css
        self.help = help
        self.admin_only = admin_only
        self.errors = errors

    id_regex = re.compile(r"id=[\"|'](.*?)[\"|']")
    big_zero = re.compile(r"^0([.]0+)?$")

    def render(self, context):
        prefix_id = TagUtils.value_str(context, self.id_prefix)
        value_id = TagUtils.value_str(context, self.value_id)
        complete_id = value_id
        if prefix_id and value_id:
            complete_id = f"{prefix_id}-{value_id}"

        label = TagUtils.value_str(context, self.label, (value_id.replace('_', ' ') if value_id else ""))
        if TagUtils.value_bool(context, self.admin_only):  # if admin only
            user: User = context.request.user
            if not user.is_superuser:
                return ""
            else:
                label = '<i class="fas fa-key" title="Admin only functionality"></i>' + label

        help_html = TagUtils.value_str(context, self.help)
        hint = TagUtils.value_str(context, self.hint)
        label_css = ""
        value_css = ""
        row_css = "form-group row mb-4 mb-md-3"

        if hint == "tiny":
            label_css = "col-12 col-md-6 text-md-right"
            value_css = "col-12 col-md-6 text-left align-self-center text-break"
        elif hint == "chunky":
            label_css = "col-12"
            value_css = "col-12 text-break"
        elif hint == "inline":
            label_css = "m-2 align-self-center"
            value_css = "m-2"
        else:
            label_css = "col-12 col-md-3 text-md-right align-self-center"
            value_css = "col-12 col-md-9 text-left text-break"

        label_css_extra = TagUtils.value_str(context, self.label_css, '')
        label_css = f"{label_css} {label_css_extra}".strip()

        value_css_extra = TagUtils.value_str(context, self.value_css, '')
        value_css = f"{value_css} {value_css_extra}".strip()

        row_css_extra = TagUtils.value_str(context, self.row_css, "")
        row_css = f"{row_css} {row_css_extra}".strip()

        output = self.nodelist.render(context)
        give_div_id = complete_id
        if not complete_id and not '<label' in output:
            if found_id := LabelledValueTag.id_regex.search(output):
                complete_id = found_id.group(1)
                give_div_id = False

        div_id = ""
        for_id = ""
        if complete_id:
            if give_div_id:
                div_id = f"id=\"{complete_id}\""
            for_id = f"for=\"{complete_id}\""

        if output in ("", "None"):
            output = "<span class=\"no-value\">-</span>"
        elif LabelledValueTag.big_zero.match(output):
            output = f"<span class=\"zero-value\">{output}</span>"

        errors: Optional[ErrorList]
        if filter_errors := self.errors:
            if errors := filter_errors.resolve(context):
                for error in errors:
                    output += f'<div class="text-danger">{error}</div>'
        help_tag = ""
        if help_html:
            help_html = help_html.replace('"', "'")  # Used double quotes around data-content
            help_tag = f' <i class="fas fa-duotone fa-info-circle hover-detail popover-hover-stay" data-toggle="popover" popover-header="{label}" data-html="true" data-placement="left" data-content="{help_html}"></i>'

        label_tag = f'<label {for_id} class="{label_css}">{label}{help_tag}</label>'
        content = f"""{label_tag}<div {div_id} class="{value_css}">{output}</div>"""

        if hint == "inline":
            return content

        content = f'<div class="{row_css}">{content}</div>'
        return content


@register.tag(name='modal')
def render_labelled(parser, token):
    tag_name, args, kwargs = parse_tag(token, parser)
    nodelist = parser.parse(('endmodal',))
    parser.delete_first_token()
    return ModalTag(
        nodelist,
        id=kwargs.get('id'),
        label=kwargs.get('label'),
        show_prefix=kwargs.get('show_prefix'),
        size=kwargs.get('size'),
        admin_only=kwargs.get('admin_only'),
        button=kwargs.get('button')
    )


class ModalTag(template.Node):
    def __init__(self, nodelist,
                 id: FilterExpression = None,
                 label: FilterExpression = None,
                 show_prefix: FilterExpression = None,
                 size: FilterExpression = None,
                 admin_only: FilterExpression = None,
                 button: FilterExpression = None):
        self.nodelist = nodelist
        self.id = id
        self.label = label
        self.show_prefix = show_prefix
        self.size = size
        self.admin_only = admin_only
        self.button = button

    def render(self, context):
        admin_only_bool = TagUtils.value_bool(context, self.admin_only)
        if admin_only_bool and not context.request.user.is_superuser:
            return ""

        # if an ID isn't provided, generate a uuid and make sure it starts with a letter
        id_str = escape(TagUtils.value_str(context, self.id) or "x" + str(uuid.uuid4()))
        label_str = TagUtils.value_str(context, self.label)
        output = self.nodelist.render(context)

        link = "<div>"
        if admin_only_bool:
            link += '<i class="fas fa-key" title="Admin only functionality"></i>'

        show_prefix_bool = TagUtils.value_bool(context, self.show_prefix, True)
        show_label_str = ("Show " if show_prefix_bool else "") + label_str

        if TagUtils.value_bool(context, self.button):
            link += f'<button class="btn btn-outline-primary" href="#{id_str}" data-toggle="modal">{show_label_str}</button>'
        else:
            link += f'<a href="#{id_str}" data-toggle="modal" class="modal-link">{"Show " if show_prefix_bool else ""}{label_str}</a>'

        link += "</div>"

        size_str = TagUtils.value_str(context, self.size, "xl")

        modal = \
            f"""
                <div id="{id_str}" class="modal" tabindex="-1">
                    <div class="modal-dialog modal-{size_str}">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">{label_str}</h5>
                                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                  <span aria-hidden="true">&times;</span>
                                </button>
                            </div>
                            {output}
                        </div>
                    </div>
                </div>
            """
        return link + modal


@register.filter()
def severity_icon(severity: str) -> str:
    if not severity:
        severity = 'I'
    severity = severity.upper()
    if severity.startswith('C'):  # critical
        return SafeString('<i class="fas fa-bomb text-danger"></i>')
    if severity.startswith('E'):  # error
        return SafeString('<i class="fas fa-exclamation-circle text-danger"></i>')
    if severity.startswith('W'):  # warning
        return SafeString('<i class="fas fa-exclamation-triangle text-warning"></i>')
    if severity.startswith('I'):  # info
        return SafeString('<i class="fas fa-info-circle text-info"></i>')
    if severity.startswith('D'):  # debug
        return SafeString('<i class="fas fa-key text-info"></i>')
    if severity.startswith('S'):  # success
        return SafeString('<i class="fas fa-check-circle text-success"></i>')
    # debug

    return SafeString('<i class="fas fa-question-circle text-secondary"></i>')


@register.filter()
def danger_badge(count: Optional[int]) -> str:
    """
    If count is None, does nothing
    If count is 0, shows a success badge with 0 in it
    If count is anything else, shown in a danger badge
    """
    if count is None:
        return ""
    if count == 0:
        return SafeString(' <span class="d-inline-block ml-1 badge badge-success">0</span>')
    return SafeString(f' <span class="d-inline-block ml-1 badge badge-danger">{count}</span>')


@register.filter()
def badge(count: Optional[int], status: Optional[str] = None) -> str:
    if count is None:
        return ""
    if status is None:
        status = "danger"

    render_status = status
    if count == 0:
        render_status = "info"
    return SafeString(f' <span class="d-inline-block ml-1 badge badge-{render_status}">{count}</span>')


@register.filter()
def success_badge(count: Optional[int]) -> str:
    if count is None:
        return ""
    if count == 0:
        return SafeString(' <span class="d-inline-block ml-1 badge badge-secondary">0</span>')
    return SafeString(f' <span class="d-inline-block ml-1 badge badge-success">{count}</span>')


@register.filter()
def checked(test: bool) -> str:
    if test:
        return SafeString('checked="checked"')
    return ''


@register.filter()
def boolean(test: bool) -> str:
    if test:
        return SafeString('<i class="text-success fas fa-check-circle" style="margin-top:4px"></i>')
    else:
        return SafeString('<i class="text-secondary fas fa-times-circle" style="margin-top:4px"></i>')


@register.filter()
def number(number: int, severity: Optional[str] = None) -> str:
    if number:
        result = SafeString(f'<span class="text-monospace" style="inline-block;margin-right:4px">{number:,}</span> ')
        if severity:
            result += severity_icon(severity)
        return result
    else:
        return SafeString('<span class="no-value">0</span>')


@register.filter()
def value(value: Any, no_value: Optional[str] = None) -> str:
    if isinstance(value, bool):
        return boolean(value)
    if value in ('', 0, '-'):
        return SafeString(f'<span class="no-value">{no_value or value}</span>')
    elif isinstance(value, int):
        return f'{value:,}'
    else:
        return value


@register.filter()
def secret(value: Any, length: int = -4) -> str:
    if value is None:
        return ""
    else:
        str_value = str(value)
        if length > 0:
            return SafeString("<span class='secret'>" + escape(str_value[0:length]) + "****</span>")
        elif length < 0:
            return SafeString("<span class='secret'>****" + escape(str_value[length:]) + "</span>")
        else:
            return str_value


@register.filter()
def segmented_text(text: str, divider: str = ':') -> str:
    if not text:
        return ""
    parts = text.split(divider)
    output = list()
    for segment in parts[:-1]:
        output.append(f"<span class='text-monospace text-small text-muted'>{escape(segment)}</span>")
        output.append(f"<span class='text-monospace text-muted'>{escape(divider)}</span>")
    output.append(parts[-1])
    output_str = "".join(output)
    return SafeString(f"<span>{output_str}</span>")


@register.filter()
def is_view_enabled(view_name: str) -> bool:
    return get_visible_url_names().get(view_name)


class TagUtils:

    @staticmethod
    def value(context, value: Any, default: Any = None) -> Optional[Any]:
        if isinstance(value, FilterExpression):
            resolved = value.resolve(context)
        else:
            resolved = value
        if resolved is None:
            resolved = default
        return resolved

    @staticmethod
    def value_str(context, value: Any, default: Any = None) -> Optional[str]:
        val = TagUtils.value(context, value, default)
        if val is not None:
            return str(val)
        return None

    @staticmethod
    def value_int(context, value: Any, default: Any = None) -> Optional[int]:
        val = TagUtils.value(context, value, default)
        if val is not None and val != '':
            try:
                return int(val)
            except TypeError:
                try:
                    return len(val)
                except TypeError:
                    pass
        return None

    @staticmethod
    def value_bool(context, value: Any, default: Any = None) -> Optional[bool]:
        val = TagUtils.value(context, value, default)
        if val is not None:
            return bool(val)
        return None


@register.filter()
def bytes(bytes: Optional[int]):
    if not bytes:
        return '-'
    else:
        unit = 'bytes'
        value = bytes
        if value > 1024:
            value = value / 1024.0
            unit = 'KB'
            if value > 1024:
                value = value / 1024.0
                unit = 'MB'
            value = round(value)
    return SafeString(f'<span class="text-monospace">{value:,}</span> {unit}')


@register.inclusion_tag(name="diff_text", filename="uicore/tags/diff_text.html")
def diff_text_html(a: str, b: str):
    return {"diffs": diff_text(a, b), "before": a, "after": b}


@register.inclusion_tag(takes_context=True, name="admin_link", filename="uicore/tags/admin_link.html")
def admin_link(context, object: Model):
    if not context.request.user.is_superuser:
        return {}
    url: Optional[str] = None
    if isinstance(object, Model):
        try:
            model = object._meta.model
            meta = model._meta
            path = f"admin:{meta.app_label}_{meta.model_name}_change"
            url = reverse(path, kwargs={"object_id": object.pk})
        except NoReverseMatch:
            pass
    return {"url": url}