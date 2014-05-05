import scss_expand

class StringSCSSExpand(scss_expand.SCSSExpand):
  def __init__(self, startpos, text):
    self.text = text
    get_char_fn = lambda index : self.text[index]
    scss_expand.SCSSExpand.__init__(self, startpos, get_char_fn)
