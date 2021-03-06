# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ievv_opensource.ievv_batchframework import batchregistry

from devilry.apps.core import models as core_models
from devilry.devilry_group.models import GroupComment
from devilry.devilry_comment.models import CommentFile
from devilry.devilry_group.views.download_files.batch_download_api import AbstractBatchCompressionAPIView


class BatchCompressionAPIAssignmentView(AbstractBatchCompressionAPIView):
    """
    API for checking if a compressed ``Assignment`` is ready for download.
    """
    model_class = core_models.Assignment
    batchoperation_type = 'batchframework_compress_assignment'

    def _get_comment_file_queryset(self):
        assignment_group_ids = core_models.AssignmentGroup.objects \
            .filter(parentnode=self.content_object) \
            .filter_examiner_has_access(user=self.request.user) \
            .values_list('id', flat=True)
        group_comment_ids = GroupComment.objects \
            .filter(feedback_set__group_id__in=assignment_group_ids) \
            .values_list('id', flat=True)
        return CommentFile.objects \
            .filter(comment_id__in=group_comment_ids)

    def has_no_files(self):
        return self._get_comment_file_queryset().count() == 0

    def new_file_is_added(self, latest_compressed_datetime):
        return self._get_comment_file_queryset()\
            .filter(created_datetime__gt=latest_compressed_datetime)\
            .exists()

    def get_ready_for_download_status(self, content_object_id=None):
        status_dict = super(BatchCompressionAPIAssignmentView, self).get_ready_for_download_status()
        status_dict['download_link'] = self.request.cradmin_app.reverse_appurl(
            viewname='assignment-file-download',
            kwargs={
                'assignment_id': content_object_id
            })
        return status_dict

    def start_compression_task(self, content_object_id):
        batchregistry.Registry.get_instance().run(
            actiongroup_name=self.batchoperation_type,
            context_object=self.content_object,
            operationtype=self.batchoperation_type,
            started_by=self.request.user
        )
