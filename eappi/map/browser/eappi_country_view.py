from five import grok
from plone.directives import dexterity, form
from eappi.map.content.eappi_country import IEappiCountry
from plone.memoize.view import memoize

grok.templatedir('templates')

class Index(dexterity.DisplayForm):
    grok.context(IEappiCountry)
    grok.require('zope2.View')
    grok.template('eappi_country_view')
    grok.name('view')
