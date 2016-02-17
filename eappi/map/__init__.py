from zope.interface import implements
from Products.CMFQuickInstallerTool.interfaces import INonInstallable
from five import grok
from collective.grok import gs
from zope.i18nmessageid import MessageFactory
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from eappi.map.interfaces import IEappiSettings

# Set up the i18n message factory for our package
MessageFactory = MessageFactory('eappi.map')

_ = MessageFactory

class HiddenProducts(grok.GlobalUtility):
    """This hides the upgrade profiles from the quick installer tool."""
    implements(INonInstallable)
    grok.name('eappi.map.upgrades')

    def getNonInstallableProducts(self):
        return [
            'eappi.map.upgrades',
        ]

gs.profile(name=u'default',
           title=u'eappi.map',
           description=_(u''),
           directory='profiles/default')

def getSettings():
    registry = getUtility(IRegistry)
    try:
        return registry.forInterface(IEappiSettings)
    except:
        registry.registerInterface(IEappiSettings)
    return registry.forInterface(IEappiSettings)
