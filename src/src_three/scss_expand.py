import re

class SCSSExpand():
  def __init__(self, startpos, get_char_fn, separator = ' '):
    self.selectors = []
    self.comment_blocks = [] #array of tuples /*123*/ - will give (0, 6) - inclusive!
    self.separator = separator
    self.get_char_fn = get_char_fn
    self.startpos = startpos

  def coalesce_rule(self):
    self.comment_machine(self.startpos)
    if self.check_block_comment(self.startpos):
      self.startpos = self.skip_comment(self.startpos)
    self.selector_machine(self.startpos)
    self.process_at_root()

    selector_array = filter(lambda x : not re.search('@(for|each|while|if|else)', x), self.selectors)
    selector_array = map(self.process_selector, selector_array)

    ### Past this point are mostly differences in formatting
    # If loop directive information must be retained,
    # modify the filter above
    self.generate_expanded(selector_array)
    return self.strip_whitespace((',' + self.separator).join(self.selectors))

  # We read forwards for comment blocks
  def comment_machine(self, endpos):
    startpos = 0
    endpos -= 1
    commentstart = None
    commentend = None
    while startpos <= endpos:
      char = self.get_char_fn(startpos)

      # Single line comments
      if char == '/' and self.forward_lookahead(startpos) == '/':
        commentstart = startpos
        while char != '\n':
          if startpos == endpos + 1:
            self.comment_blocks.append((commentstart, endpos))
            return
          startpos += 1
          char = self.get_char_fn(startpos)
        commentend = startpos
        self.comment_blocks.append((commentstart, commentend))

      # Block comments
      elif char == '/' and self.forward_lookahead(startpos) == '*':
        commentstart = startpos
        startpos += 2 # move past the opening block so that /*/ is still commented
        char = self.get_char_fn(startpos)
        while char != '*' or self.forward_lookahead(startpos) != '/':
          if startpos == endpos:
            self.comment_blocks.append((commentstart, endpos + 1))
            return
          startpos += 1
          char = self.get_char_fn(startpos)

        startpos += 1
        commentend = startpos
        self.comment_blocks.append((commentstart, commentend))

      startpos += 1

  def skip_comment(self, pos):
    for commentstart, commentend in self.comment_blocks:
      if pos == commentend:
        return commentstart - 1
    return pos

  def selector_machine(self, cursorpos):
    position = self.push_next_selector(cursorpos)
    while position >= 0:
      position = self.push_next_selector(position)
    self.selectors = self.selectors[::-1]

  def push_next_selector(self, startpos):
    bracket_counter = 0

    while bracket_counter > -1 and startpos >= 0:
      char = self.get_char_fn(startpos)
      if char == '/' and self.lookahead(startpos) == '*':
        startpos = self.skip_comment(startpos)
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
    if (bracket_counter < 0 and self.get_char_fn(startpos) != '#'):
      self.gather_selector(startpos)

    return startpos

  def forward_lookahead(self, pos):
    return self.get_char_fn(pos + 1)

  def lookahead(self, pos):
    return self.get_char_fn(pos - 1)

  def gather_selector(self, openposition):
    selector = ''
    selectorposition = openposition
    char = self.get_char_fn(selectorposition)

    while char != ';' and char != '{' and selectorposition >= 0:
      if char == '\n' or (char == '/' and self.lookahead(selectorposition) == '*'):
        selectorposition = self.skip_comment(selectorposition)
        char = self.get_char_fn(selectorposition)

      if char == '}':
        stringbuffer = '}'
        selectorposition -= 1

        while char != '{' and selectorposition >= 0:
          char = self.get_char_fn(selectorposition)
          stringbuffer += char
          selectorposition -= 1

        if char == '{' and self.get_char_fn(selectorposition) == '#':
          selector += stringbuffer
          char = self.get_char_fn(selectorposition)
        else:
          break

      selector += char
      selectorposition -= 1
      char = self.get_char_fn(selectorposition)

    if len(selector) > 0:
      selector = self.strip_whitespace(selector)
      self.selectors.append(selector[::-1])

  # Returns whether the line is a comment and
  # the number of the first character of the comment ('/')
  # [True, 32]
  # If it is not a commented line, return the same selectorpos
  def check_comment(self, selectorposition):
    return [self.check_block_comment(selectorposition), self.skip_comment(selectorposition)]

  # Returns False if the startpos is not in a block comment,
  # returns True if it is
  def check_block_comment(self, selectorposition):
    for commentstart, commentend in self.comment_blocks:
      if selectorposition >= commentstart and selectorposition <= commentend:
        return True
    return False

  def process_at_root(self):
    selectors = self.selectors
    # Group 1: with/without
    # Group 2: space-separated list of with/without directives
    AT_ROOT_RE = re.compile(r'@at-root\s*(?:\((with|without)\s*:\s*((?:\w+\s?)+)\))?\s*')
    at_root_index = None
    at_root = dict() # only the final at-root is important
    for index, selector in enumerate(selectors):
      at_root_match = re.search(AT_ROOT_RE, selector)
      if at_root_match:
        at_root_index = index
        at_root['exclusion'] = at_root_match.group(1)
        if at_root_match.group(2):
          at_root['directives'] = at_root_match.group(2).split(' ')
        else:
          at_root['directives'] = []

    if not at_root_index:
      return

    directive_re = re.compile('@(' + '|'.join(at_root['directives']) +')')

    # @at-root has two special values, 'all' and 'rule'
    if at_root['exclusion'] == 'without' and 'all' in at_root['directives']:
      selectors[at_root_index] = re.sub(AT_ROOT_RE, '', selectors[at_root_index])
      self.selectors = selectors[at_root_index:] #discard everything
      return
    elif at_root['exclusion'] == 'with' and 'rule' in at_root['directives']:
      # keep listed directives and all rules
      filter_func = lambda x: re.match(directive_re, x) or not re.match('@', x)
    elif at_root['exclusion'] == 'with':
      # keep only listed directives
      filter_func = lambda x: re.match(directive_re, x)
    elif at_root['exclusion'] == None:
      # just keep directives
      filter_func = lambda x: re.match('@', x)
    elif at_root['exclusion'] == 'without':
      # keep directives but not those listed. without rule is in this case
      filter_func = lambda x: re.match('@', x) and not re.match(directive_re, x)

    allowed_directives = filter(filter_func, selectors[:at_root_index])
    selectors[at_root_index] = re.sub(AT_ROOT_RE, '', selectors[at_root_index])
    self.selectors = allowed_directives + selectors[at_root_index:]

  def process_selector(self, selector):
    split = []
    if '@' in selector:
      split = [selector]
    else:
      split = selector.split(',')
    return split

  # selector array goes forward
  # generate_expanded takes an array of arrays and joins them together
  # e.g. [['.hello', '.there'], ['.one', '.two']]
  # gives ['.hello .one', '.hello .two', '.there .one', '.there .two']
  def generate_expanded(self, selector_array):

    def comma_reducer(array, following_array):
      results = []
      for selector in array:
        for sel in following_array:
          stripped_selector = self.strip_whitespace(selector)
          if '&' in sel:
            results.append(sel.replace('&', stripped_selector))
          else:
            results.append(stripped_selector + self.separator + self.strip_whitespace(sel))
      return results

    self.selectors = reduce(comma_reducer, selector_array)

  def strip_whitespace(self, selector):
    return selector.strip()
