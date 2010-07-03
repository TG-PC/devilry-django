from django.db import models


class CharFieldGrade(models.Model):
    grade = models.CharField(max_length=15)

    def __unicode__(self):
        return self.grade

    def set_grade_from_string(self, grade):
        self.grade = grade
