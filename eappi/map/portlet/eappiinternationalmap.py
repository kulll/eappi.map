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
from plone.memoize import instance
from plone.memoize import view
from plone.memoize import forever
import json
from geopy import geocoders
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility
from wcc.vocabularies.countries import lookup_capital
from zope.annotation.interfaces import IAnnotations
from eappi.map import getSettings
import requests


class IEappiInternationalMap(IPortletDataProvider):
    """
    Define your portlet schema here
    """
    map_zoom = schema.Int(
        title=_('Map initial zoom'),
        required=False,
        default=1,
        )

    min_zoom = schema.Int(
        title=_('Minimum zoom'),
        required=False,
        default=1,
        )

    map_height = schema.Int(
        title=_('Map height (in px)'),
        default=350
        )

    marker_size = schema.Int(
        title=_('Map marker size'),
        default=5
        )

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

    @instance.memoize
    def _getcollection(self):
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

    @instance.memoize
    def map_marker(self, hidden=None):
        collection = self._getcollection()
        brains = collection.queryCatalog()
        vocab = getUtility(IVocabularyFactory, name='wcc.vocabulary.country')
        api_key = ''
        settings  = getSettings()
        if settings.openmapquest_api_key:
            api_key = settings.openmapquest_api_key

        if not brains:
            return None

        map_data = list()
        for i in brains:
            obj = i.getObject()
            country = vocab.name_from_code(obj.country_code)
            capital = lookup_capital(obj.country_code)
            
            if country == "C\xc3\xb4te d'Ivoire":
                query = "&country=Cote d'Ivoire"
            elif country in ['Netherlands Antilles']:
                query = "&location="+capital
            else:
                query ='&country='+country
                
            loc = requests.get('http://www.mapquestapi.com/geocoding/v1/address?key='+api_key+query)
            #if not loc:
            #    loc = requests.get('http:www//open.mapquestapi.com/geocoding/v1/address?key='+api_key+'&capital='+capital)
            
            
            
            #additional condition to fix problem with congo
            if not loc:
                return ''
            
            location = loc.json()
    
            #place, (lat, lng) = location
            if location['info']['statuscode'] == 0:
                lat = location['results'][0]['locations'][0]['latLng']['lat']
                lng = location['results'][0]['locations'][0]['latLng']['lng']
            else:
                lat = 0
                lng = 0
            
            #location = self.query_geolocation(country, capital)[1]
            #lat = location[0]
            #lng = location[1]

            # Empty bodytext will return none
            if obj.bodytext:
                text = obj.bodytext.output
            else:
                text = ''

            map_data.append(
                {'title': obj.title,
                 'body': text,
                 'lat': lat,
                 'lng': lng}
                )
        if hidden:
            return map_data
        return json.dumps(map_data)

    def _query_geolocation(self, country, capital):
        geo = geocoders.OpenMapQuest()

        try:
            location = geo.geocode(country)
        except IndexError:
            location = geo.geocode(capital)
        return location

    @instance.memoize
    def query_geolocation(self, country, capital):

        key = "cache-%s-%s" % (country, capital)

        cache = IAnnotations(self.data)
        data = cache.get(key, None)
        if not data:
            data = self._query_geolocation(country, capital)
            cache[key] = data
        return data
    
    @instance.memoize
    def static_map(self):
        source = 'https://www.mapquestapi.com/staticmap/v4/getmap?key='
        collection = self._getcollection()
        brains = collection.queryCatalog()
        vocab = getUtility(IVocabularyFactory, name='wcc.vocabulary.country')
        api_key = ''
        settings  = getSettings()
        if settings.openmapquest_api_key:
            api_key = settings.openmapquest_api_key
        
        source += api_key+'&size=900,500&type=map&imagetype=png&pois='
        if not brains:
            return None
        map_data = list()
        for brain in brains:
            obj = brain.getObject()
            country = vocab.name_from_code(obj.country_code)
            capital = lookup_capital(obj.country_code)
            
            if country == "C\xc3\xb4te d'Ivoire":
                query = "&country=Cote d'Ivoire"
            elif country in ['Netherlands Antilles']:
                query = "&location="+capital
            else:
                query ='&country='+country
            
            loc = requests.get('http://www.mapquestapi.com/geocoding/v1/address?key='+api_key+query)
            if not loc:
                return ''
            
            location = loc.json()
    
            #place, (lat, lng) = location
            if location['info']['statuscode'] == 0:
                lat = location['results'][0]['locations'][0]['latLng']['lat']
                lng = location['results'][0]['locations'][0]['latLng']['lng']
            else:
                lat = 0
                lng = 0
            
            map_data.append(
                {'title':obj.title,
                 'lat': lat,
                 'lng': lng})
        
        if len(map_data):
            for mapd in map_data:
                indx = map_data.index(mapd)
                
                source += str(indx+1)+','+str(mapd['lat'])+','+str(mapd['lng'])
                if indx == 0:
                    source += ',0,0'
                if (indx+1) != len(map_data):
                    source += '|'
        
    
        return source
    
    @instance.memoize
    def mapquest_api_key(self):
        api_key = ''
        settings  = getSettings()
        if settings.openmapquest_api_key:
            api_key = settings.openmapquest_api_key
        return api_key
    
    @instance.memoize
    def geocode_map(self):
        collection = self._getcollection()
        if not collection:
            return []
        brains = collection.queryCatalog()
        vocab = getUtility(IVocabularyFactory, name='wcc.vocabulary.country')
        countries = []
        if not brains:
            return countries
        for brain in brains:
            obj = brain.getObject()
            country = vocab.name_from_code(obj.country_code)
            capital = lookup_capital(obj.country_code)
            if country == "C\xc3\xb4te d'Ivoire":
                countries.append("Cote d'Ivoire")
            elif country in ['Netherlands Antilles']:
                countries.append(capital)
            else:
                countries.append(country)
        return countries
    
    @instance.memoize
    def orig_country_names(self):
        collection = self._getcollection()
        if not collection:
            return []
        brains = collection.queryCatalog()
        vocab = getUtility(IVocabularyFactory, name='wcc.vocabulary.country')
        countries = {}
        if not brains:
            return countries
        for brain in brains:
            obj = brain.getObject()
            country = vocab.name_from_code(obj.country_code)
            capital = lookup_capital(obj.country_code)
            if country not in countries.keys():
                if country == "C\xc3\xb4te d'Ivoire":
                    countries["Cote d'Ivoire"] = "Cote d'Ivoire"
                elif country in ['Netherlands Antilles']:
                    countries[capital] = 'Netherlands Antilles'
                else:
                    countries[country] = country
        return countries
        
        
        


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
