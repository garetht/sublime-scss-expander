import sublime, sublime_plugin
import re, sys, os

if sys.version < '3':
  from src.src_two.scss_expand import SCSSExpand
else:
  from .src.src_three.scss_expand import SCSSExpand

class ScssexpanderCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    curpos = self.view.sel()[0].begin()
    expander = SCSSExpand(curpos, self.view.substr, '\n')
    status = expander.coalesce_rule()
    sublime.message_dialog(status)
