# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import pgettext_lazy
from django.views.generic import TemplateView
from django_cradmin.viewhelpers import listbuilder

from devilry.devilry_deadlinemanagement.views.viewutils import GroupQuerySetMixin
from devilry.utils import datetimeutils


class SelectDeadlineItemValue(listbuilder.itemvalue.TitleDescription):
    template_name = 'devilry_deadlinemanagement/select-deadline-item-value.django.html'
    valuealias = 'deadline'

    def __init__(self, assignment_groups, assignment, devilryrole, **kwargs):
        super(SelectDeadlineItemValue, self).__init__(**kwargs)
        self.assignment_groups = assignment_groups
        self.assignment = assignment
        self.devilryrole = devilryrole
        self.deadline = datetimeutils.datetime_to_string(self.value)


class DeadlineListView(GroupQuerySetMixin, TemplateView):
    template_name = 'devilry_deadlinemanagement/select-deadline.django.html'

    def get_pagetitle(self):
        return pgettext_lazy('{} select_deadline'.format(self.request.cradmin_app.get_devilryrole()),
                             'Select deadline to manage')

    def get_pageheading(self):
        return pgettext_lazy('{} select_deadline'.format(self.request.cradmin_app.get_devilryrole()),
                             'Select deadline')

    def get_page_subheading(self):
        return pgettext_lazy('{} select_deadline'.format(self.request.cradmin_app.get_devilryrole()),
                             'Please choose how you would like to manage groups for a deadline.')

    def annotate_queryset(self, queryset):
        """
        Annotate the queryset with data that can be used to filtered out which
        groups that can be managed.

        Args:
            queryset (QuerySet): Of :class:`.AssignmentGroup`.

        Returns:
            ``queryset``(from parameters) with annotations.
        """
        return queryset\
            .annotate_with_is_waiting_for_feedback_count()\
            .annotate_with_is_waiting_for_deliveries_count()\
            .annotate_with_is_corrected_count()

    def get_queryset_for_role(self, role):
        """
        If additional filtering is needed, override this with a call to super.

        Args:
            role: :class:`.Assignment`.
        """
        queryset = self.get_queryset_for_role_filtered(role=role)
        return self.annotate_queryset(queryset=queryset)\
            .distinct()\
            .filter(annotated_is_corrected__gt=0)\
            .order_by('cached_data__last_published_feedbackset__deadline_datetime')

    def get_distinct_deadlines_with_groups(self):
        """
        Collect data from queryset where the everything is ordered by distinct deadlines.
        Adds data to a OrderDict where the keys are deadlines and values are lists of ``AssignmentGroups``.

        Example::

            The returned value will be something like this:
                {
                    2017-02-16-23:59:59(``django datetime object``): [group4, group5, group6],
                    2017-02-13-23:59:59(``django datetime object``): [group1, group2, group3],
                    2017-02-19-23:59:59(``django datetime object``): [group7, group8]
                }

        Returns:
            (OrderedDict): Ordered dictionary of deadlines(keys) and list of groups(values).
        """
        queryset = self.get_queryset_for_role(role=self.request.cradmin_role)
        deadlines_dict = {}
        for group in queryset:
            deadline = group.cached_data.last_published_feedbackset.deadline_datetime
            if deadline not in deadlines_dict:
                deadlines_dict[deadline] = []
            deadlines_dict[deadline].append(group)
        return deadlines_dict

    def __make_listbuilder_list(self):
        listbuilder_list = listbuilder.lists.RowList()
        for deadline, group_list in self.get_distinct_deadlines_with_groups().iteritems():
            listbuilder_list.append(
                listbuilder.itemframe.DefaultSpacingItemFrame(
                    SelectDeadlineItemValue(
                        assignment_groups=group_list,
                        assignment=self.request.cradmin_role,
                        devilryrole=self.request.cradmin_app.get_devilryrole(),
                        value=deadline)
                )
            )
        return listbuilder_list

    def get_context_data(self, **kwargs):
        context_data = super(DeadlineListView, self).get_context_data(**kwargs)
        context_data['listbuilder_list'] = self.__make_listbuilder_list()
        context_data['pagetitle'] = self.get_pagetitle()
        context_data['pageheading'] = self.get_pageheading()
        context_data['page_subheading'] = self.get_page_subheading()
        context_data['startapp_backlink_url'] = self.get_startapp_backlink_url()
        return context_data

    def get_startapp_backlink_url(self):
        """
        Override this function to provide a URL back to the app accessed this view from.

        Note:
            By default this just redirects to back to itself, so you probably want
            to override it.
        """
        return self.request.cradmin_app.reverse_appindexurl()
