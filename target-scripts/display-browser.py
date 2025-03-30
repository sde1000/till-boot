#!/usr/bin/env python3

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('WebKit', '6.0')
from gi.repository import Gtk, WebKit, GLib, GObject


if __name__ == "__main__":
    window = Gtk.Window(title="Display browser")
    window.set_default_size(800, 600)
    web = WebKit.WebView.new()
    web.set_size_request(0, 1)
    web.set_vexpand(True)
    window.set_child(web)
    web.bind_property('title', window, 'title', GObject.BindingFlags.DEFAULT)

    window.present()
    window.fullscreen()
    web.load_uri(sys.argv[1])

    # Hide the cursor, always
    window.set_cursor_from_name("none")

    while (len(Gtk.Window.get_toplevels()) > 0):
        GLib.MainContext.default().iteration(True)
