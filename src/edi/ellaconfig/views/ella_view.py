# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
# from edi.ellaconfig.views.examples import uischema
from plone.i18n.normalizer import idnormalizer
from plone import api as ploneapi
import json
from jinja2 import Template


class EllaView(BrowserView):

    def formatcontent(self, obj):
        article = dict()
        article['id'] = obj.getId()
        article['title'] = obj.title
        article['description'] = obj.description
        article['text'] = u''
        if hasattr(obj, 'text'):
            if obj.text:
                article['text'] = obj.text.output
        article['img'] = u''
        if hasattr(obj, 'image'):
            if obj.image:
                article['img'] = '%s/@@download/image' % obj.absolute_url()
        return article

    def get_content(self):
        content = []
        if self.context.portal_type == 'Folder':
            fc = self.context.listFolderContents(contentFilter={"portal_type": "Document"})
            for obj in fc:
                content.append(self.formatcontent(obj))
        else:
            content.append(self.formatcontent(self.context))
        return content

    ##############################################################################################

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
        ellaservice['form'] = json_schema_view.__call__(localmarker=True, idtyp='id')
        ui_schema_view = ploneapi.content.get_view(name='ui-schema-view', context=form, request=self.request)
        ellaservice['ui'] = ui_schema_view.__call__(localmarker=True)
        buttons = service.listFolderContents(contentFilter={"portal_type": "Servicebutton"})
        ellaservice['formactions'] = self.create_servicebuttons(buttons)
        return ellaservice

    def create_group_service(self, service):
        servicelist = list()
        subservices = service.listFolderContents(contentFilter={"portal_type": "Service"})
        for subservice in subservices:
            typ = subservice.servicetyp
            if typ == 'service':
                servicelist.append(self.create_single_service(subservice))
            elif typ in ['audio', 'video']:
                servicelist.append(self.create_media_service(subservice, typ))
            else:
                servicelist.append(self.create_page_service(subservice))
        ellaservice = dict()
        ellaservice['name'] = service.getId()
        ellaservice['title'] = service.title
        ellaservice['description'] = service.description
        ellaservice['type'] = service.servicetyp
        ellaservice['services'] = servicelist
        return ellaservice

    def create_media_service(self, service, mediatype):
        mediaservice = dict()
        mediacontainer = service.serviceref.to_object
        mediafiles = self.create_mediafiles(mediacontainer.getFolderContents(), mediatype)
        mediaservice['name'] = mediacontainer.id
        mediaservice['title'] = mediacontainer.title
        mediaservice['description'] = mediacontainer.description
        mediaservice['type'] = mediatype
        mediaservice['textbefore'] = ''
        mediaservice['textafter'] = ''
        if mediacontainer.text:
            if mediacontainer.text.output:
                mediaservice['textbefore'] = mediacontainer.text.output
        if mediacontainer.schlusstext:
            if mediacontainer.schlusstext.output:
                mediaservice['textafter'] = mediacontainer.schlusstext.output
        mediaservice['mediafiles'] = mediafiles
        return mediaservice

    def create_mediafiles(self, brains, mediatype):
        mediafiles = []
        for mediabrain in brains:
            mediadict = dict()
            mediafile = mediabrain.getObject()
            mediadict['name'] = mediafile.id
            mediadict['title'] = mediafile.title
            mediadict['description'] = mediafile.description
            if mediatype == 'audio':
                mediadict['url'] = f'{mediafile.absolute_url()}/@@download/audio/{mediafile.audio.filename}'
                mediadict['mimetype'] = 'audio/mpeg'
            elif mediatype == 'video':
                mediadict['url'] = f'{mediafile.absolute_url()}/@@download/video/{mediafile.video.filename}'
                mediadict['mimetype'] = 'video/mp4'
            mediadict['imageurl'] = ''
            mediadict['imagecaption'] = ''
            mediadict['transcript'] = ''
            if mediafile.image:
                mediadict['imageurl'] = f'{mediafile.absolute_url()}/@@images/image/large'
            if mediafile.image_caption:
                mediadict['imagecaption'] = mediafile.image_caption
            if mediafile.transcript:
                mediadict['transcript'] = mediafile.transcript
            mediafiles.append(mediadict)
        return mediafiles

    def create_page_service(self, service):
        ellaservice = dict()
        ellaservice['name'] = service.getId()
        ellaservice['title'] = service.title
        ellaservice['description'] = service.description
        ellaservice['type'] = service.servicetyp
        pageobj = service.serviceref.to_object
        text = getattr(pageobj, 'text', u'')
        if text:
            text = text.output
        image = getattr(pageobj, 'image', u'')
        if image:
            image = '%s/@@download/image' % pageobj.absolute_url()
        ellaservice['text'] = self.format_ella_single(pageobj.title, text, image)
        return ellaservice

    def create_welcome_page(self, page, nav):
        service = dict()
        service['name'] = page.getId()
        service['title'] = page.title
        service['description'] = page.description
        service['type'] = 'page'
        text = getattr(page, 'text', u'')
        if text:
            text = text.output
        image = getattr(page, 'image', u'')
        if image:
            image = '%s/@@download/image' % page.absolute_url()
        service['text'] = self.format_ella_single(page.title, text, image) + nav
        return service

    def create_navigations(self, startseiten):
        naventries = []
        page = 1
        for i in startseiten:
            naventries.append(
                """<li class="page-item edi_active"><a class="page-link" href="#/services/%s">%s</a></li>""" % (
                i.getId(), str(page)))
            page += 1
        navs = []
        for i in range(len(startseiten)):
            navigation = """\
<nav aria-label="Navigation">
  <ul class="pagination justify-content-center">"""
            for k in range(len(naventries)):
                naventry = naventries[k]
                if i == k:
                    naventry = naventry.replace(u'edi_active', u'active')
                else:
                    naventry = naventry.replace(u'edi_active', u'')
                navigation += naventry
            navigation += """</ul></nav>"""
            navs.append(navigation)
        return navs

    def create_welcome_services(self):
        servicelist = list()
        startseiten = [obj.to_object for obj in self.context.startseiten]
        navigations = self.create_navigations(startseiten)
        for page, nav in zip(startseiten, navigations):
            servicelist.append(self.create_welcome_page(page, nav))
        groupnametitle = self.context.groupname.split('#')
        service = dict()
        service['name'] = groupnametitle[0]
        service['title'] = groupnametitle[1]
        service['description'] = self.context.description
        service['type'] = 'group'
        service['services'] = servicelist
        return service

    def get_ella_services(self):
        services = []
        for service in self.context.listFolderContents(contentFilter={"portal_type": "Service"}):
            typ = service.servicetyp
            if typ == 'service':
                services.append(self.create_single_service(service))
            elif typ == 'group':
                services.append(self.create_group_service(service))
            elif typ == 'page':
                services.append(self.create_page_service(service))
            elif typ in ['audio', 'video']:
                services.append(self.create_media_service(service, typ))
        if len(self.context.startseiten) > 1:
            services.append(self.create_welcome_services())
        return services

    def format_ella_single(self, title, text, image):
        tm = Template(self.context.bodytemplate)
        bodytext = tm.render(ella_title=title, ella_bodytext=text, ella_image=image)
        return bodytext

    def format_ella_startnavi(self, startseiten):
        startid = startseiten[0].to_object.getId()
        navigation = """\
<nav aria-label="Navigation">
  <ul class="pagination justify-content-center">
    <li class="page-item active"><a class="page-link" href="#/services/%s">1</a></li>""" % startid
        page = 2
        for i in startseiten[1:]:
            objid = i.to_object.getId()
            navigation += """<li class="page-item"><a class="page-link" href="#/services/%s">%s</a></li>""" % (
            objid, str(page))
            page += 1
        navigation += """</ul></nav>"""
        return navigation

    def get_ella_content(self):
        title = self.context.title
        if not self.context.startseiten:
            text = self.context.bodytext
            if text:
                text = text.output
            else:
                text = u''
            if self.context.image:
                image = '%s/@@download/image' % self.context.absolute_url()
            else:
                image = u''
            content = self.format_ella_single(title, text, image)
        else:
            obj = self.context.startseiten[0].to_object
            text = getattr(obj, 'text', u'')
            if text:
                text = text.output
            image = getattr(obj, 'image', u'')
            if image:
                image = '%s/@@download/image' % obj.absolute_url()
            content = self.format_ella_single(title, text, image)
            if len(self.context.startseiten) > 1:
                navi = self.format_ella_startnavi(self.context.startseiten)
                content += navi
        return content

    def __call__(self):
        if self.context.portal_type == "EllaKonfig":
            welcome = dict()
            welcome['name'] = self.context.getId()
            welcome['title'] = self.context.title
            welcome['description'] = self.context.description
            welcome['bodytext'] = self.get_ella_content()
            welcome['services'] = self.get_ella_services()
            content = welcome
        else:
            content = self.get_content()
        return json.dumps(content)
