SCSS Expander
=====================
[![Build Status](https://travis-ci.org/garetht/sublime-scss-expander.svg?branch=master)](https://travis-ci.org/garetht/sublime-scss-expander)

Suppose you're working on a particularly long project written using the SCSS syntax, and you're starting to forget the nesting structure of the current rule is.

```scss
//... {
        .foo {
          &.bar {
            // what CSS rule is being generated here?
          }
        }
//... }
```

It's possible to look at the generated CSS, of course, if the generated stylesheets are not too complex. But even that requires keeping another file open somewhere and hunting for line numbers. Most of the time you just want an answer straight away; here, you might get this answer:

```
.bim
.baz
.foo.bar
```

(because Sublime Text's alert window has remarkably little space.)

## Installation and Usage
`sublime-scss-expander` does that for you. To install, either place this repository in the Sublime packages folder or use the far simpler **Sublime Package Control**. Press `ctrl+shift+p` on Windows/Linux and `cmd+shift+p` on a Mac to bring up Sublime's Command Palette, then type install package to bring up Package Control's package selector. It should be the first selection. Type **SCSS Expander** which, again, should be the first selection, and then hit enter.

To use, position the cursor in the scope of the rule you want to know about, and press **command-E** by default to show the rule that is in scope at that position. It is also available in the command palette as **SCSS Expander: Expand Cursor Scope**.

![](http://cl.ly/image/0o2J3a3Y0a2G/scss-expander.png)

## Support
It supports most sane uses of SCSS, including SASS 3.3's **@at-root** with all possible arguments, various permutations of the **parent selector** as well as combinatorically combined comma-separated rules.

Because it is **not a parser**, it works only when you give it correct code. It does not expand content-blocks that masquerade as rules. It does not even attempt to peek inside any imports.

### Examples
Here are a few examples of how it works. In each case assume the cursor is placed in the **innermost scope**. All examples are drawn from the tests; look in the test file for more.

#### Comma-separated rules
```scss
.first-rule, .second-rule {
  &:hover {
    font-weight: 500;
  }
}
```
```
.first-rule:hover,
.second-rule:hover
```
#### Interpolated variables
```scss
.bim {
  @for $thing in (foo bar) {
    .test-#{$thing}-bling {
      width: 20px;
    }
  }
}
```
```
.bim .test-#{$thing}-bling
```
#### At-root without
```scss
@media screen {
  @supports something {
    .foo {
      @at-root(without: rule media) .bar {
        top: 0;
      }
    }
  }
}
```
```
@supports something .bar
```

## Tests
There's a mound of tests which hopefully give good coverage. These are located in `scss_expand_test.py`. This does not test Sublime Text directly; instead, the expander can and has been generalized to work with any piece of text given a starting position within that text and a function that, given an index, returns the character at that position within the text. This means that the main Python class, `SCSSExpander`, can be exported for use with other projects.
