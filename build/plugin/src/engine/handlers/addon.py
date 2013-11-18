from item import ItemHandler
from content import ContentHandler
from folder import FolderItemHandler
from media import VideoItemHandler
from context import ContextMenuItemHandler

from Plugins.Extensions.archivCZSK import _
from Plugins.Extensions.archivCZSK.engine.contentprovider import VideoAddonContentProvider
from Plugins.Extensions.archivCZSK.engine.items import PExit, PVideoAddon
from Plugins.Extensions.archivCZSK.gui.exception import AddonExceptionHandler


class VideoAddonItemHandler(ItemHandler):
    handles = (PVideoAddon, )
        
    def open_item(self, item, *args, **kwargs):
        self.item = item
        def open_item_success_cb(result):
                list_items, command, args = result
                list_items.insert(0, PExit())
                self.content_screen.resolveCommand(command, args)
                self.content_screen.stopLoading()
                self.open_video_addon(item.addon, list_items)
            
        @AddonExceptionHandler(self.session)  
        def open_item_error_cb(failure):
                self.open_video_addon_cb(item.addon.provider)
                self.content_screen.stopLoading()
                self.content_screen.workingFinished()
                failure.raiseException()
                
        @AddonExceptionHandler(self.session)
        def get_content(addon):
                try:
                    content_provider = addon.provider
                    content_provider.start()
                    content_provider.get_content(self.session, {}, open_item_success_cb, open_item_error_cb)
                except Exception:
                    content_provider.stop()
                    self.content_screen.stopLoading()
                    self.content_screen.workingFinished()
                    raise
                
        self.content_screen.workingStarted()
        self.content_screen.startLoading()
        get_content(item.addon)
            
    def open_video_addon(self, addon, list_items):
        from Plugins.Extensions.archivCZSK.gui.content import ContentScreen
        self.session.openWithCallback(self.open_video_addon_cb, ContentScreen, addon, list_items)
        
    def open_video_addon_cb(self, content_provider):
        if isinstance(content_provider, VideoAddonContentProvider):
            content_provider.stop()
        self.content_screen.workingFinished()
        
    def resolve_command(self):
        pass
    
    def _init_menu(self, item):
        addon = item.addon
        #item.add_context_menu_item(_("Update"), action=item.addon.update)
        item.add_context_menu_item(_("Settings"),
                                   action=addon.open_settings,
                                   params={'session':self.session})
        item.add_context_menu_item(_("Changelog"),
                                   action=addon.open_changelog,
                                   params={'session':self.session})
        item.add_context_menu_item(_("Downloads"),
                                   action=addon.open_downloads,
                                   params={'session':self.session,
                                           'cb':self.content_screen.workingFinished})
        item.add_context_menu_item(_("Shortcuts"),
                                   action=addon.open_shortcuts,
                                   params={'session':self.session,
                                           'cb':self.content_screen.workingFinished})
        

class VideoAddonContentHandler(ContentHandler):
    
    def __init__(self, session, content_screen, content_provider):
        handlers = []
        handlers.append(FolderItemHandler(session, content_screen, content_provider))
        handlers.append(VideoItemHandler(session, content_screen, content_provider))
        handlers.append(ContextMenuItemHandler(session, content_screen, content_provider))
        ContentHandler.__init__(self, session, content_screen, content_provider, handlers)
            
    def exit_item(self):
        parent_content = self.content_screen.popParent()
        if parent_content is not None:
            self.content_screen.load(parent_content)
        else:
            self.content_provider.save_shortcuts()
            self.content_screen.close(self.content_provider)
            
    def close_screen(self):
        self.content_provider.save_shortcuts()
        self.content_screen_close()