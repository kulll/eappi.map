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
from Products.ATContentTypes.interfaces.topic import IATTopic
from plone.app.collection.interfaces import ICollection
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from AccessControl import getSecurityManager
from plone.memoize.instance import memoize
import json
from geopy import geocoders


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

    """
    Define your portlet schema here
    """

    target_collection = schema.Choice(
        title=_(u"Target collection"),
        description=_(u"Find the collection which provides the items to display"),
        required=True,
        source=SearchableTextSourceBinder(
            {'portal_type': ('Topic', 'Collection')},
            default_query='path:'))


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

    @memoize
    def collection(self):
        collection_path = self.data.target_collection
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

    @memoize
    def map_marker(self):
        collection = self.collection()
        brains = collection.queryCatalog()

        if not brains:
            return None

        map_data = list()
        for i in brains:
            obj = i.getObject()
            lat = self._query_geolocation(obj.title)[0]
            lng = self._query_geolocation(obj.title)[1]
            map_data.append(
                {'title': obj.title,
                 'body': obj.getText(),
                 'lat': lat,
                 'lng': lng}
                )
        return json.dumps(map_data)

    @memoize
    def _query_geolocation(self, country):
        geo = geocoders.OpenMapQuest()
        location = geo.geocode(country)
        return location[1]


# XXX: z3cform
# class AddForm(z3cformhelper.AddForm):
class AddForm(base.AddForm):

#    XXX: z3cform
#    fields = field.Fields(IEappiInternationalMap)

    form_fields = form.Fields(IEappiInternationalMap)
    form_fields['target_collection'].custom_widget = UberSelectionWidget

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
    form_fields['target_collection'].custom_widget = UberSelectionWidget


    label = _(u"Edit Eappi International Map")
    description = _(u"")
