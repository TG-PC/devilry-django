from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import transaction

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.apps.core.models import PointRangeToGrade
from devilry.apps.core.models import PointToGradeMap
from devilry.apps.core.models.pointrange_to_grade import NonzeroSmallesMinimalPointsValidationError
from devilry.apps.core.models.pointrange_to_grade import InvalidLargestMaximumPointsValidationError
from devilry.apps.core.models.pointrange_to_grade import GapsInMapValidationError


class TestPointRangeToGradeManager(TestCase):
    def setUp(self):
        self.assignment = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment').assignment
        self.point_to_grade_map = PointToGradeMap.objects.create(assignment=self.assignment)

    def test_filter_overlapping_ranges(self):
        self.point_to_grade_map.pointrangetograde_set.create(
            minimum_points=10,
            maximum_points=20,
            grade='D'
        )
        self.assertFalse(PointRangeToGrade.objects.filter_overlapping_ranges(0, 9).exists())
        self.assertTrue(PointRangeToGrade.objects.filter_overlapping_ranges(10, 20).exists())
        self.assertTrue(PointRangeToGrade.objects.filter_overlapping_ranges(13, 18).exists())
        self.assertTrue(PointRangeToGrade.objects.filter_overlapping_ranges(18, 25).exists())
        self.assertTrue(PointRangeToGrade.objects.filter_overlapping_ranges(20, 21).exists())
        self.assertTrue(PointRangeToGrade.objects.filter_overlapping_ranges(8, 22).exists())
        self.assertFalse(PointRangeToGrade.objects.filter_overlapping_ranges(21, 22).exists())

    def test_filter_grades_matching_points(self):
        self.point_to_grade_map.pointrangetograde_set.create(
            minimum_points=0,
            maximum_points=9,
            grade='F'
        )
        self.point_to_grade_map.pointrangetograde_set.create(
            minimum_points=10,
            maximum_points=20,
            grade='E'
        )
        self.point_to_grade_map.pointrangetograde_set.create(
            minimum_points=21,
            maximum_points=30,
            grade='D'
        )
        self.assertEquals(PointRangeToGrade.objects.filter_grades_matching_points(9).get().grade, 'F')
        self.assertEquals(PointRangeToGrade.objects.filter_grades_matching_points(10).get().grade, 'E')
        self.assertEquals(PointRangeToGrade.objects.filter_grades_matching_points(20).get().grade, 'E')
        self.assertEquals(PointRangeToGrade.objects.filter_grades_matching_points(21).get().grade, 'D')


class TestPointRangeToGrade(TestCase):
    def setUp(self):
        self.periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        self.assignment = self.periodbuilder.add_assignment('assignment').assignment

    def test_clean_max_smaller_than_min_fails(self):
        pointrange_to_grade = PointRangeToGrade(
            point_to_grade_map=PointToGradeMap.objects.create(assignment=self.assignment),
            minimum_points=2,
            maximum_points=1,
            grade='D'
        )
        with self.assertRaises(ValidationError):
            pointrange_to_grade.clean()

    def test_clean_max_equal_to_min_works(self):
        pointrange_to_grade = PointRangeToGrade(
            point_to_grade_map=PointToGradeMap.objects.create(assignment=self.assignment),
            minimum_points=1,
            maximum_points=1,
            grade='D'
        )
        with self.assertRaises(ValidationError):
            pointrange_to_grade.clean()

    def test_clean_max_greater_than_min_works(self):
        pointrange_to_grade = PointRangeToGrade(
            point_to_grade_map=PointToGradeMap.objects.create(assignment=self.assignment),
            minimum_points=0,
            maximum_points=1,
            grade='D'
        )
        pointrange_to_grade.clean()  # Should work without error

    def test_clean_overlapping_other_on_same_assignment_fails(self):
        point_to_grade_map = PointToGradeMap.objects.create(assignment=self.assignment)
        point_to_grade_map.pointrangetograde_set.create(
            minimum_points=10,
            maximum_points=20,
            grade='D'
        )
        pointrange_to_grade = PointRangeToGrade(
            point_to_grade_map=point_to_grade_map,
            minimum_points=12,
            maximum_points=18,
            grade='C'
        )
        with self.assertRaises(ValidationError):
            pointrange_to_grade.clean()

    def test_clean_existing_does_not_match_overlapping_range(self):
        pointrange_to_grade = PointRangeToGrade(
            point_to_grade_map=PointToGradeMap.objects.create(assignment=self.assignment),
            minimum_points=12,
            maximum_points=18,
            grade='C'
        )
        pointrange_to_grade.save()
        pointrange_to_grade.clean()

    def test_clean_does_not_match_overlapping_range_in_other_assignments(self):
        assignment2 = self.periodbuilder.add_assignment('assignment2').assignment
        pointrange_to_grade = PointRangeToGrade(
            point_to_grade_map=PointToGradeMap.objects.create(assignment=self.assignment),
            minimum_points=12,
            maximum_points=18,
            grade='D'
        )
        PointRangeToGrade(
            point_to_grade_map=PointToGradeMap.objects.create(assignment=assignment2),
            minimum_points=10,
            maximum_points=20,
            grade='C'
        ).save()
        pointrange_to_grade.clean()

    def test_clean_not_unique_grade(self):
        point_to_grade_map = PointToGradeMap.objects.create(assignment=self.assignment)
        PointRangeToGrade(
            point_to_grade_map=point_to_grade_map,
            minimum_points=1,
            maximum_points=2,
            grade='C'
        ).save()
        pointrange_to_grade = PointRangeToGrade(
            point_to_grade_map=point_to_grade_map,
            minimum_points=5,
            maximum_points=6,
            grade='C'
        )

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                pointrange_to_grade.save()

        # Does not fail when in another assignment
        assignment2 = self.periodbuilder.add_assignment('assignment2').assignment
        PointRangeToGrade(
            point_to_grade_map=PointToGradeMap.objects.create(assignment=assignment2),
            minimum_points=5,
            maximum_points=6,
            grade='C'
        ).save()

    def test_ordering(self):
        point_to_grade_map = PointToGradeMap.objects.create(assignment=self.assignment)
        f = point_to_grade_map.pointrangetograde_set.create(
            minimum_points=0,
            maximum_points=20,
            grade='F'
        )
        e = point_to_grade_map.pointrangetograde_set.create(
            minimum_points=21,
            maximum_points=40,
            grade='E'
        )
        d = point_to_grade_map.pointrangetograde_set.create(
            minimum_points=41,
            maximum_points=50,
            grade='D'
        )
        self.assertEquals(list(PointRangeToGrade.objects.all()), [f, e, d])


class TestPointToGradeMap(TestCase):
    def setUp(self):
        self.periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        self.assignment = self.periodbuilder.add_assignment(
            'assignment',
            max_points=100).assignment

    def test_points_to_grade_matches(self):
        point_to_grade_map = PointToGradeMap.objects.create(assignment=self.assignment)
        f = point_to_grade_map.pointrangetograde_set.create(
            minimum_points=0,
            maximum_points=20,
            grade='F'
        )
        e = point_to_grade_map.pointrangetograde_set.create(
            minimum_points=21,
            maximum_points=40,
            grade='E'
        )
        self.assertEquals(point_to_grade_map.points_to_grade(0), f)
        self.assertEquals(point_to_grade_map.points_to_grade(12), f)
        self.assertEquals(point_to_grade_map.points_to_grade(20), f)
        self.assertEquals(point_to_grade_map.points_to_grade(21), e)
        with self.assertRaises(PointRangeToGrade.DoesNotExist):
            point_to_grade_map.points_to_grade(41)

    def test_points_to_grade_multi_assignment(self):
        assignment2 = self.periodbuilder\
            .add_assignment('assignment2').assignment

        point_to_grade_map1 = PointToGradeMap.objects.create(assignment=self.assignment)
        point_to_grade_map1.pointrangetograde_set.create(
            minimum_points=0,
            maximum_points=9,
            grade='F'
        )
        point_to_grade_map2 = PointToGradeMap.objects.create(assignment=assignment2)
        pointrange_to_grade2 = point_to_grade_map2.pointrangetograde_set.create(
            minimum_points=0,
            maximum_points=3,
            grade='F'
        )
        self.assertEquals(pointrange_to_grade2, assignment2.pointtogrademap.points_to_grade(2))

        # When we update to Django 1.5+, this should start only
        # matching pointrange_to_grade2. See:
        # https://github.com/devilry/devilry-django/issues/563
        matches = assignment2.pointtogrademap.pointrangetograde_set.filter_grades_matching_points(2)
        self.assertEquals({pointrange_to_grade2}, set(matches))
        # self.assertEquals(set([pointrange_to_grade1, pointrange_to_grade2]), set(matches))

    def test_clean_no_entries(self):
        point_to_grade_map = PointToGradeMap.objects.create(assignment=self.assignment)
        self.assertTrue(point_to_grade_map.invalid)
        point_to_grade_map.invalid = True
        self.assertEquals(point_to_grade_map.pointrangetograde_set.count(), 0)
        point_to_grade_map.clean()
        self.assertTrue(point_to_grade_map.invalid)

    def test_clean_single_entry_valid(self):
        point_to_grade_map = PointToGradeMap.objects.create(assignment=self.assignment)
        point_to_grade_map.pointrangetograde_set.create(
            minimum_points=0,
            maximum_points=100,
            grade='Good'
        )
        self.assertTrue(point_to_grade_map.invalid)
        point_to_grade_map.clean()
        self.assertFalse(point_to_grade_map.invalid)

    def test_clean_multientry_valid(self):
        point_to_grade_map = PointToGradeMap.objects.create(assignment=self.assignment)
        point_to_grade_map.pointrangetograde_set.create(
            minimum_points=0,
            maximum_points=30,
            grade='Bad'
        )
        point_to_grade_map.pointrangetograde_set.create(
            minimum_points=31,
            maximum_points=70,
            grade='Better'
        )
        point_to_grade_map.pointrangetograde_set.create(
            minimum_points=71,
            maximum_points=100,
            grade='Good'
        )
        self.assertTrue(point_to_grade_map.invalid)
        point_to_grade_map.clean()
        self.assertFalse(point_to_grade_map.invalid)

    def test_clean_invalid_first_minimum_points(self):
        point_to_grade_map = PointToGradeMap.objects.create(assignment=self.assignment)
        point_to_grade_map.pointrangetograde_set.create(
            minimum_points=1,
            maximum_points=30,
            grade='Bad'
        )
        point_to_grade_map.pointrangetograde_set.create(
            minimum_points=31,
            maximum_points=100,
            grade='Better'
        )
        self.assertTrue(point_to_grade_map.invalid)
        with self.assertRaises(NonzeroSmallesMinimalPointsValidationError):
            point_to_grade_map.clean()

    def test_clean_invalid_first_maximum_points(self):
        point_to_grade_map = PointToGradeMap.objects.create(assignment=self.assignment)
        point_to_grade_map.pointrangetograde_set.create(
            minimum_points=0,
            maximum_points=30,
            grade='Bad'
        )
        point_to_grade_map.pointrangetograde_set.create(
            minimum_points=31,
            maximum_points=70,
            grade='Better'
        )
        self.assertTrue(point_to_grade_map.invalid)
        with self.assertRaises(InvalidLargestMaximumPointsValidationError):
            point_to_grade_map.clean()

    def test_clean_invalid_gaps_in_map(self):
        point_to_grade_map = PointToGradeMap.objects.create(assignment=self.assignment)
        point_to_grade_map.pointrangetograde_set.create(
            minimum_points=0,
            maximum_points=30,
            grade='Bad'
        )
        point_to_grade_map.pointrangetograde_set.create(
            minimum_points=32,
            maximum_points=100,
            grade='Better'
        )
        self.assertTrue(point_to_grade_map.invalid)
        with self.assertRaises(GapsInMapValidationError):
            point_to_grade_map.clean()

    def test_as_choices(self):
        point_to_grade_map = PointToGradeMap.objects.create(assignment=self.assignment)
        point_to_grade_map.pointrangetograde_set.create(
            minimum_points=0,
            maximum_points=30,
            grade='Bad'
        )
        point_to_grade_map.pointrangetograde_set.create(
            minimum_points=32,
            maximum_points=100,
            grade='Better'
        )
        self.assertEquals(point_to_grade_map.as_choices(), [
            (0, 'Bad'),
            (32, 'Better')
        ])

    def test_create_map(self):
        point_to_grade_map = PointToGradeMap.objects.create(assignment=self.assignment)
        point_to_grade_map.create_map(
            (0, 'Bad'),
            (30, 'Better'),
            (60, 'Good'))
        self.assertEquals(point_to_grade_map.pointrangetograde_set.count(), 3)
        bad, better, good = point_to_grade_map.pointrangetograde_set.all()
        self.assertEquals(bad.minimum_points, 0)
        self.assertEquals(bad.maximum_points, 29)
        self.assertEquals(bad.grade, 'Bad')
        self.assertEquals(better.minimum_points, 30)
        self.assertEquals(better.maximum_points, 59)
        self.assertEquals(better.grade, 'Better')
        self.assertEquals(good.minimum_points, 60)
        self.assertEquals(good.maximum_points, 100)
        self.assertEquals(good.grade, 'Good')

    def test_clear_map(self):
        point_to_grade_map = PointToGradeMap.objects.create(assignment=self.assignment)
        point_to_grade_map.pointrangetograde_set.create(
            minimum_points=0,
            maximum_points=30,
            grade='Bad'
        )
        point_to_grade_map.pointrangetograde_set.create(
            minimum_points=32,
            maximum_points=100,
            grade='Better'
        )
        self.assertEquals(point_to_grade_map.pointrangetograde_set.count(), 2)
        point_to_grade_map.clear_map()
        self.assertEquals(point_to_grade_map.pointrangetograde_set.count(), 0)

    def test_recreate_map(self):
        point_to_grade_map = PointToGradeMap.objects.create(assignment=self.assignment)
        point_to_grade_map.create_map(
            (0, 'Bad'),
            (30, 'Better'),
            (60, 'Good'))
        self.assertEquals(point_to_grade_map.pointrangetograde_set.count(), 3)
        bad, better, good = point_to_grade_map.pointrangetograde_set.all()
        self.assertEquals(bad.grade, 'Bad')
        self.assertEquals(better.grade, 'Better')
        self.assertEquals(good.grade, 'Good')
