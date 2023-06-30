## INTRODUCTION

***Jesting Language*** is a minimalist functional-like 
language, intended to be compatible with the standard 
syntax used in most Spreadsheet applications, such as 
**Microsoft's Excel**, 
**Libre Office's Calc** and 
**Google's Sheets**. 
It can be considered a subset of the core languages used 
in those programs, but lacking many of the rich syntax and 
functions they use.

It was created for the JESTING APP, a Python-based 
Spreadsheet program used to emulate behaviours similar 
to those Spreadsheet Applications. Mostly to test 
esoteric code created to work on those applications.

## Syntax and AST

The Jesting Lang syntax follows the standard used by most
spreadsheets programs, allowing simple operations (+, -, *
, /, =, & ), the **IF token** (to allow branching), the use of 
indirections to other cells such as A2 (key behaviour or
spreadhseets) and the **INDIRECT token** (to give more power to 
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

## Structures: T.V.D.

Here are the 3 structures used in this project:

* **Trees** (Abstract Syntax Trees) are created based on the
  code given to compile, it is the "pure" state of the
  compiling/parsing process without any interpretation. 


* **Visitors** explore the trees and do something with them, 
  which could be as trivial as printing its data. The ones
  we will actually care about are those that take care of 
  doing the interpretations/execution of the AST. The idea 
  is to keep them "application-agnostic", so these visitors 
  do not manipulate memory directly on their own, and 
  have no way of directly resolving any reference.


* **De-referencers** can access memory and resolve the
  references used in the visitors. They exist to abstract
  the behaviour with secondary effect of "of real components" 
  such as databases. Most of the examples of this repo will
  be constrained to python structures, such as simple
  arrays or key-value maps.

## Fixed vs Volatile Visitors

Some APPS using JestingLang may need to precompile a tree 
without actually resolving values or references, as the 
value of a cell may get updated data every once in a while 
without updating the formula behind it. With that in mind,
the concept of **volatile** was included in this lib. 

A volatile Node is one such that it has (or includes or some 
sub-branch that has) a value that is not fixed. In turn, a 
volatile visitor is one that resolves all volatile nodes 
when visiting a tree. A fixed tree does the opposite, and 
returns a Tree without exploring any volatile Node. 


## JestingScript

A small variation has been made for the parser/lexer so
that more than one line can be provided and additional 
syntax instructions are understood. This means the 
language is no longer functional (since it now has side
effects), but it becomes more usable as it represents 
common things done in other spreadsheet APPs,
such as giving a cell a value, giving a cell a formula,
changing 'current sheet/page/cells', printing a value,
making a comment and making "time progress".

For example, if we had this as a file *example.jestScript*:

    // Comments are allowed and should always start with a '//'

    // Import code from other File
    *INCLUDE* imported_in_example.jestScript

    // Open a file
    } BOOK_A

    // Set the raw value "xxx 2" to the cell [BOOK_A]Sheet_A!A1
    //  (Note: First space is mandatory and will be ignored)
    [BOOK_A]Sheet_A!A1 << xxx 2

    // Set the default file and default sheet
    //  (Note: needs to be a complete cell for the moment)
    @ [BOOK_A]Sheet_A!A1

    //  Set the raw value "12" to the cell [BOOK_A]Sheet_A!A1
    A1 << 12

    // Set the result ("12") to the cell [BOOK_A]Sheet_A!A2 
    //  (Note: spaces are not important here)
    A2 <~ 12

    // Set the formula below to the cell [BOOK_A]Sheet_A!A3 
    A3 <~ A1 * 2

    // Run a Tick of time
    //  (Note: [BOOK_A]Sheet_A!A3 will become 24) 
    ;

    // Output the value of [BOOK_A]Sheet_A!A2 
    !A2

    // Output all of the values
    !!

    // Create an Alias
    FIRST_CELL ? A1

    // Use the Alias as a regular cell name
    FIRST_CELL << 12
    A2 <~ FIRST_CELL + 1
    !FIRST_CELL

    // Close a file
    { BOOK_A

We could compile it in Python with:

    lexerparser = LexerParser(multilineScript=True)
    parser = lexerparser.parser
    with open("example.jestScript", "r") as f:
         tree = parser.parse(f.read())

This is yet on an early stage, so it is not
powerful enough to use as a real interpreter. I plan to 
add a handful of test to make sure the language is working 
as expected. In the future, running this (or some derivation
of this) will probably be the main goal of this library.

## TODO

* Finish dates as datatypes
* Add function for readall
* Use the script visitor to create more test cases