Sublime SCSS Expander
=====================
[![Build Status](https://travis-ci.org/garetht/sublime-scss-expander.svg?branch=master)](https://travis-ci.org/garetht/sublime-scss-expander)

Suppose you're working on a particularly long project written using the SCSS syntax, and you're starting to forget the nesting structure of the current rule is.

```scss
//... {
        .foo {
          .bar {
            // what CSS rule is being generated here?
          }
        }
//... }
```

It's possible to look at the generated CSS, of course, if the generated stylesheets are not too complex. But even that requires keeping another file open somewhere and hunting for line numbers. Most of the time you just want an answer straight away.

## Installation and Usage
`sublime-scss-expander` helps you do that: position the cursor in the scope of the rule you want to know about, and press **command-E** by default to show the rule that is in scope at that position. It is also be available in the command palette as **SCSS Expander: Expand Cursor Scope**.

## Support
It supports most sane uses of SCSS, including SASS 3.3's **@at-root** with all possible arguments, various permutations of the **parent selector** as well as combinatorically combined comma-separated rules.

Because it is **not a parser**, it works only when you give it correct code. It does not currently support content-blocks that masquerade as rules. It will also be slightly confused (for now) if you start in the middle of a comment block. It does not even attempt to peek inside any imports.

## Tests
There's a mound of tests which hopefully give good coverage. These are located in `scss_expand_test.py`. This does not test Sublime Text directly; instead, the expander can and has been generalized to work with any piece of text given a starting position within that text and a function that, given an index, returns the character at that position within the text. This means that the main Python class, `SCSSExpander`, can be exported for use with other projects.
