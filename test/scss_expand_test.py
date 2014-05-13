import unittest, sys

if sys.version < '3':
  from src.src_two.string_scss_expand import StringSCSSExpand
else:
  from src.src_three.string_scss_expand import StringSCSSExpand


class TestScssExpand(unittest.TestCase):

  def test_one_rule(self):
    """Can handle one unnested rule."""
    string = ".hello{margin: 0}"
    sse = StringSCSSExpand(10, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".hello"

    self.assertEqual(actual_rule, expected_rule)

  def test_two_rules(self):
    """Can handle two unnested rules separated by a comma."""
    string = ".baz,.bang{padding:0}"
    sse = StringSCSSExpand(14, string)
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
    sse = StringSCSSExpand(42, string)
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
    sse = StringSCSSExpand(99, string)
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
    sse = StringSCSSExpand(37, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .bar"

    self.assertEqual(actual_rule, expected_rule)

  def test_single_line_nested_rules(self):
    """Can handle a rule that is nested within another on a single line."""
    string = ".baz{.bang{.three{.four#end{z-index: 2}}}}"
    sse = StringSCSSExpand(35, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".baz .bang .three .four#end"

    self.assertEqual(actual_rule, expected_rule)

  def test_other_combinator_nested_rules(self):
    """Can handle a rule that is nested within another on a single line using other combinators."""
    string = ".baz{ + .bang{.three{> .four#end{z-index: 2}}}}"
    sse = StringSCSSExpand(35, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".baz + .bang .three > .four#end"

    self.assertEqual(actual_rule, expected_rule)

  def test_newline_comma_rules(self):
    """Can handle comma-separated rules broken into multiple lines."""
    string = """
.foo,
.bar {
  .baz {
    outline: none;
  }
}
    """
    sse = StringSCSSExpand(28, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .baz, .bar .baz"

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
    sse = StringSCSSExpand(37, string)
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
    sse = StringSCSSExpand(37, string)
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
    sse = StringSCSSExpand(63, string)
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
    sse = StringSCSSExpand(63, string)
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
    sse = StringSCSSExpand(21, string)
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
    sse = StringSCSSExpand(49, string)
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
    sse = StringSCSSExpand(49, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .bang.baz, .foo .bim.baz, .bar .bang.baz, .bar .bim.baz"

    self.assertEqual(actual_rule, expected_rule)

  def test_handle_block_comment_rules(self):
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
    sse = StringSCSSExpand(88, string)
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
    sse = StringSCSSExpand(102, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .baz, .foo .bang, .bar .baz, .bar .bang"
    self.assertEqual(actual_rule, expected_rule)

  def test_handle_block_comment_start(self):
    """Searches outside the comment scope if the cursor starts at the comment."""
    string = """
.baz {
  height: 10px;
  /* .foo, .bar {
    width: 14px;
  }
  */
}
    """
    sse = StringSCSSExpand(48, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".baz"

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
    sse = StringSCSSExpand(77, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .baz, .foo .bang, .bar .baz, .bar .bang"

    self.assertEqual(actual_rule, expected_rule)

  def test_handle_bracketless_single_line_comment_rule(self):
    """Does not include single-line comments without brackets before rules."""
    string = """
// comment here
.foo {
  .bar { width: 20px; }
}
    """
    sse = StringSCSSExpand(33, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .bar"

    self.assertEqual(actual_rule, expected_rule)

  def test_handle_spliced_single_line_comments(self):
    """Does not include single-line comments without brackets before rules."""
    string = """
.baz,
// comment here
.foo {
  .bar { width: 20px; }
}
    """
    sse = StringSCSSExpand(40, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".baz .bar, .foo .bar"

    self.assertEqual(actual_rule, expected_rule)

  def test_handle_single_line_comment_single_line_with_interpolation(self):
    """Does not include single-line comments before lines with interpolation."""
    string = """
// another comment here
.foo {
  .bar { width: #{$height} - 20px; }
}
    """
    sse = StringSCSSExpand(50, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .bar"

    self.assertEqual(actual_rule, expected_rule)

    sse = StringSCSSExpand(62, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .bar"

    self.assertEqual(actual_rule, expected_rule)


  def test_handle_complex_single_line_comment(self):
    """Does not include rules in single-line comments"""
    string = """
.foo {// bar: baz;}
  baz: bang; //}
}
    """
    sse = StringSCSSExpand(27, string)
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
    sse = StringSCSSExpand(82, string)
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
    sse = StringSCSSExpand(63, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .baz"

    self.assertEqual(actual_rule, expected_rule)

  def test_handle_interpolation(self):
    """Treats an interpolated variable as part of a selector."""
    string = """
$foo: 14;
.bar-#{$foo}-type {
  height: 12px;
}
    """

    sse = StringSCSSExpand(38, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".bar-#{$foo}-type"

    self.assertEqual(actual_rule, expected_rule)

  def test_handle_multiple_interpolation(self):
    """Treats multiple interpolated variables as part of a selector."""
    string = """
$foo: 14;
$bim: 22;
.baz {
  .bar-#{$foo}-type-#{$bim} {
    height: 12px;
  }
}

    """

    sse = StringSCSSExpand(67, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".baz .bar-#{$foo}-type-#{$bim}"

    self.assertEqual(actual_rule, expected_rule)

  def test_ignore_loops(self):
    """Does not list loops as part of output."""
    string = """
.bim {
  @for $thing in (foo bar) {
    .test-#{$thing}-bling {
      width: 20px;
    }
  }
}

    """
    sse = StringSCSSExpand(63, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".bim .test-#{$thing}-bling"

    self.assertEqual(actual_rule, expected_rule)

  def test_include_other_directives(self):
    """Includes directives such as @media."""
    string = """
@media only print, only screen and (max-device-width: 480px) {
  .foo {
    width: 200px;
  }
}
    """
    sse = StringSCSSExpand(80, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = "@media only print, only screen and (max-device-width: 480px) .foo"

    self.assertEqual(actual_rule, expected_rule)

  def test_at_root(self):
    """Supports the @at-root directive without any arguments."""
    string = """
@media screen {
  @supports something {
    .foo {
      @at-root .bar {
        top: 0;
      }
    }
  }
}
    """
    sse = StringSCSSExpand(84, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = "@media screen @supports something .bar"

    self.assertEqual(actual_rule, expected_rule)

  def test_at_root_without_all(self):
    """Supports the @at-root directive while excluding all directives and rules."""
    string = """
@media screen {
  @supports something {
    .foo {
      @at-root(without: all) .bar {
        top: 0;
      }
    }
  }
}
    """
    sse = StringSCSSExpand(95, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".bar"

    self.assertEqual(actual_rule, expected_rule)

  def test_at_root_with_rule(self):
    """Supports the @at-root directive while including all rules."""
    string = """
@media screen {
  @supports something {
    .foo {
      @at-root(with: rule) .bar {
        top: 0;
      }
    }
  }
}
    """
    sse = StringSCSSExpand(95, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = ".foo .bar"

    self.assertEqual(actual_rule, expected_rule)

  def test_at_root_with(self):
    """Supports the @at-root directive while including some rules."""
    string = """
@media screen {
  @supports something {
    .foo {
      @at-root(with: supports) .bar {
        top: 0;
      }
    }
  }
}
    """
    sse = StringSCSSExpand(100, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = "@supports something .bar"

    self.assertEqual(actual_rule, expected_rule)

  def test_at_root_without(self):
    """Supports the @at-root directive while excluding some rules."""
    string = """
@media screen {
  @supports something {
    .foo {
      @at-root(without: media) .bar {
        top: 0;
      }
    }
  }
}
    """
    sse = StringSCSSExpand(104, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = "@supports something .bar"

    self.assertEqual(actual_rule, expected_rule)

  def test_at_root_without_rule(self):
    """Supports the @at-root directive while excluding all rules, the same as with no arguments."""
    string = """
@media screen {
  @supports something {
    .foo {
      @at-root(without: rule) .bar {
        top: 0;
      }
    }
  }
}
    """
    sse = StringSCSSExpand(104, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = "@media screen @supports something .bar"

    self.assertEqual(actual_rule, expected_rule)

  def test_at_root_without_rule_and_other(self):
    """Supports the @at-root directive while excluding rules and other directives at the same time."""
    string = """
@media screen {
  @supports something {
    .foo {
      @at-root(without: rule media) .bar {
        top: 0;
      }
    }
  }
}
    """
    sse = StringSCSSExpand(100, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = "@supports something .bar"

    self.assertEqual(actual_rule, expected_rule)

  def test_at_root_block(self):
    """Supports the @at-root directive as a block."""
    string = """
@media screen {
  @supports something {
    .foo {
      @at-root {
        .bar {
          top: 0;
        }
        .baz {
          bottom: 0;
        }
      }
    }
  }
}
    """
    sse = StringSCSSExpand(138, string)
    actual_rule = sse.coalesce_rule()
    expected_rule = "@media screen @supports something .baz"

    self.assertEqual(actual_rule, expected_rule)

  def test_comment_machine_single_simple(self):
    """Test pure functionality of comment machine with a one-line comment"""
    string = "//2345678\n"

    sse = StringSCSSExpand(0, string)
    sse.comment_machine(9)
    actual_comments = sse.comment_blocks
    expected_comments = [(0, 9)]

    self.assertEqual(actual_comments, expected_comments)

  def test_comment_machine_single_complex(self):
    """Test comment machine when comment is within rules"""
    string = """
.foo {
  width: 20px;
}
// This is a comment.
.bar {
  height: 20px;
}
    """

    sse = StringSCSSExpand(0, string)
    sse.comment_machine(64)
    actual_comments = sse.comment_blocks
    expected_comments = [(25, 46)]

    self.assertEqual(actual_comments, expected_comments)

  def test_comment_machine_single_nested(self):
    """Test comment machine when comment has comment"""
    string = """
.foo {
  width: 20px;
}
//// This is a comment.
.bar {
  height: 20px;
}
    """

    sse = StringSCSSExpand(0, string)
    sse.comment_machine(64)
    actual_comments = sse.comment_blocks
    expected_comments = [(25, 48)]

    self.assertEqual(actual_comments, expected_comments)

  def test_comment_machine_single_multiple(self):
    """Test comment machine with multiple single line comments"""
    string = """
// Hello comment
.foo {
  width: 20px;
}
//// This is a comment.
.bar {
  height: 20px;
}
    """

    sse = StringSCSSExpand(0, string)
    sse.comment_machine(80)
    actual_comments = sse.comment_blocks
    expected_comments = [(1, 17), (42, 65)]

    self.assertEqual(actual_comments, expected_comments)

  def test_comment_machine_block_single_line(self):
    """Test functionality of comment machine with a block comment"""
    string = "/*/345678*/ "

    sse = StringSCSSExpand(0, string)
    sse.comment_machine(11)
    actual_comments = sse.comment_blocks
    expected_comments = [(0, 10)]

    self.assertEqual(actual_comments, expected_comments)

  def test_comment_machine_block_multiple_lines(self):
    """Test functionality of comment machine with a block comment"""
    string = """
.foo {
  height: 30px;
}
/*
Things in here.
 */
.bar {
  width: 20px;
}
    """

    sse = StringSCSSExpand(0, string)
    sse.comment_machine(63)
    actual_comments = sse.comment_blocks
    expected_comments = [(26, 47)]

    self.assertEqual(actual_comments, expected_comments)

  def test_comment_machine_nested_multi_comments(self):
    """Test functionality of comment machine with single comments in block comments"""
    string = """
.foo {
  height: 30px;
}
/*
Things in here. // like this
 */
.bar {
  width: 20px;
}
    """

    sse = StringSCSSExpand(0, string)
    sse.comment_machine(80)
    actual_comments = sse.comment_blocks
    expected_comments = [(26, 60)]

    self.assertEqual(actual_comments, expected_comments)

  def test_comment_machine_multi_block_starters(self):
    """Test functionality of comment machine with multiple comment block starters"""
    string = """
.foo {
  height: 30px;
}
/* /* /*
/*
Things in here. // like this
 */
.bar {
  width: 20px;
}
    """

    sse = StringSCSSExpand(0, string)
    sse.comment_machine(90)
    actual_comments = sse.comment_blocks
    expected_comments = [(26, 69)]

    self.assertEqual(actual_comments, expected_comments)

  def test_comment_machine_mixed_comments(self):
    """Test functionality of comment machine with multiple comment block starters"""
    string = """
.foo {
  height: 30px;
  // a thing here
}
/* /* /*
/*
Things in here. // like this
 */
.bar {
  width: 20px;
}
/* thing there */
// end
    """

    sse = StringSCSSExpand(0, string)
    sse.comment_machine(138)
    actual_comments = sse.comment_blocks
    expected_comments = [(26, 41), (44, 87), (113, 129), (131, 137)]

    self.assertEqual(actual_comments, expected_comments)
