import htmls
import mock
from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from django_cradmin import cradmin_testhelpers

from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group import models as  group_models
from devilry.devilry_group.tests.feedbackfeed import test_feedbackfeed_examiner
from devilry.devilry_group.views import feedbackfeed_examiner
from devilry.apps.core import models as core_models


class TestFeedbackfeedExaminerFeedbackRendering(test_feedbackfeed_examiner.TestFeedbackfeedExaminer):
    # Override viewclass for this specific view.
    viewclass = feedbackfeed_examiner.ExaminerFeedbackView

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_for_examiners_and_admins_button(self):
        examiner = mommy.make('core.Examiner')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_publish_feedback'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_to_feedbackdraft_button(self):
        examiner = mommy.make('core.Examiner')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_add_comment_to_feedback_draft'))

    def test_get_form_passedfailed_grade_option(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=mommy.make('core.AssignmentGroup', parentnode=assignment),
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#div_id_passed'))
        self.assertFalse(mockresponse.selector.exists('#div_id_points'))

    def test_get_form_points_grade_option(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=mommy.make('core.AssignmentGroup', parentnode=assignment),
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertFalse(mockresponse.selector.exists('#div_id_passed'))
        self.assertTrue(mockresponse.selector.exists('#div_id_points'))

    # def test_feedbackfeed_view_publish_feedback(self):
    #     group = mommy.make('core.AssignmentGroup')
    #     examiner = mommy.make('core.Examiner',
    #                           assignmentgroup=group,
    #                           relatedexaminer=mommy.make('core.RelatedExaminer'))
    #     mommy.make('devilry_group.GroupComment',
    #                user=examiner.relatedexaminer.user,
    #                user_role='examiner',
    #                visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
    #                part_of_grading=True,
    #                published_datetime=timezone.now(),
    #                feedback_set__group=group)


    # def test_get_examiner_comment_part_of_grading_private(self):
    #     group = mommy.make('core.AssignmentGroup')
    #     examiner1 = mommy.make('core.Examiner',
    #                            assignmentgroup=group,
    #                            relatedexaminer=mommy.make('core.RelatedExaminer'),)
    #     examiner2 = mommy.make('core.Examiner',
    #                            assignmentgroup=group,
    #                            relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='Jane Doe'),)
    #     mommy.make('devilry_group.GroupComment',
    #                user=examiner2.relatedexaminer.user,
    #                user_role='examiner',
    #                part_of_grading=True,
    #                visibility=GroupComment.VISIBILITY_PRIVATE,
    #                published_datetime=timezone.now() - timezone.timedelta(days=1),
    #                feedback_set__group=group)
    #     mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner1.assignmentgroup,
    #                                                       requestuser=examiner1.relatedexaminer)
    #     self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))

    def test_post_feedbackdraft_comment_with_text(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', )
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment',
                    'examiner_add_comment_to_feedback_draft': 'unused value'
                }
            })
        self.assertEquals(1, len(group_models.GroupComment.objects.all()))

    def test_post_feedbackset_comment_visibility_private(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', )
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment',
                    'examiner_add_comment_to_feedback_draft': 'unused value'
                }
            })
        self.assertEquals('private', group_models.GroupComment.objects.all()[0].visibility)


class TestFeedbackFeedExaminerPublishFeedback(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = feedbackfeed_examiner.ExaminerFeedbackView

    def test_post_can_not_publish_with_first_deadline_as_none(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED,
                                       first_deadline=None)
        feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        self.assertEquals(1, group_models.FeedbackSet.objects.all().count())
        self.assertIsNone(group_models.FeedbackSet.objects.all()[0].grading_published_datetime)

    def test_post_can_not_publish_with_last_feedbackset_deadline_as_none(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment
                                       .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset_first = group_mommy.feedbackset_first_attempt_published(group=group, is_last_in_group=None)
        feedbackset_last = group_mommy.feedbackset_new_attempt_unpublished(group=group, deadline_datetime=None)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all().order_by('created_datetime')
        self.assertEquals(2, len(feedbacksets))
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
        self.assertIsNone(feedbacksets[1].grading_published_datetime)

    def test_post_publish_feedbackset_before_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_middle')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        self.assertIsNone(group_models.FeedbackSet.objects.all()[0].grading_published_datetime)

    def test_post_publish_feedbackset_after_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)

    def test_post_publish_feedbackset_after_deadline_grading_system_points(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'points': 10,
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
        self.assertEquals(10, feedbacksets[0].grading_points)

    def test_post_publish_feedbackset_after_deadline_grading_system_passed_failed(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'passed': True,
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
        self.assertEquals(1, feedbacksets[0].grading_points)

    def test_post_publish_feedbackset_drafts_on_last_feedbackset_only(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset_first = group_mommy.feedbackset_first_attempt_published(is_last_in_group=None, group=group)
        feedbackset_last = group_mommy.feedbackset_new_attempt_unpublished(group=group, deadline_datetime=timezone.now())
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        student = mommy.make('core.Candidate',
                             assignment_group=group,
                             relatedstudent=mommy.make('core.RelatedStudent'))
        mommy.make('devilry_group.GroupComment',
                       text='test text 1',
                       user=examiner.relatedexaminer.user,
                       user_role='examiner',
                       part_of_grading=True,
                       feedback_set=feedbackset_first)
        comment2 = mommy.make('devilry_group.GroupComment',
                       text='test text 2',
                       user=examiner.relatedexaminer.user,
                       user_role='examiner',
                       part_of_grading=True,
                       feedback_set=feedbackset_last)
        self.mock_http302_postrequest(
            cradmin_role=student.assignment_group,
            requestuser=student.relatedstudent.user,
            viewkwargs={'pk': group.id},
            requestkwargs={
                'data': {
                    'passed': True,
                    'text': 'post comment',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        feedback_comments = group_models.GroupComment.objects.all().filter(feedback_set=feedbacksets[1])

        self.assertEquals(2, len(feedback_comments))
        self.assertEquals(feedback_comments[0], comment2)
        self.assertEquals(feedback_comments[1].text, 'post comment')

    def test_post_publish_feedbackset_after_deadline_test_publish_drafts_part_of_grading(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mommy.make('devilry_group.GroupComment',
                   text='test text 1',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   feedback_set=feedbackset)
        mommy.make('devilry_group.GroupComment',
                   text='test text 2',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   feedback_set=feedbackset)
        mommy.make('devilry_group.GroupComment',
                   text='test text 3',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   feedback_set=feedbackset)
        mommy.make('devilry_group.GroupComment',
                   text='test text 4',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   feedback_set=feedbackset)
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'passed': True,
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        feedback_comments = group_models.GroupComment.objects.all()
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
        self.assertEquals(1, feedbacksets[0].grading_points)
        self.assertEquals(5, len(feedback_comments))

    def test_examiner_publishes_without_comment_text(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'passed': True,
                    'text': '',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
        self.assertEquals(0, group_models.GroupComment.objects.all().count())

    def test_examiner_publishes_with_comment_text(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'passed': True,
                    'text': 'test',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
        self.assertEquals(1, group_models.GroupComment.objects.all().count())

    # def test_post_comment_file(self):
    #     feedbackset = mommy.make('devilry_group.FeedbackSet')
    #     filecollection = mommy.make(
    #         'cradmin_temporaryfileuploadstore.TemporaryFileCollection',
    #     )
    #     test_file = mommy.make(
    #         'cradmin_temporaryfileuploadstore.TemporaryFile',
    #         filename='test.txt',
    #         collection=filecollection
    #     )
    #     test_file.file.save('test.txt', ContentFile('test'))
    #     self.mock_http302_postrequest(
    #         cradmin_role=feedbackset.group,
    #         viewkwargs={'pk': feedbackset.group.id},
    #         requestkwargs={
    #             'data': {
    #                 'text': 'This is a comment',
    #                 'temporary_file_collection_id': filecollection.id,
    #             }
    #         })
    #     comment_files = comment_models.CommentFile.objects.all()
    #     self.assertEquals(1, len(comment_files))