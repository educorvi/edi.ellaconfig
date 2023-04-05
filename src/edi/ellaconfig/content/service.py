# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from z3c.relationfield.schema import RelationChoice
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from zope.interface import implementer
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import Invalid
from zope.interface import invariant
from plone.app.multilingual.browser.interfaces import make_relation_root_path

from edi.ellaconfig import _

servicetyp = SimpleVocabulary((
    SimpleTerm(value='service', token='service', title='Formular/Checkliste'),
    SimpleTerm(value='page', token='page', title='Seite'),
    SimpleTerm(value='group', token='group', title='Gruppe von Formularen oder Seiten'),
    SimpleTerm(value='audio', token='audio', title='Audiodatei(en)'),
    SimpleTerm(value='video', token='video', title='Videodatei(en)'),
))


class IService(model.Schema):
    """ Marker interface and Dexterity Python Schema for Service
    """

    servicetyp = schema.Choice(title=u"Servicetyp", default='service', vocabulary=servicetyp)

    serviceref = RelationChoice(title="Referenz auf das Formular (z.B. Checkliste), Seite oder Nachricht.",
                                vocabulary='plone.app.vocabularies.Catalog',
                                required=False)

    directives.widget(
        "serviceref",
        RelatedItemsFieldWidget,
        pattern_options={
            "basePath": make_relation_root_path,
            "selectableTypes": ["Fragebogen", "Document", "News Item", "Audiocontainer", "Videocontainer"],
        })

    @invariant
    def serviceref_invariant(data):
        if data.servicetyp == 'group':
            if data.serviceref:
                raise Invalid(u'Bei Typ = Gruppe von Services darf keine Referenz eingetragen werden.')
        else:
            if not data.serviceref:
                raise Invalid(u'Es muss eine Referenz auf ein Formular, Seite oder Nachricht eingetragen werden.')


@implementer(IService)
class Service(Container):
    """
    """
