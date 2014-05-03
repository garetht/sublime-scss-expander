class SCSSExpanderCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    print self.view.sel()
