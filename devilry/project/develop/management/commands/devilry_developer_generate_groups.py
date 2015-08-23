from optparse import make_option
import re
from datetime import timedelta, datetime
from django.core.management.base import BaseCommand, CommandError
from devilry.devilry_account.models import User
import sys


class Command(BaseCommand):
    help = 'Create users and add them to .'
    args = '<assignment-path>'
    option_list = BaseCommand.option_list + (
        make_option(
            '--groupcount',
            type='int',
            default=10,
            help='Numbers of groups. Defaults to 10.'),
        make_option(
            '--groupsize',
            type='int',
            default=1,
            help='Numbers of candidates per group. Defaults to 1.'),
        make_option(
            '--username-prefix',
            default='student',
            help='Prefix for the autogenerated students. Defaults to "student".'),
    )

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('This command requires a single argument. See --help.')
        self.assignmentpath = args[0]
        self.groupsize = options['groupsize']
        self.groupcount = options['groupcount']
        self.username_prefix = options['username_prefix']
        self.verbosity = options['verbosity']
        self._find_assignment()
        self._create_users()
        self._create_groups()

    def _find_assignment(self):
        from devilry.apps.core.models import Assignment
        subject_short_name, period_short_name, assignment_short_name = self.assignmentpath.split('.')
        self.assignment = Assignment.objects.get(
            short_name=assignment_short_name,
            parentnode__short_name=period_short_name,
            parentnode__parentnode__short_name=subject_short_name)

    def _find_first_studentnumber(self):
        try:
            user = User.objects\
                .filter(username__startswith=self.username_prefix)\
                .order_by('-username')[0]
        except IndexError:
            return 1
        else:
            return int(re.match(r'^.+?(\d+)$', user.username).groups()[0]) + 1

    def _create_users(self):
        first_studentnumber = self._find_first_studentnumber()
        self.users = []
        for usernumber in xrange(first_studentnumber, first_studentnumber + self.groupcount * self.groupsize):
            username = '{}{:08}'.format(self.username_prefix, usernumber)
            self._print_message('Creating user: {}'.format(username))
            user = User.objects.create(
                username=username,
                fullname=u'{} {}'.format(self.username_prefix.title(), usernumber))
            self.users.append(user)

    def _create_groups(self):
        self._print_message('Creating {} groups with {} candidates in each group'.format(
            self.groupcount, self.groupsize))
        for groupnumber in xrange(self.groupcount):
            group = self.assignment.assignmentgroups.create()
            for candidatenumber in xrange(self.groupsize):
                user = self.users.pop()
                group.candidates.create(student=user)
            group.deadlines.create(
                deadline=datetime.now() + timedelta(days=2)
            )
            if self.verbosity > 1:
                sys.stdout.write('.')
                sys.stdout.flush()
        if self.verbosity > 1:
            print

    def _print_message(self, message):
        if self.verbosity > 0:
            print message
