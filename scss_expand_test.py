import unittest
import string_scss_expand

class TestScssExpand(unittest.TestCase):

  def test_one_rule(self):
    """Can handle one unnested rule."""
    string = ".hello{margin: 0}"
    sse = string_scss_expand.StringSCSSExpand(10, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".hello"

    self.assertEqual(actual_rule, expected_rule)

  def test_two_rules(self):
    """Can handle two unnested rules separated by a comma."""
    string = ".baz,.bang{padding:0}"
    sse = string_scss_expand.StringSCSSExpand(14, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".baz, .bang"

    self.assertEqual(actual_rule, expected_rule)

  def test_complex_rules(self):
    """Can handle unnested rules that are complex."""
    string = """
body#hello-world.program.rule:before {
  text-align: left;
}
    """
    sse = string_scss_expand.StringSCSSExpand(42, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = "body#hello-world.program.rule:before"

    self.assertEqual(actual_rule, expected_rule)

  def test_sibling_rules(self):
    """Does not include prior sibling rules as parents."""
    string = """
.sibling-rule {
  height: 20px;
  position: absolute;
  font-weight: 700;
}

.actual-rule {
  border: 0;
}
"""
    sse = string_scss_expand.StringSCSSExpand(99, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".actual-rule"

    self.assertEqual(actual_rule, expected_rule)

  def test_nested_rules(self):
    """Can handle a rule that is nested within another."""
    string = """
.foo {
  .bar {
    outline: none;
  }
}
    """
    sse = string_scss_expand.StringSCSSExpand(37, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .bar"

    self.assertEqual(actual_rule, expected_rule)

  def test_single_line_nested_rules(self):
    """Can handle a rule that is nested within another on a single line."""
    string = ".baz{.bang{.three{.four#end{z-index: 2}}}}"
    sse = string_scss_expand.StringSCSSExpand(35, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".baz .bang .three .four#end"

    self.assertEqual(actual_rule, expected_rule)

  def test_other_combinator_nested_rules(self):
    """Can handle a rule that is nested within another on a single line using other combinators."""
    string = ".baz{ + .bang{.three{> .four#end{z-index: 2}}}}"
    sse = string_scss_expand.StringSCSSExpand(35, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".baz + .bang .three > .four#end"

    self.assertEqual(actual_rule, expected_rule)

  def test_top_comma_nested_rules(self):
    """Can handle a nested rule with two top-level rules."""
    string = """
.foo, .bar {
  .baz-width {
    outline: none;
  }
}
    """
    sse = string_scss_expand.StringSCSSExpand(37, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .baz-width, .bar .baz-width"

    self.assertEqual(actual_rule, expected_rule)

  def test_double_comma_nested_rules(self):
    """Can handle two layers of nested rules."""
    string = """
.foo, .bar {
  .baz, .bang {
    outline: none;
  }
}
    """
    sse = string_scss_expand.StringSCSSExpand(37, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .baz, .foo .bang, .bar .baz, .bar .bang"

    self.assertEqual(actual_rule, expected_rule)

  def test_parent_selector(self):
    """Replaces the parent selector correctly in simple cases"""
    string = """
.some-rule-here {
  .other-rule-there {
    .ie8 & {
      position: absolute;
    }
  }
}
    """
    sse = string_scss_expand.StringSCSSExpand(63, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".ie8 .some-rule-here .other-rule-there"

  def test_complex_parent_selector(self):
    """Replaces the parent selector correctly when it is adjoined to a rule."""
    string = """
.some-rule-here {
  .other-rule-there {
    .ie8 &:hover {
      position: absolute;
    }
  }
}
    """
    sse = string_scss_expand.StringSCSSExpand(63, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".ie8 .some-rule-here .other-rule-there:hover"

    self.assertEqual(actual_rule, expected_rule)

  def test_suffixed_parent_selector(self):
    """Replaces the parent selector correctly when it is a suffix of a rule."""
    string = """
.foo {
  &bar{
    e: f;
  }
}
    """
    sse = string_scss_expand.StringSCSSExpand(21, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foobar"

    self.assertEqual(actual_rule, expected_rule)

  def test_multiple_parent_selector(self):
    """Replaces the parent selector correctly when it has two comma-separated rules as parents."""
    string = """
.first-rule, .second-rule {
  &:hover {
    font-weight: 500;
  }
}
    """
    sse = string_scss_expand.StringSCSSExpand(49, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".first-rule:hover, .second-rule:hover"

    self.assertEqual(actual_rule, expected_rule)

  def test_multiple_nested_multiple_parent_selector(self):
    """Replaces the parent selector correctly when it is multiply nested with multiple comma-separated rules."""
    string = """
.foo, .bar {
  .bang, .bim {
    &.baz {
      outline: 0;
    }
  }
}
    """
    sse = string_scss_expand.StringSCSSExpand(49, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .bang.baz, .foo .bim.baz, .bar .bang.baz, .bar .bim.baz"

    self.assertEqual(actual_rule, expected_rule)

  def test_handle_block_comment(self):
    """Does not include rules in commented blocks."""
    string = """
.foo, .bar {
  /*
    .comment-rule {
   */
      .baz, .bang {
        outline: none;
      }
  /*
    }
   */
}
    """
    sse = string_scss_expand.StringSCSSExpand(82, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .baz, .foo .bang, .bar .baz, .bar .bang"

  def test_handle_block_comment(self):
    """Does not get thrown off by unbalanced brackets in commented blocks."""
    string = """
.foo, .bar {
  /*
    .comment-rule {}}{}{{{{{{{{}}}
   */
      .baz, .bang {
        outline: none;
      }
  /*
    }
   */
}
    """
    sse = string_scss_expand.StringSCSSExpand(82, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .baz, .foo .bang, .bar .baz, .bar .bang"

    self.assertEqual(actual_rule, expected_rule)

  def test_handle_single_line_comment(self):
    """Does not include rules in single-line comments"""
    string = """
.foo, .bar {

  //.comment-rule {
      .baz, .bang {
        outline: none;
      }
  // }
}
    """
    sse = string_scss_expand.StringSCSSExpand(82, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .baz, .foo .bang, .bar .baz, .bar .bang"

    self.assertEqual(actual_rule, expected_rule)

  def test_handle_complex_single_line_comment(self):
    """Does not include rules in single-line comments"""
    string = """
.foo {// bar: baz;}
  baz: bang; //}
}
    """
    sse = string_scss_expand.StringSCSSExpand(27, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo"

    self.assertEqual(actual_rule, expected_rule)

  def test_handle_single_line_comment_left_unbalanced_brackets(self):
    """Does not get thrown off by left unbalanced brackets in single-line comments."""
    string = """
.foo, .bar {

  //.comment-rule {{{{{}
      .baz, .bang {
        outline: none;
      }
  // }
}
    """
    sse = string_scss_expand.StringSCSSExpand(82, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .baz, .foo .bang, .bar .baz, .bar .bang"

    self.assertEqual(actual_rule, expected_rule)

  def test_handle_single_line_comment_right_unbalanced_brackets(self):
    """Does not get thrown off by right unbalanced brackets in single-line comments."""
    string = """
.foo {

  //.comment-rule }}}}}}
      .baz {
        outline: none;
      }
  // }
}
    """
    sse = string_scss_expand.StringSCSSExpand(63, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .baz"

    self.assertEqual(actual_rule, expected_rule)



