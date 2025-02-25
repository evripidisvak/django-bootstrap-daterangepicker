import json
import re
from collections import OrderedDict
from datetime import date, datetime, timedelta

from dateutil import relativedelta
from django import forms
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.core.serializers.json import DjangoJSONEncoder

__all__ = [
    "DatePickerWidget",
    "DateRangeWidget",
    "DateTimeRangeWidget",
    "add_month",
    "common_dates",
]

format_to_js = {
    "%m": "MM",
    "%d": "DD",
    "%Y": "YYYY",
    "%y": "YY",
    "%B": "MMMM",
    "%b": "MMM",
    "%M": "mm",
    "%H": "HH",
    "%I": "hh",
    "%p": "A",
    "%S": "ss",
}

format_to_js_re = re.compile(r"(?<!\w)(" + "|".join(format_to_js.keys()) + r")\b")


def add_month(start_date, months):
    return start_date + relativedelta.relativedelta(months=months)


def common_dates(date_format, start_date=date.today()):
    one_day = timedelta(days=1)
    return OrderedDict(
        [
            (
                "Σήμερα",
                (start_date.strftime(date_format), start_date.strftime(date_format)),
            ),
            (
                "Εχθές",
                (
                    (start_date - one_day).strftime(date_format),
                    (start_date - one_day).strftime(date_format),
                ),
            ),
            (
                "Τρέχουσα εβδομάδα",
                (
                    (start_date - timedelta(days=start_date.weekday())).strftime(
                        date_format
                    ),
                    start_date.strftime(date_format),
                ),
            ),
            (
                "Προηγούμενη εβδομάδα",
                (
                    (start_date - timedelta(days=start_date.weekday() + 7)).strftime(
                        date_format
                    ),
                    (start_date - timedelta(days=start_date.weekday() + 1)).strftime(
                        date_format
                    ),
                ),
            ),
            (
                "7 τελευταίες ημέρες",
                (
                    (start_date - timedelta(days=7)).strftime(date_format),
                    start_date.strftime(date_format),
                ),
            ),
            (
                "Τρέχων μήνας",
                (
                    (start_date.replace(day=1)).strftime(date_format),
                    start_date.strftime(date_format),
                ),
            ),
            (
                "Προηγούμενος μήνας",
                (
                    (add_month(start_date.replace(day=1), -1)).strftime(date_format),
                    (start_date.replace(day=1) - one_day).strftime(date_format),
                ),
            ),
            (
                "Τρίμηνο",
                (
                    (add_month(start_date, -3)).strftime(date_format),
                    start_date.strftime(date_format),
                ),
            ),
            (
                "Έτος",
                (
                    (add_month(start_date, -12)).strftime(date_format),
                    start_date.strftime(date_format),
                ),
            ),
        ]
    )


def common_datetimes(date_format, start_date=datetime.today()):
    one_day = timedelta(days=1)
    return OrderedDict(
        [
            (
                "Σήμερα",
                (
                    start_date.strftime(date_format),
                    start_date.replace(
                        hour=23, minute=59, second=59, microsecond=999999
                    ).strftime(date_format),
                ),
            ),
            (
                "Εχθές",
                (
                    (start_date - one_day).strftime(date_format),
                    (start_date - one_day)
                    .replace(hour=23, minute=59, second=59, microsecond=999999)
                    .strftime(date_format),
                ),
            ),
            (
                "Εχθές απόγευμα",
                (
                    (start_date - one_day)
                    .replace(hour=18, minute=00, second=00, microsecond=00)
                    .strftime(date_format),
                    (start_date - one_day)
                    .replace(hour=21, minute=00, second=00, microsecond=00)
                    .strftime(date_format),
                ),
            ),
            (
                "Τρέχουσα εβδομάδα",
                (
                    (start_date - timedelta(days=start_date.weekday())).strftime(
                        date_format
                    ),
                    start_date.replace(
                        hour=23, minute=59, second=59, microsecond=999999
                    ).strftime(date_format),
                ),
            ),
            (
                "Προηγούμενη εβδομάδα",
                (
                    (start_date - timedelta(days=start_date.weekday() + 7)).strftime(
                        date_format
                    ),
                    (start_date - timedelta(days=start_date.weekday() + 1))
                    .replace(hour=23, minute=59, second=59, microsecond=999999)
                    .strftime(date_format),
                ),
            ),
            (
                "7 τελευταίες ημέρες",
                (
                    (start_date - timedelta(days=7)).strftime(date_format),
                    start_date.replace(
                        hour=23, minute=59, second=59, microsecond=999999
                    ).strftime(date_format),
                ),
            ),
            (
                "Τρέχων μήνας",
                (
                    (start_date.replace(day=1)).strftime(date_format),
                    start_date.replace(
                        hour=23, minute=59, second=59, microsecond=999999
                    ).strftime(date_format),
                ),
            ),
            (
                "Προηγούμενος μήνας",
                (
                    (add_month(start_date.replace(day=1), -1)).strftime(date_format),
                    (start_date.replace(day=1) - one_day)
                    .replace(hour=23, minute=59, second=59, microsecond=999999)
                    .strftime(date_format),
                ),
            ),
            (
                "Τρίμηνο",
                (
                    (add_month(start_date, -3)).strftime(date_format),
                    start_date.replace(
                        hour=23, minute=59, second=59, microsecond=999999
                    ).strftime(date_format),
                ),
            ),
            (
                "Έτος",
                (
                    (add_month(start_date, -12)).strftime(date_format),
                    start_date.replace(
                        hour=23, minute=59, second=59, microsecond=999999
                    ).strftime(date_format),
                ),
            ),
        ]
    )


class DateRangeWidget(forms.TextInput):
    format_key = "DATE_INPUT_FORMATS"
    template_name = "bootstrap_daterangepicker/daterangepicker.html"

    def __init__(
        self,
        picker_options=None,
        attrs=None,
        format=None,
        separator=" - ",
        clearable=False,
    ):
        super(DateRangeWidget, self).__init__(attrs)

        self.separator = separator
        self.format = format
        self.picker_options = picker_options or {}
        self.clearable_override = clearable

        if "class" not in self.attrs:
            self.attrs["class"] = "form-control"

    def clearable(self):
        """clearable if the field is an optional field or if explicitly set as clearable"""
        # Can't be set on init as is_required is set *after* widget initialisation
        # https://github.com/django/django/blob/d5f4ce9849b062cc788988f2600359dc3c2890cb/django/forms/fields.py#L100
        return not self.is_required or self.clearable_override

    def _get_format(self):
        return self.format or formats.get_format(self.format_key)[0]

    def _format_date_value(self, value):
        return formats.localize_input(value, self._get_format())

    def format_value(self, value):
        if isinstance(value, tuple):
            return (
                self._format_date_value(value[0])
                + self.separator
                + self._format_date_value(value[1])
            )
        else:
            return value

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        date_format = format_to_js_re.sub(
            lambda m: format_to_js[m.group()], self._get_format()
        )

        default_picker_options = {
            "locale": {
                "format": date_format,
            }
        }

        if self.clearable():
            default_picker_options["autoUpdateInput"] = False
            default_picker_options["locale"]["cancelLabel"] = _("Clear")

        # Rename for clarity
        picker_options = default_picker_options
        picker_options.update(self.picker_options)

        # If range is a dict of functions, call with 'today' as argument
        if "ranges" in picker_options:
            ranges = OrderedDict(picker_options["ranges"])
            for k, v in ranges.items():
                if callable(v):
                    ranges[k] = v(datetime.today())
            picker_options["ranges"] = ranges

        # Update context for template
        context["widget"]["picker"] = {
            "options": {
                "json": mark_safe(json.dumps(picker_options, cls=DjangoJSONEncoder)),
                "python": picker_options,
            },
            "clearable": self.clearable(),
            "separator": self.separator,
        }

        return context


class DateTimeRangeWidget(DateRangeWidget):
    format_key = "DATETIME_INPUT_FORMATS"

    def __init__(self, *args, **kwargs):
        super(DateTimeRangeWidget, self).__init__(*args, **kwargs)

        if "timePicker" not in self.picker_options:
            self.picker_options["timePicker"] = True


class DatePickerWidget(DateRangeWidget):
    def __init__(self, *args, **kwargs):
        super(DatePickerWidget, self).__init__(*args, **kwargs)

        if "singleDatePicker" not in self.picker_options:
            self.picker_options["singleDatePicker"] = True
