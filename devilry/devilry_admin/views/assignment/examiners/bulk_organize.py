from __future__ import unicode_literals

import math
import random

from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy
from django.views.generic import TemplateView
from django_cradmin import crapp

from devilry.apps.core.models import Examiner, RelatedExaminer
from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_cradmin import devilry_listbuilder


class SelectMethodView(TemplateView):
    template_name = 'devilry_admin/assignment/examiners/bulk_organize/select_method.django.html'


class RandomOrganizeForm(groupview_base.SelectedGroupsForm):
    selected_relatedexaminers_invalid_choice_message = ugettext_lazy(
            'You must select at least two examiners.')
    selected_relatedexaminers = forms.ModelMultipleChoiceField(
        queryset=RelatedExaminer.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        label=ugettext_lazy('Select at least two examiners:'),
        required=False
    )

    def __make_relatedexaminer_choices(self, relatedexaminerqueryset):
        return [
            (relatedexaminer.id, relatedexaminer.user.get_full_name())
            for relatedexaminer in relatedexaminerqueryset]

    def __init__(self, *args, **kwargs):
        selectable_relatedexaminers_queryset = kwargs.pop('selectable_relatedexaminers_queryset')
        super(RandomOrganizeForm, self).__init__(*args, **kwargs)
        self.fields['selected_relatedexaminers'].queryset = selectable_relatedexaminers_queryset
        self.fields['selected_relatedexaminers'].choices = self.__make_relatedexaminer_choices(
            relatedexaminerqueryset=selectable_relatedexaminers_queryset)

    def clean(self):
        cleaned_data = super(RandomOrganizeForm, self).clean()
        selected_relatedexaminers = cleaned_data.get("selected_relatedexaminers")
        if selected_relatedexaminers.count() < 2:
            self.add_error(
                'selected_relatedexaminers',
                self.selected_relatedexaminers_invalid_choice_message)


class RandomOrganizeTargetRenderer(devilry_listbuilder.assignmentgroup.GroupTargetRenderer):
    def get_with_items_title(self):
        return ugettext_lazy('Select at least two students:')

    def get_submit_button_text(self):
        return ugettext_lazy('Randomly assign selected students to selected examiners')

    def get_field_layout(self):
        return [
            'selected_relatedexaminers'
        ]


class RandomView(groupview_base.BaseMultiselectView):
    filterview_name = 'random'
    template_name = 'devilry_admin/assignment/examiners/bulk_organize/random.django.html'

    def get_target_renderer_class(self):
        return RandomOrganizeTargetRenderer

    def get_form_class(self):
        return RandomOrganizeForm

    def __get_relatedexaminerqueryset(self):
        assignment = self.request.cradmin_role
        period = assignment.period
        queryset = RelatedExaminer.objects\
            .filter(period=period)\
            .select_related('user')\
            .exclude(active=False)
        return queryset

    def get_form_kwargs(self):
        kwargs = super(RandomView, self).get_form_kwargs()
        kwargs['selectable_relatedexaminers_queryset'] = self.__get_relatedexaminerqueryset()
        return kwargs

    def get_success_url(self):
        return self.request.cradmin_instance.reverse_url(
            appname='examineroverview',
            viewname=crapp.INDEXVIEW_NAME)

    def __clear_examiners(self, groupqueryset):
        Examiner.objects.filter(assignmentgroup__in=groupqueryset).delete()

    def __random_organize_examiners(self, groupqueryset, relatedexaminerqueryset):
        relatedexaminers = list(relatedexaminerqueryset)
        groups = list(groupqueryset)
        max_per_examiner = int(math.ceil(len(groups) / len(relatedexaminers)))
        relatedexaminer_to_count_map = {}
        examiners_to_create = []
        for group in groupqueryset:
            relatedexaminer = random.choice(relatedexaminers)
            if relatedexaminer.id not in relatedexaminer_to_count_map:
                relatedexaminer_to_count_map[relatedexaminer.id] = 0
            relatedexaminer_to_count_map[relatedexaminer.id] += 1
            if relatedexaminer_to_count_map[relatedexaminer.id] > max_per_examiner:
                relatedexaminers.remove(relatedexaminer)
            examiner_to_create = Examiner(relatedexaminer=relatedexaminer, assignmentgroup=group)
            examiners_to_create.append(examiner_to_create)
        Examiner.objects.bulk_create(examiners_to_create)

    def form_invalid_add_global_errormessages(self, form):
        super(RandomView, self).form_invalid_add_global_errormessages(form=form)
        if 'selected_relatedexaminers' in form.errors:
            for errormessage in form.errors['selected_relatedexaminers']:
                messages.error(self.request, errormessage)

    def form_valid(self, form):
        groupqueryset = form.cleaned_data['selected_items']
        relatedexaminerqueryset = form.cleaned_data['selected_relatedexaminers']
        self.__clear_examiners(groupqueryset=groupqueryset)
        self.__random_organize_examiners(groupqueryset=groupqueryset,
                                         relatedexaminerqueryset=relatedexaminerqueryset)
        # messages.success(self.request, self.get_success_message(candidatecount=candidatecount))
        return redirect(self.get_success_url())


class ManualAddOrReplaceExaminersForm(groupview_base.SelectedGroupsForm):
    selected_relatedexaminers_required_message = ugettext_lazy(
            'You must select at least one examiner.')
    selected_relatedexaminers = forms.ModelMultipleChoiceField(
        queryset=RelatedExaminer.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        label=ugettext_lazy('Select examiners:'),
        required=True,
        error_messages={
            'required': selected_relatedexaminers_required_message
        }
    )

    def __make_relatedexaminer_choices(self, relatedexaminerqueryset):
        return [
            (relatedexaminer.id, relatedexaminer.user.get_full_name())
            for relatedexaminer in relatedexaminerqueryset]

    def __init__(self, *args, **kwargs):
        selectable_relatedexaminers_queryset = kwargs.pop('selectable_relatedexaminers_queryset')
        super(ManualAddOrReplaceExaminersForm, self).__init__(*args, **kwargs)
        self.fields['selected_relatedexaminers'].queryset = selectable_relatedexaminers_queryset
        self.fields['selected_relatedexaminers'].choices = self.__make_relatedexaminer_choices(
            relatedexaminerqueryset=selectable_relatedexaminers_queryset)


class ManualAddOrReplaceTargetRenderer(devilry_listbuilder.assignmentgroup.GroupTargetRenderer):

    def get_field_layout(self):
        return [
            'selected_relatedexaminers'
        ]


class BaseManualAddOrReplaceView(groupview_base.BaseMultiselectView):
    def get_form_class(self):
        return ManualAddOrReplaceExaminersForm

    def __get_relatedexaminerqueryset(self):
        assignment = self.request.cradmin_role
        period = assignment.period
        queryset = RelatedExaminer.objects\
            .filter(period=period)\
            .select_related('user')\
            .exclude(active=False)
        return queryset

    def get_form_kwargs(self):
        kwargs = super(BaseManualAddOrReplaceView, self).get_form_kwargs()
        kwargs['selectable_relatedexaminers_queryset'] = self.__get_relatedexaminerqueryset()
        return kwargs

    def get_success_url(self):
        return self.request.get_full_path()

    def clear_existing_examiners_from_groups(self, groupqueryset):
        raise NotImplementedError()

    def get_ignored_relatedexaminerids_for_group(self, group):
        raise NotImplementedError()

    def __add_examiners(self, groupqueryset, relatedexaminerqueryset):
        examiners = []
        groupcount = 0
        candidatecount = 0
        relatedexaminers = list(relatedexaminerqueryset)
        for group in groupqueryset:
            groupcount += 1
            candidatecount += len(group.candidates.all())
            ignored_relatedexaminers_for_group = self.get_ignored_relatedexaminerids_for_group(group=group)
            for relatedexaminer in relatedexaminers:
                if relatedexaminer.id not in ignored_relatedexaminers_for_group:
                    examiner = Examiner(assignmentgroup=group,
                                        relatedexaminer=relatedexaminer)
                    examiners.append(examiner)
        Examiner.objects.bulk_create(examiners)
        return groupcount, candidatecount, relatedexaminers

    def form_invalid_add_global_errormessages(self, form):
        super(BaseManualAddOrReplaceView, self).form_invalid_add_global_errormessages(form=form)
        if 'selected_relatedexaminers' in form.errors:
            for errormessage in form.errors['selected_relatedexaminers']:
                messages.error(self.request, errormessage)

    def get_success_message_formatting_string(self):
        raise NotImplementedError()

    def get_success_message(self, candidatecount, relatedexaminers):
        examinernames = [relatedexaminer.user.get_full_name()
                         for relatedexaminer in relatedexaminers]
        return self.get_success_message_formatting_string() % {
            'count': candidatecount,
            'examinernames': ', '.join(examinernames)
        }

    def form_valid(self, form):
        groupqueryset = form.cleaned_data['selected_items']
        relatedexaminerqueryset = form.cleaned_data['selected_relatedexaminers']
        self.clear_existing_examiners_from_groups(groupqueryset=groupqueryset)
        groupcount, candidatecount, relatedexaminers = self.__add_examiners(
                groupqueryset=groupqueryset,
                relatedexaminerqueryset=relatedexaminerqueryset)
        messages.success(self.request, self.get_success_message(candidatecount=candidatecount,
                                                                relatedexaminers=relatedexaminers))
        return redirect(self.get_success_url())


class ManualAddTargetRenderer(ManualAddOrReplaceTargetRenderer):
    def get_submit_button_text(self):
        return ugettext_lazy('Add selected examiners to selected students')


class ManualAddView(BaseManualAddOrReplaceView):
    filterview_name = 'manual-add'
    template_name = 'devilry_admin/assignment/examiners/bulk_organize/manual-add.django.html'

    def get_target_renderer_class(self):
        return ManualAddTargetRenderer

    def clear_existing_examiners_from_groups(self, groupqueryset):
        pass  # We do not clear existing examiners in Add view!

    def get_ignored_relatedexaminerids_for_group(self, group):
        # We ignore any examiners currently registered on the group
        return {examiner.relatedexaminer_id for examiner in group.examiners.all()}

    def get_success_message_formatting_string(self):
        return ugettext_lazy('Added %(count)s students to %(examinernames)s.')


class ManualReplaceTargetRenderer(ManualAddOrReplaceTargetRenderer):
    def get_submit_button_text(self):
        return ugettext_lazy('Replace selected examiners with current examiners for selected students')


class ManualReplaceView(BaseManualAddOrReplaceView):
    filterview_name = 'manual-replace'
    template_name = 'devilry_admin/assignment/examiners/bulk_organize/manual-replace.django.html'

    def get_target_renderer_class(self):
        return ManualReplaceTargetRenderer

    def clear_existing_examiners_from_groups(self, groupqueryset):
        # We clear any existing examiners on for selected groups
        Examiner.objects.filter(assignmentgroup__in=groupqueryset).delete()

    def get_ignored_relatedexaminerids_for_group(self, group):
        # We do not need to ignore any existing examiners - they are removed
        # by :meth:`.clear_existing_examiners_from_groups`
        return []

    def get_success_message_formatting_string(self):
        return ugettext_lazy('Made %(examinernames)s examiner for %(count)s students, replacing any previous '
                             'examiners for those students.')


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  SelectMethodView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^random/(?P<filters_string>.+)?$',
                  RandomView.as_view(),
                  name='random'),
        crapp.Url(r'^manual-add/(?P<filters_string>.+)?$',
                  ManualAddView.as_view(),
                  name='manual-add'),
        crapp.Url(r'^manual-replace/(?P<filters_string>.+)?$',
                  ManualReplaceView.as_view(),
                  name='manual-replace'),
    ]
