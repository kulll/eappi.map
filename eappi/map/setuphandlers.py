from collective.grok import gs
from eappi.map import MessageFactory as _

@gs.importstep(
    name=u'eappi.map', 
    title=_('eappi.map import handler'),
    description=_(''))
def setupVarious(context):
    if context.readDataFile('eappi.map.marker.txt') is None:
        return
    portal = context.getSite()

    # do anything here
