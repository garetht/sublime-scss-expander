from .scss_expand import SCSSExpand

class StringSCSSExpand(SCSSExpand):
  def __init__(self, startpos, text):
    self.text = text
    get_char_fn = lambda index : self.text[index]
    SCSSExpand.__init__(self, startpos, get_char_fn)
