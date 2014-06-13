from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form

# XXX: Uncomment for z3cform

from z3c.form import field

from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.relationfield.schema import RelationList, RelationChoice

from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from eappi.map import MessageFactory as _

class IEappiInternationalMap(IPortletDataProvider):
    """
    Define your portlet schema here
    """
    map_zoom = schema.Int(
        title=_('Map initial zoom'),
        required=False,
        default=1,
        )

    map_height = schema.Int(
        title=_('Map height (in px)'),
        default=350
        )

class Assignment(base.Assignment):
    implements(IEappiInternationalMap)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def title(self):
        return _('Eappi International Map')

class Renderer(base.Renderer):
    
    render = ViewPageTemplateFile('templates/eappiinternationalmap.pt')

    @property
    def available(self):
        return True

# XXX: z3cform
# class AddForm(z3cformhelper.AddForm):
class AddForm(base.AddForm):

#    XXX: z3cform
#    fields = field.Fields(IEappiInternationalMap)

    form_fields = form.Fields(IEappiInternationalMap)

    label = _(u"Add Eappi International Map")
    description = _(u"")

    def create(self, data):
        return Assignment(**data)

# XXX: z3cform
# class EditForm(z3cformhelper.EditForm):
class EditForm(base.EditForm):

#    XXX: z3cform
#    fields = field.Fields(IEappiInternationalMap)

    form_fields = form.Fields(IEappiInternationalMap)

    label = _(u"Edit Eappi International Map")
    description = _(u"")
