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
from gi.repository import Gtk

class MainWindow(Gtk.ApplicationWindow):
    """The main window of the app."""

    def __init__(self, app):
        try:
            super().__init__(application=app, title="BOTWTools")
            self.app = app

            self._box = Gtk.Box(orientation='vertical')
            self.add(self._box)
        except:
            log.exception("Failed creating main window!")
            sys.exit(1) # avoid hang
