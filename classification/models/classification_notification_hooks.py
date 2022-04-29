from django.conf import settings
from django.dispatch import receiver
from django.urls import reverse

from classification.enums import SpecialEKeys
from classification.models import DiscordanceReport, discordance_change_signal, EvidenceKeyMap, UserPerspective, \
    DiscordanceReportSummary
from library.django_utils import get_url_from_view_path
from library.log_utils import NotificationBuilder
from snpdb.utils import LabNotificationBuilder


@receiver(discordance_change_signal, sender=DiscordanceReport)
def notify_discordance_change(discordance_report: DiscordanceReport, **kwargs):
    if settings.DISCORDANCE_ENABLED:
        send_discordance_notification(discordance_report=discordance_report)


def send_discordance_notification(discordance_report: DiscordanceReport):
    all_labs = discordance_report.involved_labs.keys()
    # all_lab_names = ", ".join(lab.name for lab in all_labs)
    report_url = get_url_from_view_path(
        reverse('discordance_report', kwargs={'discordance_report_id': discordance_report.id}),
    )
    clin_sig_key = EvidenceKeyMap.cached_key(SpecialEKeys.CLINICAL_SIGNIFICANCE)
    for lab in all_labs:
        notification = LabNotificationBuilder(lab=lab, message=f"Discordance Update (DR_{discordance_report.id})")

        user_perspective = UserPerspective.for_lab(lab=lab)
        report_summary = DiscordanceReportSummary(discordance_report=discordance_report, perspective=user_perspective)
        if resolution_text := discordance_report.resolution_text:
            notification.add_markdown(f"The below overlap is now marked as *{resolution_text}*")
        # notification.add_markdown(f"The labs {all_lab_names} are involved in the following discordance:")

        notification.add_field(label="Discordance Detected On", value=report_summary.date_detected_str)

        c_hgvs_str = "\n".join((str(chgvs) for chgvs in report_summary.c_hgvses))
        notification.add_field(label="c.HGVS", value=c_hgvs_str)

        sig_lab: DiscordanceReportSummary.LabClinicalSignificances
        for sig_lab in report_summary.lab_significances:
            notification.add_field(f"{sig_lab.lab} - classify this as", "\n".join([clin_sig_key.pretty_value(cs) for cs in sig_lab.clinical_significances]))

        withdrawn_labs = sorted({lab for lab, involvement in discordance_report.involved_labs.items() if involvement == DiscordanceReport.LabInvolvement.WITHDRAWN})
        for withdrawn_lab in withdrawn_labs:
            notification.add_field(label=f"{sig_lab.lab} - classify this as", value="_WITHDRAWN_")

        notification.add_markdown(f"Full details of the overlap can be seen here : <{report_url}>")
        notification.send()

    labs_notified = ", ".join(sorted([lab.name for lab in all_labs]))
    NotificationBuilder(message=f"Discordance Notification <{report_url}> sent to {labs_notified}")\
        .add_markdown(f":fire_engine: :email: Discordance Notification <{report_url}> sent to {labs_notified}").send()
