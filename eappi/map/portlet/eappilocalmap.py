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
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from eappi.map import getSettings
from plone.memoize import instance
from AccessControl import getSecurityManager


class IEappiLocalMap(IPortletDataProvider):
    """
    Define your portlet schema here
    """
    jerusalem = schema.Choice(
        title=_(u'Jerusalem'),
        description=_(u''),
        source=SearchableTextSourceBinder(
            {'portal_type': ('Document')})
        )

    northern_west_bank = schema.Choice(
        title=_(u'Northern West Bank'),
        description=_(u''),
        source=SearchableTextSourceBinder(
            {'portal_type': ('Document')})
        )

    southern_west_bank = schema.Choice(
        title=_(u'Southern West Bank'),
        description=_(u''),
        source=SearchableTextSourceBinder(
            {'portal_type': ('Document')})
        )

    jordan_valley = schema.Choice(
        title=_(u'Jordan Valley'),
        description=_(u''),
        source=SearchableTextSourceBinder(
            {'portal_type': ('Document')})
        )

    zoom = schema.Int(
        title=_(u'Map initial zoom'),
        description=_(u''),
    )

    min_zoom = schema.Int(
        title=_(u'Map minimum zoom'),
        description=_(u''),
    )

    map_height = schema.Int(
        title=_(u'Map height (in px)'),
        description=_(u''),
    )


class Assignment(base.Assignment):
    implements(IEappiLocalMap)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def title(self):
        return _('Eappi Local Map')

class Renderer(base.Renderer):
    
    render = ViewPageTemplateFile('templates/eappilocalmap.pt')
    
    @instance.memoize
    def _getcollection(self, target):
        collection_path = getattr(self.data,target)
        if not collection_path:
            return None

        if collection_path.startswith('/'):
            collection_path = collection_path[1:]

        if not collection_path:
            return None

        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        if isinstance(collection_path, unicode):
            # restrictedTraverse accepts only strings
            collection_path = str(collection_path)

        result = portal.unrestrictedTraverse(collection_path, default=None)
        if result is not None:
            sm = getSecurityManager()
            if not sm.checkPermission('View', result):
                result = None
        return result

    @property
    def available(self):
        return True
    
    @instance.memoize
    def mapquest_api_key(self):
        api_key = ''
        settings  = getSettings()
        if settings.openmapquest_api_key:
            api_key = settings.openmapquest_api_key
        return api_key
    
    
    @instance.memoize
    def contents(self):
        data = {}
        
        data['Amman'] = self._getcollection('jordan_valley').absolute_url()
        data['Jerusalem'] = self._getcollection('jerusalem').absolute_url()
        data['Ramallah'] = self._getcollection('northern_west_bank').absolute_url()
        data['Hebron'] = self._getcollection('southern_west_bank').absolute_url()
        return data
        


# XXX: z3cform
# class AddForm(z3cformhelper.AddForm):
class AddForm(base.AddForm):

#    XXX: z3cform
#    fields = field.Fields(IEappiLocalMap)

    form_fields = form.Fields(IEappiLocalMap)
    form_fields['jerusalem'].custom_widget = UberSelectionWidget
    form_fields['northern_west_bank'].custom_widget = UberSelectionWidget
    form_fields['southern_west_bank'].custom_widget = UberSelectionWidget
    form_fields['jordan_valley'].custom_widget = UberSelectionWidget

    label = _(u"Add Eappi Local Map")
    description = _(u"")

    def create(self, data):
        return Assignment(**data)


# XXX: z3cform
# class EditForm(z3cformhelper.EditForm):
class EditForm(base.EditForm):

#    XXX: z3cform
#    fields = field.Fields(IEappiLocalMap)

    form_fields = form.Fields(IEappiLocalMap)
    form_fields['jerusalem'].custom_widget = UberSelectionWidget
    form_fields['northern_west_bank'].custom_widget = UberSelectionWidget
    form_fields['southern_west_bank'].custom_widget = UberSelectionWidget
    form_fields['jordan_valley'].custom_widget = UberSelectionWidget

    label = _(u"Edit Eappi Local Map")
    description = _(u"")
