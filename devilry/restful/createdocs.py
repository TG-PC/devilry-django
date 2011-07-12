"""
Autogenerate documentation RESTful APIs
"""
from random import randint
from os.path import join
from django.template import Context, Template
from django.db.models import fields

from devilry.simplified import SimplifiedModelApi
from devilry.simplified.utils import get_field_from_fieldname, get_clspath



CREATE_DOCS = '''Create a {{doc.model_verbose_name}}.
'''
READ_DOCS = '''Retreive a {{doc.model_verbose_name}}.
'''
UPDATE_DOCS = '''Update a {{doc.model_verbose_name}}.
'''
DELETE_DOCS = '''Delete a {{doc.model_verbose_name}}.
'''
SEARCH_DOCS = '''Search for {{doc.model_verbose_name_plural}}.


Parameters
##########


query
-----
A string to search for.


{% if doc.filters %}

filters
---------------

A list of filters, where each filter is a map with the following entries:

    field
        A field name.
    comp
        A comparison operator.
    value
        The value to filter on.

Example:

    .. code-block:: javascript

{{ doc.filterexample|safe }}

{{doc.model_verbose_name_plural}} can be filtered on the following *fields*:
{% if doc.filters.filterspecs %}
{% for fs in doc.filterspecs %}
    {{ fs.filterspec.fieldname }}
        About the field:
            {{ fs.help_text|safe|default:"MISSING HELP TEXT" }}
        Type
            {{ fs.fieldtype }}
        Supported comparison operators:
            {%for comp in fs.filterspec.supported_comp%}``{{comp|safe}}``{%if not forloop.last%}, {%endif%}{%endfor%}.
{% endfor %}
{% endif %}
{% if doc.filters.patternfilterspecs %}
    Filters matching the following python compatible regular expressions:
    {% for filterspec in doc.patternfilterspecs %}
        ``{{ filterspec.fieldname }}``
            Supported comparison operators:
            {%for comp in filterspec.supported_comp%}``{{comp|safe}}``{%if not forloop.last%}, {%endif%}{%endfor%}.
    {% endfor %}
{% endif %}

{%endif%}

orderby
-------
List of fieldnames. Order the result by these fields.
Fieldnames can be prefixed by ``'-'`` for descending ordering.
Example: TODO generate ordeby example.

start
-----
After query, filters and orderby have been executed, the result is limited to
the values from *start* to *start+limit*. Start defalts to ``0``.

limit
-----
Limit results to this number of items. Defaults to ``50``.

{% if doc.result_fieldgroups %}
result_fieldgroups
------------------
Adds additional fields to each item in the result.
{{doc.result_fieldgroups}}

The fields are documented in :class:`{{doc.modelmodulename}}.{{doc.modelclsname}}`.
Follow fields containing ``__`` through the corrensponding related attributes.
{% endif %}



{% if doc.search_fieldgroups %}
search_fieldgroups
------------------
Adds additional fields which are searched for the ``query`` string.

{{doc.search_fieldgroups}}

The fields are documented in :class:`{{doc.modelmodulename}}.{{doc.modelclsname}}`.
Follow fields containing ``__`` through the corrensponding related attributes.
{% endif %}



Return
######

TODO: Autogenereate return example(s) containing fields.


Notes for non-standard extensions
#################################

TODO: getdata_in_qrystring and X-header
'''


def field_to_restfultype(field):
    if isinstance(field, fields.related.AutoField):
        return 'Integer', 15
    elif isinstance(field, fields.CharField):
        return 'String', 'myvalue'
    else:
        raise ValueError('Unsupported field type.')

def field_to_help_text(field):
    help_text = field.help_text
    if isinstance(field, fields.related.AutoField):
        help_text = 'Autogenerated identifier.'
    elif not help_text or help_text.strip() == '':
        raise ValueError('Missing help for: {0}.{1}'.format(get_clspath(field.model), field.name))


class Docstring(object):
    def __init__(self, docstring, restfulcls):
        self.docstring = Template(docstring)
        self.restfulcls = restfulcls
        simplified = restfulcls._meta.simplified
        model = simplified._meta.model

        self.modelclsname = model.__name__
        self.modelmodulename = model.__module__
        if self.modelmodulename.endswith('.' + self.modelclsname.lower()):
            self.modelmodulename = self.modelmodulename.rsplit('.', 1)[0]
        self.modelclspath = '{0}.{1}'.format(self.modelmodulename, self.modelclsname)
        self.model_verbose_name = model._meta.verbose_name
        self.model_verbose_name_plural = model._meta.verbose_name_plural
        self.model = model

        self.result_fieldgroups = self._create_fieldgroup_overview(simplified._meta.resultfields.additional_fieldgroups)
        self.search_fieldgroups = self._create_fieldgroup_overview(simplified._meta.searchfields.additional_fieldgroups)
        self._create_filter_docattrs()

        self.context = Context(dict(doc=self))

    def _create_filter_docattrs(self):
        self.filters = self.restfulcls._meta.simplified._meta.filters
        self.filterspecs = []
        for filterspec in sorted(self.filters.filterspecs.values(), key=lambda s: s.fieldname):
            field = self._get_field(filterspec.fieldname)
            help_text = field_to_help_text(field)
            fieldtype, valueexample = field_to_restfultype(field)
            self.filterspecs.append(dict(filterspec=filterspec,
                                         help_text=help_text,
                                         fieldtype=fieldtype,
                                         valueexample=valueexample))

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
                                                                repr(fs['valueexample']))
            filterexample.append(example)
        filterexample = '[{0}]'.format(',\n '.join(filterexample))
        self.filterexample = self._indent(filterexample, '        ')

    def _indent(self, value, indent):
        return '\n'.join('{0}{1}'.format(indent, line) for line in value.split('\n'))


    def _create_fieldgroup_overview(self, fieldgroups):
        if not fieldgroups:
            return ''
        result = ['Available values are:', '']
        for fieldgroup, fieldgroupfields in fieldgroups.iteritems():
            result.append(fieldgroup)
            result.append('    Expands to the following fields: ' + ', '.join(fieldgroupfields))
        return '\n    '.join(result)

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
                               indexitems='\n    '.join(unicode(i) for i in self.indexitems))

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
                indexitems.append(IndexItem(refprefix, methodname, httpmethod, itemurl, Docstring(docs, restfulcls)))
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
