# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Devilry imports
from devilry.devilry_qualifiesforexam.plugintyperegistry import PluginType
from .views import select_assignment


class SelectAssignmentsPlugin(PluginType):
    plugintypeid = 'devilry_qualifiesforexam_plugin_approved.plugin_select_assignments'
    human_readable_name = 'Select assignments that must be approved'
    description = 'Choose this option if you require your students to get a passing grade on the assignments ' \
                  'you select. All assignments are selected by default.'

    def get_plugin_view_class(self):
        return select_assignment.PluginSelectAssignmentsView
