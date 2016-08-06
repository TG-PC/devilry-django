from django.db import models

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import FeedbackSet


class AssignmentGroupCachedData(models.Model):
    # NOTE: We may need to reverse this relationship (a cached_data field on AssignmentGroup)
    group = models.OneToOneField(AssignmentGroup, related_name='cached_data')
    first_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                          null=True, blank=True)
    last_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                         null=True, blank=True)
    last_published_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                                   null=True, blank=True)
    # public_total_comment_count = models.PositiveIntegerField()
    # public_student_comment_count = models.PositiveIntegerField()
    # public_examiner_comment_count = models.PositiveIntegerField()
    # public_admin_comment_count = models.PositiveIntegerField()
    # TODO: Add feedbackset count field