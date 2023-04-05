# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
# from edi.ellaconfig.views.examples import uischema
from plone.i18n.normalizer import idnormalizer
from plone import api as ploneapi
import jsonlib
from jinja2 import Template

class EllaServiceView(BrowserView):

    def create_additional(self, addlist):
        reqs = list()
        props = dict()
        for prop in addlist:
            key = prop.get('addid')
            props[key] = dict()
            props[key]['title'] = prop.get('addtitle')
            props[key]['type'] = prop.get('addtype')
            if prop.get('pflichtfeld'):
                reqs.append(key)
        additional = dict()
        additional['type'] = 'object'
        additional['properties'] = props
        additional['required'] = reqs
        return additional

    def create_servicebuttons(self, buttons):
        servicebuttons = list()
        for button in buttons:
            servicebutton = dict()
            servicebutton['name'] = button.name
            servicebutton['title'] = button.title
            servicebutton['cssclass'] = button.cssclass
            servicebutton['method'] = button.method
            if button.modaltitle:
                servicebutton['modaltitle'] = button.modaltitle
            if button.modaltext:
                servicebutton['modaltext'] = button.modaltext
            if button.additional:
                servicebutton['additional'] = self.create_additional(button.additional)
            servicebuttons.append(servicebutton)
        return servicebuttons

    def create_single_service(self, service):
        ellaservice = dict()
        ellaservice['name'] = service.getId()
        ellaservice['title'] = service.title
        ellaservice['description'] = service.description
        ellaservice['type'] = service.servicetyp
        form = service.serviceref.to_object
        json_schema_view = ploneapi.content.get_view(name='schema-view', context=form, request=self.request)
        ellaservice['form'] = json_schema_view.__call__(localmarker=True)
        ui_schema_view = ploneapi.content.get_view(name='ui-schema-view', context=form, request=self.request)
        ellaservice['ui'] = ui_schema_view.__call__(localmarker=True)
        buttons = service.listFolderContents(contentFilter={"portal_type" : "Servicebutton"})
        ellaservice['formactions'] = self.create_servicebuttons(buttons)
        return ellaservice

    def create_group_service(self,service):
        servicelist = list()
        subservices = service.listFolderContents(contentFilter={"portal_type" : "Service"})
        for subservice in subservices:
            typ = subservice.servicetyp
            if typ == 'service':
                servicelist.append(self.create_single_service(subservice))
            else:
                servicelist.append(self.create_single_page(subservice))
        ellaservice = dict()
        ellaservice['name'] = service.getId()
        ellaservice['title'] = service.title
        ellaservice['description'] = service.description
        ellaservice['type'] = service.servicetyp
        ellaservice['services'] = servicelist
        return ellaservice

    def create_page_service(self, service):
        service = dict()
        service['name'] = service.getId()
        service['title'] = service.title
        service['description'] = service.description
        service['type'] = service.servicetyp
        pageobj = service.serviceref.to_object
        text = getattr(pageobj, 'text', u'')
        if text:
            text = text.output
        image = getattr(pageobj, 'image', u'')
        if image:
            image = '%s/@@download/image' % pageobj.absolute_url()
        service['text'] = self.format_ella_single(title, text, image)
        return service

    def get_ella_services(self, service):
        typ = service.servicetyp
        if typ == 'service':
            ella_service = self.create_single_service(service)
        elif typ == 'group':
            ella_service = self.create_group_service(service)
        else:
            ella_service = self.create_page_service(service)
        return ella_service

    def __call__(self):
        service = self.request.get('ella_service')
        serviceobj = ploneapi.content.find(context=self.context, portal_type='Service', id=service)
        ella_service = {}
        if serviceobj:
            obj = serviceobj[0].getObject()
            ella_service = self.get_ella_services(obj)
        return jsonlib.write(ella_service)
