# INTRODUCTION

***Jesting Language*** is a minimalist functional language, 
intended to be compatible with Spreedsheet syntax found 
in Microsoft's Excel, Libre Office's Calc or Google's 
Sheets. As such, it can be considered a subset of the 
lenguages used in those programs, but lacking many of the 
rich syntax and functions they use.

It was created for the JESTING tool, a Python program 
that emulates behaviour similar to those Spreedsheet 
Applications using Curses.

I happened to find myself working with esoteric uses for the 
spreedsheet syntax, and it turns out that if TDD was in order,
the most entertaining way to do it was with python.

# Syntax and AST

The Jesting Lang syntax follows the standard used by most
spreedsheets programs, allowing simple operations (+, -, *
, /, =, & ), the **IF token** (to allow branching), the use of 
indirections to other cells such as A2 (key behaviour or
spreedhseets) and the **INDIRECT token** (to give more power to 
those indirections)

For example

    = 1 + 1 -> becomes 2
    = "A" & "B" -> becomes AB
    = "A" & 2 -> becomes A2
    = A2 -> becomes an indirection to cell A2
    = INDIRECT("A" & 2) -> becomes an indirection to cell A2
    = IF(0 = 0 , 2 , 3) -> becomes 3

The AST can become more complex, with nodes such as 
*EmptyValue* or *DateValue*. However, they can be easily
solved by using the Visitors provided in this library.

# Fixed vs Volatile Visitors

Some APPS using JestingLang may need to precompile a tree 
without actually resolving values and references, as the 
value of a cell may get updated data every once in a while 
without updating the formula behind it. With that in mind,
the concept of **volatile** was included in this lib. 

A volatile Node is one such that it has (or includes or some 
sub-branch that has) a value that is not fixed. In turn, a 
volatile visitor is one that resolves all volatile nodes 
when visiting a tree. A fixed tree does the opposite, and 
returns a Tree without exploring any volatile Node. 

# TODO

* Finish dates