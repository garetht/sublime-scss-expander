import sublime, sublime_plugin

class SassexpanderCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    self.selectors = []

    curpos = self.view.sel()[0].begin()
    self.state_machine(curpos)

  def state_machine(self, cursorpos):
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
          bracket_counter -= 1
        elif char == '}':
          bracket_counter += 1
      startpos -= 1

    if bracket_counter < 0 and not comment_state:
      self.gather_selector(startpos)

    return startpos

  def lookahead(self, pos):
    return self.view.substr(pos - 1)

  def gather_selector(self, openposition):
    selector = ''
    selectorposition = openposition - 1
    char = self.view.substr(selectorposition)

    while char != ';' and char != '}' and char != '{' and char != '/' and selectorposition >= 0:
      selector += char
      selectorposition -= 1
      char = self.view.substr(selectorposition)

    self.selectors.append(selector[::-1])
    print self.selectors
