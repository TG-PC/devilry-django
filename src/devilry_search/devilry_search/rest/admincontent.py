from haystack.query import SearchQuerySet

from devilry.apps.core.models import Node
from devilry.apps.core.models import Subject
from devilry.apps.core.models import Period
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import AssignmentGroup
from .base import SearchRestViewBase


class SearchAdminContent(SearchRestViewBase):
    """
    Searches all content where the authenticated user is admin.

    # Parameters
    Takes the following parameters (in the QUERYSTRING):

    - ``search``: The search string. The result will be an empty list if this is empty.
    - ``maxresults``: The maximum number of results. Defaults to 10. Must be between 1 and 100.

    # Returns
    """

    def _serialize_basenode(self, obj, serialized):
        serialized['title'] = obj.long_name
        serialized['path'] = obj.get_path()
        return serialized

    def serialize_type_core_node(self, obj, serialized):
        return self._serialize_basenode(obj, serialized)

    def serialize_type_core_subject(self, obj, serialized):
        return self._serialize_basenode(obj, serialized)

    def serialize_type_core_period(self, obj, serialized):
        return self._serialize_basenode(obj, serialized)

    def serialize_type_core_assignment(self, obj, serialized):
        return self._serialize_basenode(obj, serialized)

    def serialize_type_core_assignmentgroup(self, obj, serialized):
        assignment = obj.parentnode
        studentnames = [c.student.get_profile().get_displayname() for c in obj.candidates.all()]
        serialized['title'] = assignment.long_name
        serialized['meta'] = u', '.join(studentnames)
        serialized['path'] = assignment.get_path()
        return serialized

    def get_search_queryset(self):
        return SearchQuerySet().filter(admin_ids=unicode(self.request.user.id)).models(
            Node, Subject, Period, Assignment, AssignmentGroup)