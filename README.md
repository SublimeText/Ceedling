Description
===========
[Ceedling](http://throwtheswitch.org/) is a set of tools and libraries for testing and building C applications. This package adds support to Sublime Text for developing Ceedling applications.

Ceedling Installation
=====================
If you already have the Ruby scripting language installed with RubyGems support, simply execute the following at the command line:

> gem install ceedling

Package Installation
====================
Bring up a command line in the Packages/ folder of your Sublime user folder, and execute the following:
> mkdir Ceedling
> cd Ceedling
> git init
> git pull git://github.com/SublimeText/Ceedling.git

When you launch Sublime Text, it will pick up the contents of this package so that you can consume the goodness that it provides.

Features
========
* Ceedling.sublime-build for executing unit tests for the active module via <F7>
    * You must assign the builder for your project to 'Ceedling'
* Snippets for Unity unit testing framework macros
* Snippets for Unity unit test methods
	* test<TAB> => unit test method template
	* testi<TAB> => unit test method template with TEST_IGNORE(message)
	* testf<TAB> => unit test method template with TEST_FAIL(message)
* Snippets for CMock mocks
    * FuncBeingMocked.e<TAB> => FuncBeingMocked_Expect(<parameters>)
    * FuncBeingMocked.er<TAB> => FuncBeingMocked_ExpectAndReturn(<parameters>)
