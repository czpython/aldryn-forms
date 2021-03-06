# -*- coding: utf-8 -*-
from collections import defaultdict
from email.utils import formataddr
from functools import partial

from django.contrib import admin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response
from django.template.context import RequestContext
# we use SortedDict to remain compatible across python versions
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext, ugettext_lazy as _

from django_tablib.views import export

from .forms import FormDataExportForm, FormSubmissionExportForm
from .models import FormData, FormSubmission


class BaseFormSubmissionAdmin(admin.ModelAdmin):
    date_hierarchy = 'sent_at'
    list_display = ['__unicode__', 'sent_at', 'language']
    list_filter = ['name', 'language']
    readonly_fields = [
        'name',
        'get_data_for_display',
        'language',
        'sent_at',
        'get_recipients_for_display'
    ]
    export_form = None

    def has_add_permission(self, request):
        return False

    def get_data_for_display(self, obj):
        data = obj.get_form_data()
        html = render_to_string(
            template_name='admin/aldryn_forms/display/submission_data.html',
            dictionary={'data': data}
        )
        return html
    get_data_for_display.allow_tags = True
    get_data_for_display.short_description = _('data')

    def get_recipients(self, obj):
        recipients = obj.get_recipients()
        formatted = [formataddr((recipient.name, recipient.email))
                     for recipient in recipients]
        return formatted

    def get_recipients_for_display(self, obj):
        people_list = self.get_recipients(obj)
        html = render_to_string(
            template_name='admin/aldryn_forms/display/recipients.html',
            dictionary={'people': people_list}
        )
        return html
    get_recipients_for_display.allow_tags = True
    get_recipients_for_display.short_description = _('people notified')

    def get_urls(self):
        from django.conf.urls import patterns, url

        def pattern(regex, fn, name):
            args = [regex, self.admin_site.admin_view(fn)]
            return url(*args, name=self.get_admin_url(name))

        url_patterns = patterns('',
            pattern(r'export/$', self.form_export, 'export'),
        )

        return url_patterns + super(BaseFormSubmissionAdmin, self).get_urls()

    def get_admin_url(self, name):
        try:
            model_name = self.model._meta.model_name
        except AttributeError:
            # django <= 1.5 compat
            model_name = self.model._meta.module_name

        url_name = "%s_%s_%s" % (self.model._meta.app_label, model_name, name)
        return url_name

    def form_export(self, request):
        opts = self.model._meta
        app_label = opts.app_label
        context = RequestContext(request)
        form = self.export_form(request.POST or None)

        if form.is_valid():
            entries = form.get_queryset()

            if entries.exists():
                filename = form.get_filename()

                # A user can add fields to the form over time,
                # knowing this we use the latest form submission as a way
                # to get the latest form state, but this means that if a field
                # was removed then it will be ignored :(
                first_entry = entries.order_by('-sent_at')[0]

                # what follows is a bit of dark magic...
                # we call the export view in tablib with a headers dictionary, this dictionary
                # maps a key to a callable that gets passed a form submission instance and returns the value
                # for the field, we have to use a factory function in order to avoid a closure

                def clean_data(label, position):
                    def _clean_data(obj):
                        field = None
                        value = ''

                        try:
                            field = obj.get_form_data()[position]
                        except IndexError:
                            pass

                        if field and field.label == label:
                            # sanity check
                            # we need this to make sure that the field label and position remain constant
                            # otherwise we'll confuse users if a field was moved.
                            value = field.value
                        return value
                    return _clean_data

                fields = first_entry.get_form_data()

                # used to keep track of occurrences
                # in case a field with the same name appears multiple times in the form.
                occurrences = defaultdict(lambda: 1)
                headers = SortedDict()

                for position, field in enumerate(fields):
                    label = field.label

                    if label in headers:
                        occurrences[label] += 1
                        label = u'%s %s' % (label, occurrences[label])
                    headers[label] = clean_data(field.label, position)

                headers[ugettext('Language')] = 'language'
                headers[ugettext('Submitted on')] = 'sent_at'

                do_export = partial(
                    export,
                    request=request,
                    queryset=entries,
                    model=entries.model,
                    headers=headers,
                    filename=filename
                )

                try:
                    # Since django-tablib 3.1 the parameter is called file_type
                    response = do_export(file_type='xls')
                except TypeError:
                    response = do_export(format='xls')
                return response
            else:
                self.message_user(request, _("No records found"), level=messages.WARNING)
                export_url = 'admin:{}'.format(self.get_admin_url('export'))
                return redirect(export_url)
        else:
            context['errors'] = form.errors

        context.update({
            'adminform': form,
            'media': self.media + form.media,
            'has_change_permission': True,
            'opts': opts,
            'root_path': reverse('admin:index'),
            'current_app': self.admin_site.name,
            'app_label': app_label,
            'original': 'Export',
        })
        return render_to_response('admin/aldryn_forms/export.html', context)


class FormDataAdmin(BaseFormSubmissionAdmin):
    change_list_template = 'admin/aldryn_forms/formsubmission/change_list.html'
    export_form = FormDataExportForm
    readonly_fields = [
        'name',
        'data',
        'language',
        'sent_at',
        'get_recipients_for_display'
    ]

    def get_recipients(self, obj):
        return obj.get_recipients()


class FormSubmissionAdmin(BaseFormSubmissionAdmin):
    readonly_fields = BaseFormSubmissionAdmin.readonly_fields + ['form_url']
    export_form = FormSubmissionExportForm


admin.site.register(FormData, FormDataAdmin)
admin.site.register(FormSubmission, FormSubmissionAdmin)
