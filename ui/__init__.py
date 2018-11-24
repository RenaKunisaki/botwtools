# This file is part of botwtools.
#
# botwtools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# botwtools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with botwtools.  If not, see <https://www.gnu.org/licenses/>.

import logging; log = logging.getLogger(__name__)
import gi
gi.require_version('GObject', '2.0'); from gi.repository import GObject
gi.require_version('Gtk', '3.0'); from gi.repository import Gtk
gi.require_version('Gio', '2.0'); from gi.repository import Gio
from .mainwindow import MainWindow
import time


class UI(Gtk.Application):
    """The app UI."""
    application_id = "net.segment6.botwtools.dbus.sucks%d" % time.time()

    def __init__(self):
        Gtk.Application.__init__(self,
            application_id = self.application_id,
            flags = Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.mainWindow = None

    def do_startup(self):
        """Implement `startup` action, called when app is starting."""
        # app is starting. `activate` or `open` comes next.
        Gtk.Application.do_startup(self)
        #self.project = Project.new() # create new temp file

    def do_shutdown(self):
        """Implement `shutdown` action, called when app is terminating."""
        Gtk.Application.do_shutdown(self)

    def do_activate(self):
        """Implement `activate` action, called when app is
        asked to show its UI. (Usually immediately after launch.)
        """
        self.mainWindow = MainWindow(self)
        self.mainWindow.show_all()
