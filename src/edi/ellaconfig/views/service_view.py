# -*- coding: utf-8 -*-

from edi.ellaconfig import _
from Products.Five.browser import BrowserView
from edi.ellaconfig.content.service import servicetyp

class ServiceView(BrowserView):

    def __call__(self):
        self.group = False
        if self.context.servicetyp == 'group':
            self.group = True
        self.buttons = self.get_buttons()
        self.services = self.get_services()
        self.servicetyp = servicetyp.getTerm(self.context.servicetyp).title
        return self.index()

    def get_services(self):
        servicelist = list()
        services = self.context.listFolderContents(contentFilter={"portal_type" : "Service"})
        for service in services:
            listentry = dict()
            listentry['title'] = service.title
            listentry['typ'] = servicetyp.getTerm(service.servicetyp).title
            listentry['url'] = service.absolute_url()
            servicelist.append(listentry)
        return servicelist

    def get_buttons(self):
        buttonlist = list()
        buttons = self.context.listFolderContents(contentFilter={"portal_type" : "Servicebutton"})
        for button in buttons:
            be = dict()
            be['name'] = button.name
            be['class'] = 'btn btn-%s' %button.cssclass
            be['title'] = button.title
            be['url'] = button.absolute_url()
            buttonlist.append(be)
        return buttonlist
