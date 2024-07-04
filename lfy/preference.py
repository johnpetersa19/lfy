'设置'

from gettext import gettext as _

from gi.repository import Adw, Gio, Gtk

from lfy.api import get_server_names_api_key, get_servers_api_key
from lfy.api.constant import SERVERS
from lfy.api.server import Server
from lfy.settings import Settings
from lfy.widgets.server_preferences import ServerPreferences


@Gtk.Template(resource_path='/cool/ldr/lfy/preference.ui')
class PreferenceWindow(Adw.PreferencesWindow):
    """设置

    Args:
        Adw (_type_): _description_
    """
    __gtype_name__ = 'PreferencesWindow'

    acr_server: Adw.ComboRow = Gtk.Template.Child()
    entry_vpn_addr: Adw.EntryRow = Gtk.Template.Child()
    auto_check_update: Gtk.Switch = Gtk.Template.Child()
    notify_translation_results: Gtk.Switch = Gtk.Template.Child()

    gbtn_compare: Gtk.MenuButton = Gtk.Template.Child()
    gl_compare: Gtk.Label = Gtk.Template.Child()
    gp_compare: Gtk.Popover = Gtk.Template.Child()
    glb_compare: Gtk.ListBox = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        sg = Settings.get()
        self.server: Server
        # pylint: disable=E1101
        self.acr_server.set_model(
            Gtk.StringList.new(get_server_names_api_key()))
        self.entry_vpn_addr.props.text = sg.vpn_addr_port

        sg.bind('auto-check-update', self.auto_check_update,
                'active', Gio.SettingsBindFlags.DEFAULT)

        sg.bind('notify-translation-results', self.notify_translation_results,
                'active', Gio.SettingsBindFlags.DEFAULT)
        self._init_pop_compare()

    def _init_pop_compare(self):
        """初始化compare弹出菜单
        """
        # pylint:disable=E1101
        # ui中无法设置gbtn_compare翻译
        self.gbtn_compare.set_label(_("compare"))
        names = []
        keys_s = Settings.get().compare_servers
        if len(keys_s) == 0:
            for se in SERVERS[1:]:
                keys_s.append(se.key)

        self.check_items = []
        for se in SERVERS[1:]:
            check_button = Gtk.CheckButton(label=se.name)
            if se.key in keys_s:
                check_button.set_active(True)
                names.append(se.name)
            self.check_items.append(check_button)
            self.glb_compare.append(Gtk.ListBoxRow(child=check_button))

        self.gl_compare.set_label(", ".join(names))

    @Gtk.Template.Callback()
    def _on_popover_closed(self, _popover):
        """关闭时保存

        Args:
            _popover (_type_): _description_
        """
        # pylint:disable=E1101
        keys = []
        names = []
        for i, check_button in enumerate(self.check_items):
            if check_button.get_active():
                keys.append(SERVERS[1:][i].key)
                names.append(SERVERS[1:][i].name)

        if Settings.get().compare_servers != keys:
            Settings.get().compare_servers = keys
            self.gl_compare.set_label(", ".join(names))
            self.get_root().add_toast(
                Adw.Toast.new(_("It takes effect when you restart lfy")))

    @Gtk.Template.Callback()
    def _open_server(self, _btn):
        page = ServerPreferences(self.server)
        self.present_subpage(page)

    @Gtk.Template.Callback()
    def _config_select_server(self, arc, _value):
        """Called on self.translator::notify::selected signal"""
        self.server = get_servers_api_key()[arc.get_selected()]

    @Gtk.Template.Callback()
    def _on_vpn_apply(self, _row):
        # pylint: disable=E1101
        self.entry_vpn_addr.props.sensitive = False

        vpn_addr = self.entry_vpn_addr.get_text().strip()
        self.entry_vpn_addr.props.text = vpn_addr
        Settings.get().vpn_addr_port = vpn_addr
        self.entry_vpn_addr.props.sensitive = True

        self.get_root().add_toast(
            Adw.Toast.new(_("It takes effect when you restart lfy")))
