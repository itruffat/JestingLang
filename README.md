## INTRODUCTION

This repository mantains the **JestingLang** project and
its related components, which includes both the core
***JestingLang*** Language and it's more complex offspring, 
the ***JestingScript*** Language. 

The idea behind this initiative was to provide a tool 
we can use to prove the often-overlooked computational 
power of `Spreedsheets` and the unamed, underlying Syntax 
most of them share in common. I am not the first one to 
notice this, and the point has become particularly popular 
after Felienne Harmans' ["Pure functional Programming in 
Excel"](https://www.youtube.com/watch?v=0yKf8TrLUOw) 
presentation. (A bit old at this point, but that's a very 
fun presentation with a Turing Machine written in Excel, 
personally recommended if you have the time)

It was first used it for my Python-oriented SpreedSheet 
simulator, called JestingApp (`currently being refactored`), 
which is where the names of the languages were derived from. 
However, it was moved to it's own repositoryto make it 
available to other projects.

## Jesting Language


The **JestingLang** language is an ultra-minimalist 
functional-like language, imitating what would 
generally be found inside one cell in a spreedsheet 
appllication.

       IF(1+1 = $A2 , 'Hello' , 'World')

One useful way to think about it would be as a subset 
of the cell-languages used in programs such as 
**Microsoft's Excel**, **Libre Office's Calc** and 
**Google's Sheets**. 


     Disclaimer: due to the language being compatible with 
     all of those tools, `JestingLang` lacks most of the more 
     complex functions these tools use but don't share in 
     common. (For example `VLOOKUP`) 
     
     This makes it technically weaker that all of them, but 
     still capable enough to prove it's power.



In a more practical sense, the expectationis for the 
language is to be interpreted by some `supervisor` that 
controls many of these cells in parallel, sometimes referencing one-another in some way. Exactly how the cells would be 
deferenced or in which order things are executed is not defined 
in the language itself. Instead, those are things to be decided 
by the `supervisor` that's running them.

## Syntax and AST

The `JestingLang` syntax follows the standard used by most
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

## Jesting Script

If we were to imitate a spreedsheet application's behavior, one shortcomming of the `supervisor` approach given by ***Jesting Lang*** 
is that we loose any way to track `side-effects` that appear when 
filling the cells. In applications like Excel, details like which 
cells first were filled first can actually change the data.

In other words, we could have 2 programs with exactly the same
initial values in every cells, that return completely different
results because they were done in differnet order.

To capture this chronological behaviour, we also introduce the
***JestingScript*** Language, a super-set of ***JestingLang***
that explicitly includes `side-effects`. Concepts like *"opening*
*a file"*, *"Storing information at a location"* and *"Waiting for*
*time to pass"* are all present in this new language.


    } BOOK_A
    A1 << 12
    ;
    A3 <~ A1 * 2
    ;
    { BOOK_A

## Python Implementation

### Structures: T.V.D.

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

### Fixed vs Volatile Visitors

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


### Running JestingScript

Let's imagine we have the following *example.jestScript* file:

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

### TODO

* Finish dates as datatypes
* Add function for readall
* Use the script visitor to create more test cases