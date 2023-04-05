# -*- coding: utf-8 -*-
from edi.ellaconfig import _
from edi.ellaconfig.content.service import servicetyp
from Products.Five.browser import BrowserView

class EllaKonfigView(BrowserView):

    def __call__(self):
        self.services = self.get_services()
        return self.index()

    def get_services(self):
        servicelist = list()
        services = self.context.listFolderContents()
        for service in services:
            listentry = dict()
            listentry['subservices'] = None
            listentry['title'] = service.title
            listentry['typ'] = servicetyp.getTerm(service.servicetyp).title
            if service.servicetyp == 'group':
                listentry['subservices'] = len(service.listFolderContents(contentFilter={"portal_type" : "Service"}))
            listentry['url'] = service.absolute_url()
            servicelist.append(listentry)
        return servicelist
