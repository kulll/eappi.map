from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import alsoProvides

from zope.interface import invariant, Invalid

from z3c.form import group, field

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.multilingualbehavior.directives import languageindependent
from collective import dexteritytextindexer

from eappi.map import MessageFactory as _


# Interface class; used to define content-type schema.

class IEappiCountry(form.Schema, IImageScaleTraversable):
    """

    """
    bodytext = RichText(
        title=_('Body Text'),
        description=_('Keep the body text short as it will go into the map'),
        required=False,
        )

#country_code necessary due to multilingual issue
    country_code = schema.Choice(
        title=_(u'Country Code'),
        description=_(u'ISO 3166-1 alpha-2 code for this country'),
        required=True,
        vocabulary='wcc.vocabulary.country'
    )


alsoProvides(IEappiCountry, IFormFieldProvider)
