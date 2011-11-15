import chimera.extension

class Volume_Path_EMO(chimera.extension.EMO):
  def name(self):
    return 'Measuring Stick'
  def description(self):
    return 'Trace path in volume data.'
  def categories(self):
    return ['EMAN']
  def icon(self):
    return self.path('volumepath.gif')
  def activate(self):
    self.module().show_volume_path_dialog()
    return None

# -----------------------------------------------------------------------------
#
def open_marker_set(path):
  
  import VolumePath
  d = VolumePath.show_volume_path_dialog()
  d.open_marker_set(path)
  models = []
  return models

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Volume_Path_EMO(__file__))
chimera.fileInfo.register('Chimera markers', open_marker_set,
                          ['.cmm'], ['markers'])
