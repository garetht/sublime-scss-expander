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
    string = ".one,.two{padding:0}"
    sse = string_scss_expand.StringSCSSExpand(14, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".one, .two"

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

  def test_nested_rules(self):
    """Can handle a rule that is nested within another."""
    string = """
.another {
  .one-width {
    outline: none;
  }
}
    """
    sse = string_scss_expand.StringSCSSExpand(37, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".another .one-width"

    self.assertEqual(actual_rule, expected_rule)

  def test_top_comma_nested_rules(self):
    """Can handle a nested rule with two top-level rules."""
    string = """
.another, .day {
  .one-width {
    outline: none;
  }
}
    """
    sse = string_scss_expand.StringSCSSExpand(37, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".another .one-width, .day .one-width"

    self.assertEqual(actual_rule, expected_rule)

  def test_double_comma_nested_rules(self):
    """Can handle two layers of nested rules."""
    string = """
.another, .day {
  .one, .two {
    outline: none;
  }
}
    """
    sse = string_scss_expand.StringSCSSExpand(37, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".another .one, .another .two, .day .one, .day .two"

    self.assertEqual(actual_rule, expected_rule)

  def test_handle_block_comment(self):
    """Does not include rules in commented blocks."""
    string = """
.another, .day {
  /*
    .comment-rule {
   */
      .one, .two {
        outline: none;
      }
  /*
    }
   */
}
    """
    sse = string_scss_expand.StringSCSSExpand(82, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".another .one, .another .two, .day .one, .day .two"

  def test_handle_block_comment(self):
    """Does not get thrown off by unbalanced brackets in commented blocks."""
    string = """
.another, .day {
  /*
    .comment-rule {}}{}{{{{{{{{}}}
   */
      .one, .two {
        outline: none;
      }
  /*
    }
   */
}
    """
    sse = string_scss_expand.StringSCSSExpand(82, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".another .one, .another .two, .day .one, .day .two"

    self.assertEqual(actual_rule, expected_rule)

  def test_handle_single_line_comment(self):
    """Does not include rules in single-line comments"""
    string = """
.another, .day {

  //.comment-rule {
      .one, .two {
        outline: none;
      }
  // }
}
    """
    sse = string_scss_expand.StringSCSSExpand(82, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".another .one, .another .two, .day .one, .day .two"

    self.assertEqual(actual_rule, expected_rule)

  def test_handle_single_line_comment_left_unbalanced_brackets(self):
    """Does not get thrown off by left unbalanced brackets in single-line comments."""
    string = """
.another, .day {

  //.comment-rule {{{{{}
      .one, .two {
        outline: none;
      }
  // }
}
    """
    sse = string_scss_expand.StringSCSSExpand(82, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".another .one, .another .two, .day .one, .day .two"

    self.assertEqual(actual_rule, expected_rule)

  def test_handle_single_line_comment_right_unbalanced_brackets(self):
    """Does not get thrown off by right unbalanced brackets in single-line comments."""
    string = """
.another {

  //.comment-rule }}}}}}
      .one {
        outline: none;
      }
  // }
}
    """
    sse = string_scss_expand.StringSCSSExpand(63, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".another .one"

    self.assertEqual(actual_rule, expected_rule)



