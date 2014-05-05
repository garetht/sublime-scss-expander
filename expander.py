import sublime, sublime_plugin
import re

import scss_expand

class ScssexpanderCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    curpos = self.view.sel()[0].begin()
    expander = scss_expand.SCSSExpand(curpos, self.view.substr, '\n')
    status = expander.coalesce_rule()
    sublime.message_dialog(status)
