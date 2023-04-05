# -*- coding: utf-8 -*-
# from plone.app.vocabularies.catalog import CatalogSource
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from plone.app.multilingual.browser.interfaces import make_relation_root_path
from zope.interface import Invalid
from zope.interface import invariant

from edi.ellaconfig import _

default_template = \
    """<div class="card mb-3">
         <img src="{{ ella_image }}" class="card-img-top" alt="Titelbild der App">
         <div class="card-body">
           <h5 class="card-title">{{ ella_title }}</h5>
           {{ ella_bodytext }}
         </div>
       </div>"""


def check_groupname(value):
    """Check that the postcode starts with a 6
    """
    if len(value.split('#')) != 2:
        raise Invalid(u"Achten Sie auf die korrekte Schreibweise: Name#Titel. Das Hashzeichen bildet die Trennung")
    return True


class IEllaKonfig(model.Schema):
    """ Marker interface and Dexterity Python Schema for EllaKonfig
    """

    startseiten = RelationList(
        title=u"Referenz auf eine oder mehrere Startseiten",
        description="Referenzieren Sie hier auf eine oder mehrere Startseiten. Mehrere Startseiten dem Benutzer werden als Tour angezeigt.",
        default=[],
        value_type=RelationChoice(vocabulary='plone.app.vocabularies.Catalog'),
        required=False)

    directives.widget(
        "startseiten",
        RelatedItemsFieldWidget,
        vocabulary='plone.app.vocabularies.Catalog',
        pattern_options={
            "basePath": make_relation_root_path,
            "selectableTypes": ["News Item", "Document"]})

    groupname = schema.TextLine(title=u"Name und Titel der Gruppe (Tour) bei mehreren Startseiten.",
                                description=u"Schreibweise: Name#Titel. Muss eingesetzt werden, wenn mehrere Startseiten konfiguriert werden.",
                                constraint=check_groupname, required=False)

    bodytemplate = schema.Text(title="HTML-Template der Startseite",
                               default=default_template,
                               description="Das Template kann die Jinja-Variablen {{ella_title }}, {{ ella_bodytext }} und {{ ella_image }} enthalten.")

    bodytext = RichText(title=u"Alternativ: Haupttext der Startseite der Ella-App",
                        description="Wenn keine Startseite verknüpft wurde, kann hier ein Haupttext eingetragen werden. Der Haupttext wird\
                         in die Variable {{ ella_bodytext }} des HTML-Templates eingefügt.", required=False)

    image = NamedBlobImage(title=u"Alternativ: Titelbild der Startseite",
                           description="Wenn keine Startseite verknüpft wurde, kann hier ein Startbild hochgeladen werden. Das Bild wird\
                    in die Variable {{ ella_image }} des HTML-Templates eingefügt.", required=False)

    @invariant
    def verweis_invariant(data):
        if data.startseiten:
            if not data.groupname:
                raise Invalid(
                    u"Bei mehreren Startseiten muss für die Gruppe der Startseiten Name und Titel eingetragen werden.")
            if data.bodytext or data.image:
                raise Invalid(u"Es dürfen entweder eine oder mehrere Startseiten verküpft werden oder Haupttext und Titelbild\
                              eingetragen werden.")
        else:
            if not data.bodytext:
                raise Invalid(u"Wenn keine Startseiten verküpft wurden muss mindestens der Haupttext der Startseite der Ella-App\
                              bearbeitet werden.")


@implementer(IEllaKonfig)
class EllaKonfig(Container):
    """
    """
