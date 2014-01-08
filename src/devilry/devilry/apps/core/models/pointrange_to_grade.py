from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError

from .assignment import Assignment



class PointToGradeMap(models.Model):
    """
    Data structure to store the mapping from a point ranges to grades
    when using custom-table.

    The basic idea is described in https://github.com/devilry/devilry-django/issues/511,
    but we decided to add this OneToOne table to represent a mapping table
    to avoid adding complexity to Assignment that is only needed when the
    custom-table ``points_to_grade_mapper`` is used.

    .. attribute:: assignment

        Foreign Key to the assignment.
    """
    assignment = models.OneToOneField(Assignment)

    class Meta:
        app_label = 'core'


    # def update_mapping(self, *point_to_grade_list):
    #     """
    #     """
    #     for minimum_points, 

    def points_to_grade(self, points):
        """
        Convert the given ``points`` to a grade using this PointToGradeMap.

        :raises PointRangeToGrade.DoesNotExist:
            If no grade matching the given points exist.
        """
        return self.pointrangetograde_set.filter_grades_matching_points(points).get()

    def __unicode__(self):
        return u'Point to grade map for {}'.format(self.assignment.get_path())




class PointRangeToGradeMapQueryset(models.query.QuerySet):
    def filter_overlapping_ranges(self, start, end):
        return self.filter(
            Q(minimum_points__lte=start, maximum_points__gte=start) |
            Q(minimum_points__lte=end, maximum_points__gte=end) |
            Q(minimum_points__gte=start, maximum_points__lte=end))

    def filter_grades_matching_points(self, points):
        return self.filter(
            minimum_points__lte=points,
            maximum_points__gte=points
        )


class PointRangeToGradeMapManager(models.Manager):
    """
    Reflect custom QuerySet methods for custom QuerySet
    more info: https://github.com/devilry/devilry-django/issues/491
    """

    def get_queryset(self):
        return PointRangeToGradeMapQueryset(self.model, using=self._db)

    def filter_overlapping_ranges(self, start, end):
        """
        Matches all PointRangeToGrade objects where start or end is
        between the start and the end.

        This is perfect for checking if a range can be added to an assignment
        (needs ``.filter(point_to_grade_map=assignment.pointtogrademap)`` in addition to this filter).
        """
        return self.get_queryset().filter_overlapping_ranges(start, end)

    def filter_grades_matching_points(self, points):
        """
        Filter all PointRangeToGrade objects where ``points`` is between
        ``minimum_points`` and ``maximum_points`` including both ends.
        """
        return self.get_queryset().filter_grades_matching_points(points)



class PointRangeToGrade(models.Model):
    """
    Data structure to store the mapping from a single point-range to grade
    when using custom-table.

    First described in https://github.com/devilry/devilry-django/issues/511.

    .. attribute:: point_to_grade_map

        Foreign Key to the PointToGradeMap.

    .. attribute:: minimum_points

        Minimum value for points that matches this table entry.

    .. attribute:: maximum_points
        Minimum value for points that matches this table entry.

    .. attribute:: grade

        The grade that this entry represents a match for.
    """
    objects = PointRangeToGradeMapManager()
    point_to_grade_map = models.ForeignKey(PointToGradeMap)
    minimum_points = models.IntegerField()
    maximum_points = models.IntegerField()
    grade = models.CharField(max_length=12)
    
    class Meta:
        unique_together = ('point_to_grade_map', 'grade')
        app_label = 'core'
        ordering = ['minimum_points']

    def clean(self):
        if self.minimum_points >= self.maximum_points:
            raise ValidationError('Minimum points can not be equal to or greater than maximum points.')
        overlapping_ranges = self.__class__.objects\
            .filter_overlapping_ranges(self.minimum_points, self.maximum_points) \
            .filter(point_to_grade_map=self.point_to_grade_map)
        if self.id != None:
            overlapping_ranges = overlapping_ranges.exclude(id=self.id)
        if overlapping_ranges.exists():
            raise ValidationError('One or more PointRangeToGrade overlaps with this range.')

    def __unicode__(self):
        return u'{1}-{2}={3}'.format(self.minimum_points, self.maximum_points, self.grade)
