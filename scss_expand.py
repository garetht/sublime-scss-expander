import re

class SCSSExpand():
  def __init__(self, startpos, get_char_fn):
    self.selectors = []
    self.get_char_fn = get_char_fn
    self.startpos = startpos

  def coalesce_rule(self):
    self.selector_machine(self.startpos)
    self.process_at_root()

    selector_array = filter(lambda x : not re.search('@(for|each|while|if)', x), self.selectors)
    selector_array = map(self.process_selector, selector_array)

    ### Past this point are mostly differences in formatting
    # If loop directive information must be retained,
    # modify the filter above
    self.generate_expanded(selector_array)
    return self.strip_whitespace(', '.join(self.selectors))

  def selector_machine(self, cursorpos):
    position = self.push_next_selector(cursorpos)
    while position >= 0:
      position = self.push_next_selector(position)
    self.selectors = self.selectors[::-1]

  def push_next_selector(self, startpos):
    bracket_counter = 0
    comment_state = False

    while bracket_counter > -1 and startpos >= 0:
      char = self.get_char_fn(startpos)

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
    if (bracket_counter < 0 and self.get_char_fn(startpos) != '#') and not comment_state:
      self.gather_selector(startpos)

    return startpos

  def lookahead(self, pos):
    return self.get_char_fn(pos - 1)

  def gather_selector(self, openposition):
    selector = ''
    selectorposition = openposition
    char = self.get_char_fn(selectorposition)

    while char != ';' and char != '{' and char != '\n' and (char != '/' and self.lookahead(selectorposition) != '*') and selectorposition >= 0:

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
    savedpos = selectorposition
    char = self.get_char_fn(selectorposition)

    while char != '\n' and selectorposition >= 0:
      if char == '/' and self.lookahead(selectorposition) == '/':
        return [True, selectorposition - 1]
      selectorposition -= 1
      char = self.get_char_fn(selectorposition)

    return [False, savedpos]

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
      filter_func = lambda x: re.match(directive_re, x) or not re.match('@', x) #keep listed directives and all rules
    elif at_root['exclusion'] == 'with':
      filter_func = lambda x: re.match(directive_re, x) #keep only listed directives
    elif at_root['exclusion'] == None or at_root['exclusion'] == 'without' and 'rule' in at_root['directives']:
      filter_func = lambda x: re.match('@', x) #just keep directives
    elif at_root['exclusion'] == 'without':
      filter_func = lambda x: re.match('@', x) and not re.match(directive_re, x) #keep directives but not those listed

    allowed_directives = filter(filter_func, selectors[:at_root_index])
    selectors[at_root_index] = re.sub(AT_ROOT_RE, '', selectors[at_root_index])
    self.selectors = allowed_directives + selectors[at_root_index:]

  def process_selector(self, selector):
    split = []
    if re.search('@', selector):
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
          if re.search('&', sel):
            results.append(sel.replace('&', selector))
          else:
            results.append(selector + ' ' + sel)
      return results

    self.selectors = reduce(comma_reducer, selector_array)

  def strip_whitespace(self, selector):
    return re.sub(r'(^\s+|\s+$)', '', selector)
