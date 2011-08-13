"""
Autogenerate documentation RESTful APIs
"""
import json
from random import randint
from os.path import join, dirname
from django.template import Context, Template
from django.db.models import fields

from devilry.simplified import SimplifiedModelApi
from devilry.simplified.utils import get_field_from_fieldname, get_clspath




#
# Fetch templates from the 
#
this_dir = dirname(__file__)
def read_tpl(name):
    return open(join(this_dir, 'createdocs_tpl', '{0}.django.rst'.format(name))).read()
SEARCH_DOCS = read_tpl('search')
CREATE_DOCS = read_tpl('create')
READ_DOCS = read_tpl('read')
UPDATE_DOCS = read_tpl('update')
DELETE_DOCS = read_tpl('delete')





#
# Horrible code from here and down. Read at your own risc.
#



def get_model_clspath(model):
    modelclsname = model.__name__
    modelmodulename = model.__module__
    if modelmodulename.replace('_', '').endswith('.' + modelclsname.lower()): # .....assignment_group.AssignmentGroup -> AssignmentGroup
        modelmodulename = modelmodulename.rsplit('.', 1)[0]
    return '{0}.{1}'.format(modelmodulename, modelclsname)


def field_to_restfultype(field):
    if isinstance(field, fields.related.AutoField):
        return 'Integer', 15
    elif isinstance(field, fields.CharField):
        if field.name == 'short_name':
            return 'String', '"my_example001_value"'
        else:
            return 'String', '"My example value"'
    elif isinstance(field, fields.TextField):
        return 'String', '"myvalue"'
    elif isinstance(field, fields.BooleanField):
        return 'Boolean', 'true'
    elif isinstance(field, fields.IntegerField):
        return 'Integer', '20'
    elif isinstance(field, fields.DateTimeField):
        return 'DateTime string (YYYY-MM-DD hh:mm:ss)', '"2010-02-22 22:32:10"'
    elif isinstance(field, fields.related.ManyToManyField) or isinstance(field, fields.related.RelatedObject):
        return 'List of strings', '["this", "is", "an", "example"]'
    else:
        raise ValueError('Unsupported field type: {0}'.format(type(field)))

def field_to_help_text(field):
    if isinstance(field, fields.related.AutoField):
        return 'Autogenerated identifier.'
    elif isinstance(field, fields.related.ManyToManyField) or isinstance(field, fields.related.RelatedObject):
        return 'List of many values.'
    help_text = field.help_text
    if not help_text or help_text.strip() == '':
        raise ValueError('Missing help for: {0}.{1}'.format(get_clspath(field.model), field.name))
    return help_text


class Docstring(object):
    def __init__(self, docstring, restfulcls, httpmethod, itemurl):
        self.docstring = Template(docstring)
        self.restfulcls = restfulcls
        self.httpmethod = httpmethod
        self.itemurl = itemurl
        if itemurl.endswith('id**'):
            self.itemexampleurl = itemurl[:-4] + '10'
        else:
            self.itemexampleurl = itemurl
        simplified = restfulcls._meta.simplified
        model = simplified._meta.model

        self.modelclspath = get_model_clspath(model)
        self.model_verbose_name = model._meta.verbose_name
        self.model_verbose_name_plural = model._meta.verbose_name_plural
        self.model = model

        self.result_fieldgroups = self._create_fieldgroup_overview(simplified._meta.resultfields.additional_fieldgroups)
        self.result_fieldgroups_example = self._create_jslist(simplified._meta.resultfields.additional_fieldgroups.keys())
        self.search_fieldgroups = self._create_fieldgroup_overview(simplified._meta.searchfields.additional_fieldgroups)
        self.search_fieldgroups_example = self._create_jslist(simplified._meta.searchfields.additional_fieldgroups.keys())

        self.searchfields = self._create_fieldinfolist(simplified._meta.searchfields.always_available_fields)
        self.resultfields = self._create_fieldinfolist(simplified._meta.resultfields.always_available_fields)
        self.editablefields = self._create_fieldinfolist(simplified._meta.editablefields)
        self.editablefields_and_id = self._create_fieldinfolist(list(simplified._meta.editablefields) + ['id'])
        self._create_filter_docattrs()

        self.orderby_example = self._create_orderby_jslist(simplified._meta.resultfields.aslist())

        self.simplifiedclspath = get_clspath(simplified)
        #for method in simplified._meta.methods:
            #setattr(self, 'simplified_{0}methodpath'.format(method), )

        self.context = Context(dict(doc=self))

    def _create_fieldnamelist(self, fieldnames):
        return ', '.join('``{0}``'.format(fieldname) for fieldname in fieldnames)


    def _fieldinfo_dict(self, field):
        modelclspath = get_model_clspath(field.model)
        help_text = field_to_help_text(field)
        fieldtype, valueexample = field_to_restfultype(field)
        return dict(help_text=help_text,
                    fieldtype=fieldtype,
                    modelclspath=modelclspath,
                    valueexample=valueexample)

    def _fieldinfo_dict_for_annotatedfield(self):
        return dict(help_text="Generated from a query.",
                    fieldtype="unknown",
                    modelclspath="Generated from a query",
                    valueexample='No example-value available for this field')

    def _create_filter_docattrs(self):
        self.filters = self.restfulcls._meta.simplified._meta.filters
        self.filterspecs = []
        for filterspec in sorted(self.filters.filterspecs.values(), key=lambda s: s.fieldname):
            if filterspec.fieldname in self.restfulcls._meta.simplified._meta.annotated_fields:
                fs = self._fieldinfo_dict_for_annotatedfield()
            else:
                field = self._get_field(filterspec.fieldname)
                fs = self._fieldinfo_dict(field)
            fs['filterspec'] = filterspec
            self.filterspecs.append(fs)

        self.patternfilterspecs = sorted(self.filters.patternfilterspecs, key=lambda s: s.fieldname)
        self._create_filter_example()

    def _create_filter_example(self):
        filterexample = []
        for fs in self.filterspecs[:3]:
            filterspec = fs['filterspec']
            supported_comp = list(filterspec.supported_comp)
            compindex = randint(0, len(supported_comp)-1)
            example = '{{field:"{0}", comp:"{1}", value:{2}}}'.format(filterspec.fieldname,
                                                                supported_comp[compindex],
                                                                fs['valueexample'])
            filterexample.append(example)
        filterexample = '[{0}]'.format(',\n '.join(filterexample))
        self.filterexample = self._indent(filterexample, '        ')
        self.filterexample_for_overview = self._indent(filterexample, '                     ').lstrip()

    def _indent(self, value, indent):
        return '\n'.join('{0}{1}'.format(indent, line) for line in value.split('\n'))

    def _create_fieldinfolist(self, fieldnames, exclude=None):
        infolist = []
        for fieldname in fieldnames:
            if exclude and exclude == fieldname:
                continue
            if fieldname in self.restfulcls._meta.simplified._meta.annotated_fields:
                info = self._fieldinfo_dict_for_annotatedfield()
            else:
                info = self._fieldinfo_dict(self._get_field(fieldname))
            info['fieldname'] = fieldname
            infolist.append(info)
        return infolist

    def _create_fieldgroup_overview(self, fieldgroups):
        result = []
        for fieldgroup, fieldgroupfields in fieldgroups.iteritems():
            result.append(dict(fieldgroup=fieldgroup,
                               fieldinfolist=self._create_fieldinfolist(fieldgroupfields)))
        return result

    def _create_jslist(self, iterable):
        return json.dumps(list(iterable))

    def _create_orderby_jslist(self, fieldnames):
        fieldnames = list(fieldnames)
        if len(fieldnames) > 1:
            fieldnames[1] = '-' + fieldnames[1]
        return json.dumps(fieldnames)

    def get_first_para(self):
        return str(self).split('\n\n')[0].replace('\n', ' ')

    def __str__(self):
        return self.docstring.render(self.context)

    def _get_field(self, fieldname):
        return get_field_from_fieldname(self.model, fieldname, fkfield_as_idfield=True)



class Page(object):
    TPL = '''.. _{ref}:

=============================================================================
{httpmethod} {url}
=============================================================================

{docs}'''
    def __init__(self, refprefix, methodname, httpmethod, url, docs):
        self.httpmethod = httpmethod
        self.url = url
        self.docs = docs
        self.ref = '{0}_details_{1}'.format(refprefix, methodname) # id usable by rst :ref:
        self.filename = '{0}.rst'.format(self.ref)

    def __unicode__(self):
        return self.TPL.format(**self.__dict__)

    def get_filepath(self, directory):
        return join(directory, self.filename)

    def write_to_dir(self, directory):
        open(self.get_filepath(directory), 'wb').write(unicode(self).encode('utf-8'))



class IndexItem(object):
    TPL = '''
    <tr>
        <th><a href="{pageref}.html">{httpmethod}&nbsp;{prettyrestfulurl}</a></th>
        <td>{first_para}</td>
    </tr>'''
    def __init__(self, refprefix, methodname, httpmethod, url, docs):
        self.httpmethod = httpmethod
        self.url = url
        self.prettyrestfulurl = url
        if url.endswith('id'):
            self.prettyrestfulurl = self.prettyrestfulurl[:-2]
            self.prettyrestfulurl += '<span class="restfulid">id</span>'
        self.first_para = docs.get_first_para()
        self.page = Page(refprefix, methodname, httpmethod, url, docs)

    def __unicode__(self):
        return self.TPL.format(pageref=self.page.ref, **self.__dict__)

    def __cmp__(self, other):
        """ Ordering: search, read, create, update, delete """
        if self.httpmethod == 'DELETE':
            return 1
        return cmp(self.httpmethod+self.url, other.httpmethod+other.url)


class IndexPageItem(object):
    TPL = '''
{modelclsname}
-------------------------------------------------------------------------

.. raw:: html

    <table class="restfulindex">
        <thead>
            <tr>
                <th>Resource</th>
                <td>Description</td>
            </tr>
        </thead>
        <tbody>
            {indexitems}
        </tbody>
    </table>
'''
    def __init__(self, restfulcls, indexitems):
        self.restfulcls = restfulcls
        self.simplifiedclsname = self.restfulcls._meta.simplified.__name__
        self.modelclsname = self.restfulcls._meta.simplified._meta.model.__name__
        self.indexitems = indexitems

    def __unicode__(self):
        return self.TPL.format(simplifiedclsname=self.simplifiedclsname,
                               modelclsname=self.modelclsname,
                               indexitems='\n    '.join(unicode(i) for i in sorted(self.indexitems)))

    def iterpages(self):
        for indexitem in self.indexitems:
            yield indexitem.page




class IndexPage(object):
    TPL = '''.. _{ref}:

===============================================================
{indextitle}
===============================================================

.. toctree::
    :hidden:

    {toctree}

{items}'''
    def __init__(self, indexpageitems, ref, indextitle):
        self.items = '\n\n'.join(unicode(indexpageitem) for indexpageitem in indexpageitems)
        toctreerefs = []
        for indexpageitem in indexpageitems:
            for page in indexpageitem.iterpages():
                toctreerefs.append(page.ref)
        self.toctree = '\n    '.join(toctreerefs)
        self.ref = ref
        self.indextitle = indextitle

    def __unicode__(self):
        return self.TPL.format(**self.__dict__)

    def write(self, filepath):
        open(filepath, 'wb').write(unicode(self).encode('utf-8'))



class RestfulDocs(object):
    CRUD_TO_HTTP = {'create': ('POST', False, CREATE_DOCS),
                    'read': ('GET', True, READ_DOCS),
                    'update': ('PUT', True, UPDATE_DOCS),
                    'delete': ('DELETE', True, DELETE_DOCS),
                    'search': ('GET', False, SEARCH_DOCS)}
    def iter_restfulcls_methods(self, restfulcls):
        for methodname in restfulcls._meta.simplified._meta.methods:
            if methodname.startswith('insecure_'):
                continue
            method = getattr(SimplifiedModelApi, methodname)
            yield methodname

    def _get_restfulcls_docprefix(self, restfulcls):
        appname = restfulcls.__module__.split('.')[-2] # Assume restful is in appdir.restful
        return '{0}_{1}'.format(appname, restfulcls.__name__.lower())

    def iter_restfulmanager_docs(self, restfulmanager):
        for restfulcls in restfulmanager.iter_restfulclasses():
            refprefix = self._get_restfulcls_docprefix(restfulcls)
            url = restfulcls.get_rest_url()
            indexitems = []
            for methodname in self.iter_restfulcls_methods(restfulcls):
                httpmethod, hasid, docs = self.CRUD_TO_HTTP[methodname]
                if hasid:
                    itemurl = '{0}id'.format(url)
                else:
                    itemurl = url
                indexitems.append(IndexItem(refprefix, methodname, httpmethod, itemurl,
                                            Docstring(docs, restfulcls, httpmethod, itemurl)))
            yield IndexPageItem(restfulcls, indexitems)

    def restfulmanager_docs_to_rstfiles(self, directory, indexpageitem):
        for page in indexpageitem.iterpages():
            page.write_to_dir(directory)

    def create_in_directory(self, directory, indexpageref, indextitle, restfulmanager):
        indexpageitems = []
        for indexpageitem in self.iter_restfulmanager_docs(restfulmanager):
            indexpageitems.append(indexpageitem)
            self.restfulmanager_docs_to_rstfiles(directory, indexpageitem)
        indexpage = IndexPage(indexpageitems, indexpageref, indextitle)
        indexpage.write(join(directory, 'index.rst'))
