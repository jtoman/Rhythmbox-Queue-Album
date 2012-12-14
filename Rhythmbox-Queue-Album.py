'''
Plugin for Rhythmbox that random plays songs sorted by album, track-number randomly
Copyright (C) 2012  John Toman <jtoman@umd.edu>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''
from gi.repository import GObject
from gi.repository import Peas
from gi.repository import RB
from gi.repository import Gtk

queue_album_menu_item = '''
  <ui>
    <menubar name="MenuBar">
      <menu name="ControlMenu" action="Control">
        <menuitem name="QueueAlbumItem" action="QueueAlbum"/>
      </menu>
    </menubar>
  </ui>
'''

# A lot of the boilerplate (especially the setup/tear down code) in
# this class is adapted from Javon Harper's Random Album Plugin
# (https://github.com/javonharper/Rhythmbox-Random-Album-Player). Many
# thanks to him for figuring out the messy details.
class QueueAlbumPlugin(GObject.Object, Peas.Activatable):
  __gtype_name__ = 'QueueAlbumPlugin'
  object = GObject.property(type=GObject.Object)

  def __init__(self):
    super(QueueAlbumPlugin, self).__init__()
    self.album_type = RB.RhythmDBPropType.ALBUM
    self.disc_number_type = RB.RhythmDBPropType.DISC_NUMBER
    self.track_number_type = RB.RhythmDBPropType.TRACK_NUMBER

  def do_activate(self):
    shell = self.object
    action = Gtk.Action ('QueueAlbum', _('Queue Album'), _('Add the selected album to your play queue'), "")
    action.connect ('activate', self.queue_album, shell)
    action_group = Gtk.ActionGroup('QueueAlbumActionGroup')
    action_group.add_action_with_accel (action, "<alt>Q")
    
    ui_manager = shell.props.ui_manager
    ui_manager.insert_action_group(action_group)
    self.ui_id = ui_manager.add_ui_from_string(queue_album_menu_item)

  def do_deactivate(self):
    shell = self.object
    ui_manager = shell.props.ui_manager
    ui_manager.remove_ui(self.ui_id)
    
  def queue_album(self, event, shell):    
    if shell.props.selected_page is not shell.props.library_source:
      return
    entry_manager = shell.props.library_source.get_entry_view()
    selected_entries = entry_manager.get_selected_entries()
    # we don't deal with multiple selections for the moment.
    # easy enough to add later if there is demand
    if len(selected_entries) != 1:
      return
    (selected_entry,) = selected_entries
    selected_album = selected_entry.get_string(self.album_type)
    entries_in_album = []
    for row in shell.props.library_source.props.query_model:
      entry = row[0]
      if entry.get_string(self.album_type) != selected_album:
        continue
      entries_in_album.append(entry)
      sorted_album_songs = sorted(entries_in_album, cmp=self.sort_entries)
    for song in sorted_album_songs:
        shell.props.queue_source.add_entry(song, -1)
  def sort_entries(self, a, b):
    a_disc = a.get_ulong(self.disc_number_type)
    b_disc = b.get_ulong(self.disc_number_type)
    disc_cmp = int(a_disc) - int(b_disc)
    if disc_cmp != 0:
      return disc_cmp
    return int(a.get_ulong(self.track_number_type)) - int(b.get_ulong(self.track_number_type))
