from collective.grok import gs
from eappi.map import MessageFactory as _
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from eappi.map.interfaces import IEappiSettings

@gs.importstep(
    name=u'eappi.map', 
    title=_('eappi.map import handler'),
    description=_(''))
def setupVarious(context):
    if context.readDataFile('eappi.map.marker.txt') is None:
        return
    portal = context.getSite()
    registry = getUtility(IRegistry)
    registry.registerInterface(IEappiSettings)

    # do anything here
