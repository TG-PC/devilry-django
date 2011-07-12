from ...simplified import (SimplifiedModelApi, simplified_modelapi,
                           PermissionDenied, FieldSpec,
                           FilterSpecs, FilterSpec, ForeignFilterSpec, PatternFilterSpec)
from ..core import models

__all__ = ('SimplifiedNode', 'SimplifiedSubject', 'SimplifiedPeriod', 'SimplifiedAssignment')



class CanSaveBase(SimplifiedModelApi):
    @classmethod
    def write_authorize(cls, user, obj):
        if not obj.can_save(user):
            raise PermissionDenied()

    @classmethod
    def read_authorize(cls, user, obj):
        if not obj.can_save(user):
            raise PermissionDenied()

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        return cls._meta.model.where_is_admin_or_superadmin(user)


@simplified_modelapi
class SimplifiedNode(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Node`. """
    class Meta:
        model = models.Node
        resultfields = FieldSpec('id', 'short_name', 'long_name', 'parentnode')
        searchfields = FieldSpec('short_name', 'long_name')
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']
        filters = FilterSpecs(FilterSpec('parentnode'),
                              FilterSpec('short_name'),
                              FilterSpec('long_name'),
                              PatternFilterSpec('parentnode__*short_name'),
                              PatternFilterSpec('parentnode__*long_name'),
                              PatternFilterSpec('parentnode__*id'))

    @classmethod
    def create_searchqryset(cls, user):
        qryset = models.Node.where_is_admin_or_superadmin(user)
        return qryset


@simplified_modelapi
class SimplifiedSubject(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Subject`. """
    class Meta:
        model = models.Subject
        resultfields = FieldSpec('id', 'short_name', 'long_name', 'parentnode')
        searchfields = FieldSpec('short_name', 'long_name')
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']
        filters = FilterSpecs(FilterSpec('parentnode'),
                              FilterSpec('short_name'),
                              FilterSpec('long_name'),
                              ForeignFilterSpec('parentnode', # Node
                                                FilterSpec('paretnode'),
                                                FilterSpec('short_name'),
                                                FilterSpec('long_name')))


@simplified_modelapi
class SimplifiedPeriod(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Period`. """
    class Meta:
        model = models.Period
        resultfields = FieldSpec('id', 'short_name', 'long_name', 'parentnode',
                                 'start_time', 'end_time',
                                 subject = ['parentnode__short_name', 'parentnode__long_name'])
        searchfields = FieldSpec('short_name', 'long_name', 'parentnode__short_name',
                                 'parentnode__long_name')
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']
        filters = FilterSpecs(FilterSpec('parentnode'),
                              FilterSpec('short_name'),
                              FilterSpec('long_name'),
                              ForeignFilterSpec('parentnode', # Subject
                                                FilterSpec('paretnode'),
                                                FilterSpec('short_name'),
                                                FilterSpec('long_name')))


@simplified_modelapi
class SimplifiedAssignment(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Assignment`. """
    class Meta:
        model = models.Assignment
        resultfields = FieldSpec('id', 'short_name', 'long_name', 'parentnode', 'publishing_time',
                                 period = ['parentnode__short_name',
                                           'parentnode__long_name',
                                           'parentnode__parentnode'],
                                 subject = ['parentnode__parentnode__short_name',
                                            'parentnode__parentnode__long_name'],
                                 pointfields = ['anonymous', 'must_pass', 'maxpoints',
                                                'attempts'])
        searchfields = FieldSpec('short_name', 'long_name',
                                 'parentnode__short_name',
                                 'parentnode__long_name',
                                 'parentnode__parentnode__short_name',
                                 'parentnode__parentnode__long_name')
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']
        filters = FilterSpecs(FilterSpec('parentnode'),
                              FilterSpec('short_name'),
                              FilterSpec('long_name'),
                              ForeignFilterSpec('parentnode', # Period
                                                FilterSpec('paretnode'),
                                                FilterSpec('short_name'),
                                                FilterSpec('long_name')),
                              ForeignFilterSpec('parentnode__parentnode', # Subject
                                                FilterSpec('paretnode'),
                                                FilterSpec('short_name'),
                                                FilterSpec('long_name')))


@simplified_modelapi
class SimplifiedAssignmentGroup(CanSaveBase):
    class Meta:
        model = models.AssignmentGroup
        resultfields = FieldSpec('id', 'name', 'is_open', 'status', 'parentnode',
                                 users=['examiners__username', 'candidates__identifier'],
                                 assignment=['parentnode__long_name',
                                             'parentnode__short_name'],
                                 period=['parentnode__parentnode',
                                         'parentnode__parentnode__long_name',
                                         'parentnode__parentnode__short_name'],
                                 subject=['parentnode__parentnode__parentnode',
                                          'parentnode__parentnode__parentnode__long_name',
                                          'parentnode__parentnode__parentnode__short_name']
                                 )
        searchfields = FieldSpec('name',
                                 'examiners__username',
                                 'candidates__identifier',
                                 # assignment
                                 'parentnode__long_name',
                                 'parentnode__short_name',
                                 # period
                                 'parentnode__parentnode__long_name',
                                 'parentnode__parentnode__short_name',
                                 # subject
                                 'parentnode__parentnode__parentnode__long_name',
                                 'parentnode__parentnode__parentnode__short_name',
                                 )
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']
        filters = FilterSpecs(FilterSpec('id'),
                              FilterSpec('parentnode'),
                              FilterSpec('short_name'),
                              FilterSpec('long_name'),
                              ForeignFilterSpec('parentnode', # Assignment
                                                FilterSpec('paretnode'),
                                                FilterSpec('short_name'),
                                                FilterSpec('long_name')),
                              ForeignFilterSpec('parentnode__parentnode', # Period
                                                FilterSpec('paretnode'),
                                                FilterSpec('short_name'),
                                                FilterSpec('long_name')),
                              ForeignFilterSpec('parentnode__parentnode__parentnode', # Subject
                                                FilterSpec('parentnode'),
                                                FilterSpec('short_name'),
                                                FilterSpec('long_name')))


@simplified_modelapi
class SimplifiedDelivery(CanSaveBase):
    class Meta:
        model = models.Delivery
        resultfields = FieldSpec('id', 'number', 'time_of_delivery', 'assignment_group',
                                 assignment_group=['assignment_group', 'assignment_group__name'],
                                 assignment=['assignment_group__parentnode',
                                             'assignment_group__parentnode__long_name',
                                             'assignment_group__parentnode__short_name'],
                                 period=['assignment_group__parentnode__parentnode',
                                         'assignment_group__parentnode__parentnode__long_name',
                                         'assignment_group__parentnode__parentnode__short_name'],
                                 subject=['assignment_group__parentnode__parentnode__parentnode',
                                          'assignment_group__parentnode__parentnode__parentnode__long_name',
                                          'assignment_group__parentnode__parentnode__parentnode__short_name'])
        searchfields = FieldSpec('number',
                                 # assignmentgroup
                                 'assignment_group__name',
                                 'assignment_group__examiners__username',
                                 'assignment_group__candidates__identifier',
                                 'assignment_group__examiners__username',
                                 'assignment_group__candidates__identifier',
                                 # assignment
                                 'assignment_group__parentnode__long_name',
                                 'assignment_group__parentnode__short_name',
                                 # period
                                 'assignment_group__parentnode__parentnode__long_name',
                                 'assignment_group__parentnode__parentnode__short_name',
                                 # subject
                                 'assignment_group__parentnode__parentnode__parentnode__long_name',
                                 'assignment_group__parentnode__parentnode__parentnode__short_name')
        methods = ['search', 'read']


@simplified_modelapi
class SimplifiedStaticFeedback(SimplifiedModelApi):
    class Meta:
        _subject_long     = 'delivery__assignment_group__parentnode__parentnode__parentnode__long_name'
        _subject_short    = 'delivery__assignment_group__parentnode__parentnode__parentnode__short_name'
        _subject_id       = 'delivery__assignment_group__parentnode__parentnode__parentnode__id'

        _period_long      = 'delivery__assignment_group__parentnode__parentnode__long_name'
        _period_short     = 'delivery__assignment_group__parentnode__parentnode__short_name'
        _period_id        = 'delivery__assignment_group__parentnode__parentnode__id'

        _assignment_long  = 'delivery__assignment_group__parentnode__long_name'
        _assignment_short = 'delivery__assignment_group__parentnode__short_name'
        _assignment_id    = 'delivery__assignment_group__parentnode__id'

        _delivery_time    = 'delivery__time_of_delivery'
        _delivery_number  = 'delivery__number'
        _delivery_delivered_by = 'delivery__delivered_by'
        _delivery_after_deadline = 'delivery__after_deadline'

        model = models.StaticFeedback
        resultfields = FieldSpec('id', 'grade', 'points', 'is_passing_grade',
                                 period=[_period_short, _period_long, _period_id],
                                 subject=[_subject_long, _subject_short, _subject_id],
                                 assignment=[_assignment_short, _assignment_long, _assignment_id],
                                 delivery=[_delivery_time, _delivery_number, ])
        searchfields = FieldSpec(_subject_short,
                                 _subject_long,
                                 _period_short,
                                 _period_long,
                                 _assignment_long,
                                 _assignment_short,
                                 _delivery_number,
                                 )
        methods = ['search', 'read']

    @classmethod
    def create_searchqryset(cls, user):
        return cls._meta.model.where_is_admin_or_superadmin(user)

    @classmethod
    def read_authorize(cls, user, obj):
        #TODO: Replace when issue #141 is resolved!
        if not user.is_superuser:
            if not obj.delivery.assignment_group.is_admin(user):
                raise PermissionDenied()


@simplified_modelapi
class SimplifiedDeadline(SimplifiedModelApi):
    class Meta:

        subject = ['assignment_group__parentnode__parentnode__parentnode',
                   'assignment_group__parentnode__parentnode__parentnode__long_name',
                   'assignment_group__parentnode__parentnode__parentnode__short_name']
        period = ['assignment_group__parentnode__parentnode',
                  'assignment_group__parentnode__parentnode__long_name',
                  'assignment_group__parentnode__parentnode__short_name']
        assignment = ['assignment_group__parentnode',
                      'assignment_group__parentnode__long_name',
                      'assignment_group__parentnode__short_name']
        assignmentgroup = ['assignment_group',
                           'assignment_group__candidates__identifier',
                           'assignment_group__examiners__username',
                           'assignment_group__status']

        model = models.Deadline
        resultfields = FieldSpec('id', 'status', 'deadline', 'text',
                                 'deliveries_available_before_deadline',
                                 'feedbacks_published', 'is_head',
                                 assignmentgroup=assignmentgroup,
                                 assignment=assignment,
                                 period=period,
                                 subject=subject
                                 )
        searchfields = FieldSpec('status', 'deadline',
                                 subject[1], subject[2],
                                 period[1], period[2],
                                 assignment[1], assignment[2],
                                 assignmentgroup[1], assignmentgroup[2], assignmentgroup[3]
                                 )
        methods = ['search', 'read', 'create', 'delete']

    @classmethod
    def create_searchqryset(cls, user):
        return cls._meta.model.where_is_admin_or_superadmin(user)

    @classmethod
    def read_authorize(cls, user_obj, obj):
        #TODO: Replace when issue #141 is resolved!
        if not user_obj.is_superuser:
            if not obj.assignment_group.is_admin(user_obj):
                raise PermissionDenied()

    @classmethod
    def write_authorize(cls, user_obj, obj):
        if not obj.assignment_group.can_save(user_obj):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedFileMeta(SimplifiedModelApi):
    class Meta:
        model = models.FileMeta
        resultfields = FieldSpec('filename', 'size', 'id',
                                 subject=['delivery__assignment_group__parentnode__parentnode__parentnode__long_name',
                                          'delivery__assignment_group__parentnode__parentnode__parentnode__short_name',
                                          'delivery__assignment_group__parentnode__parentnode__parentnode__id'],
                                 period=['delivery__assignment_group__parentnode__parentnode__long_name',
                                         'delivery__assignment_group__parentnode__parentnode__short_name',
                                         'delivery__assignment_group__parentnode__parentnode__id'],
                                 assignment=['delivery__assignment_group__parentnode__long_name',
                                             'delivery__assignment_group__parentnode__short_name',
                                             'delivery__assignment_group__parentnode__id']
                                 )
        searchfields = FieldSpec(
            # delivery__delivered_by
            'delivery__assignment_group__parentnode__parentnode__parentnode__long_name',  # subject
            'delivery__assignment_group__parentnode__parentnode__parentnode__short_name',  # subject
            'delivery__assignment_group__parentnode__parentnode__long_name',  # period
            'delivery__assignment_group__parentnode__parentnode__short_name',  # period
            'delivery__assignment_group__parentnode__long_name',  # assignment
            'delivery__assignment_group__parentnode__short_name',  # assignment
            'delivery__assignment_group__candidates__identifier',  # assignment
            'delivery__assignment_group__examiners__username',  # assignmen
            )

        methods = ['search', 'read']

    @classmethod
    def create_searchqryset(cls, user):
        return cls._meta.model.where_is_admin_or_superadmin(user)

    @classmethod
    def read_authorize(cls, user_obj, obj):
        #TODO: Replace when issue #141 is resolved!
        if not user_obj.is_superuser:
            if not obj.delivery.assignment_group.is_admin(user_obj):
                raise PermissionDenied()
