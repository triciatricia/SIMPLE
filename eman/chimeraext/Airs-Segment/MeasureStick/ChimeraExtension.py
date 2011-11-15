import chimera.extension

# -------------------------------------------------------------------------

class MeasureStickEMO(chimera.extension.EMO):
    """Dock manually using mouse.
    """

    def name(self):
        return 'Measure Stick'
    def description(self):
        return 'A measuring stick'
    def categories(self):
        return ['AIRS']
    def icon(self):
        return self.path('measurestick.gif')
    def activate(self):
        self.module('').show_simple_distance_dialog()
        return None

# -------------------------------------------------------------------------

chimera.extension.manager.registerExtension(MeasureStickEMO(__file__))

# -------------------------------------------------------------------------

