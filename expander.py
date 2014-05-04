import sublime, sublime_plugin
import re

class SassexpanderCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    self.selectors = []

    curpos = self.view.sel()[0].begin()
    self.selector_machine(curpos)
    selector_array = map(self.process_selector, self.selectors)[::-1]
    self.generate_expanded(selector_array)
    print self.selectors

  def selector_machine(self, cursorpos):
    position = self.push_next_selector(cursorpos)
    while position >= 0:
      position = self.push_next_selector(position)

  def push_next_selector(self, startpos):
    bracket_counter = 0
    comment_state = False

    while bracket_counter > -1 and startpos >= 0:
      char = self.view.substr(startpos)

      if comment_state:
        if char == '*' and self.lookahead(startpos) == '/':
          comment_state = False
      else:
        if char == '/' and self.lookahead(startpos) == '*':
          comment_state = True
        elif char == '{':
          is_comment, startpos = self.check_comment(startpos)
          if not is_comment:
            bracket_counter -= 1
        elif char == '}':
          is_comment, startpos = self.check_comment(startpos)
          if not is_comment:
            bracket_counter += 1
      startpos -= 1

    # handle the case of interpolation
    if (bracket_counter < 0 and self.view.substr(startpos) != '#') and not comment_state:
      self.gather_selector(startpos)

    return startpos

  def lookahead(self, pos):
    return self.view.substr(pos - 1)

  def gather_selector(self, openposition):
    selector = ''
    selectorposition = openposition - 1
    char = self.view.substr(selectorposition)

    while char != ';' and char != '{' and char != '\n' and (char != '/' and self.lookahead(selectorposition) != '*') and selectorposition >= 0:

      if char == '}':
        stringbuffer = '}'
        selectorposition -= 1

        while char != '{' and selectorposition >= 0:
          char = self.view.substr(selectorposition)
          stringbuffer += char
          selectorposition -= 1

        if char == '{' and self.view.substr(selectorposition) == '#':
          selector += stringbuffer
          char = self.view.substr(selectorposition)
        else:
          break

      selector += char
      selectorposition -= 1
      char = self.view.substr(selectorposition)

    if len(selector) > 0:
      selector = self.strip_whitespace(selector)
      self.selectors.append(selector[::-1])

  # Returns whether the line is a comment and
  # the number of the first character of the comment ('/')
  # [True, 32]
  # If it is not a commented line, return the same selectorpos
  def check_comment(self, selectorposition):
    savedpos = selectorposition
    char = self.view.substr(selectorposition)

    while char != '\n' and selectorposition >= 0:
      if char == '/' and self.lookahead(selectorposition) == '/':
        return [True, selectorposition - 1]
      selectorposition -= 1
      char = self.view.substr(selectorposition)

    return [False, savedpos]

  def parse_at_root(self, selector):
    pass

  def process_selector(self, selector):
    return selector.split(',')

  # selector array goes forward
  # TODO: deal with case of directive
  def generate_expanded(self, selector_array):

    def comma_reducer(array, following_array):
      results = []
      for selector in array:
        for sel in following_array:
          results.append(selector + ' ' + sel)
      return results

    self.selectors = reduce(comma_reducer, selector_array)

  def strip_whitespace(self, selector):
    return re.sub(r'(^\s+|\s+$)', '', selector)
