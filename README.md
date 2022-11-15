## Description

[Ceedling](http://throwtheswitch.org/) is a set of tools and libraries for testing and building C applications. This package adds support to Sublime Text 4 for developing Ceedling applications.

## Ceedling Installation

If you already have the Ruby scripting language installed with RubyGems support, simply execute the following at the command line:

```sh
gem install ceedling
```

## Package Installation

Bring up a command line in the Packages/ folder of your Sublime user folder, and execute the following:

```sh
mkdir Ceedling
cd Ceedling
git init
git pull git://github.com/SublimeText/Ceedling.git

```

When you launch Sublime Text 4, it will pick up the contents of this package so that you can consume the goodness that it provides.

## Functionality in Ceedling ST4

### New Project
`New Project` comes in two flavours.
* `Minimal` is a bare bones install containing `project.yml`, `src` and `test` folders.
* `Portable` adds a `ceedling` executable bash script, and `vendor` directory.

To create a new Ceedling project:
1. Open a new window in Sublime Text
1. Open the command palette (Tools > Command Palette) and type `cn`
1. Select `Minimal` or `Portable`
1. Enter a path to where project folder location in the panel.\
For example `~/projects/drsurly` will create a project folder `drsurly` within the `projects` folder.\
`~` expands to the current users home directory.
1. Hit return/enter.

The project folder should open in the current window a few seconds later.

#### Default settings
To set a default parent folder for new projects open the Ceedling settings `Preferences >> Package Settings >> Ceedling >> Settings`.

Add the following entry to the file on the right, and update the path, then save.
```JSON
{
    "default_project_folder": "~/path/to/parent/folder/",
}
```

#### Adding Ceedling to existing projects
The `New Project` module can also be used to add Ceedling support to exisiting source code.\
Existing files and folders are not overwritten or modified in the process.\
Use the path of the existing project when prompted for the location.


### Create New Module
The `Create New Module` command now uses paths relative to the project folder.
Specifying `basename` will generate the files `test/test_basename.c`, `src/basename.h` and `src/basename.c` by default.

Additional naming schemes are supported using an abbreviated format identifiers:

* mch - model, conductor, hardware
* mvp - model, view, presenter
* dhi - driver, hardware, interrupt
* dh - driver, hardware
* test - test file only
* src - header, source, test (default output)

The first four schemes generate header, source and test files for each of the named variants.



## Features
* Ceedling.sublime-build for executing unit tests for the active module via <F7>
    * You must assign the builder for your project to 'Ceedling'
* Snippets for Unity unit testing framework macros
* Snippets for Unity unit test methods
	* test ⇥ => unit test method template
	* testi<TAB> => unit test method template with TEST_IGNORE(message)
	* testf<TAB> => unit test method template with TEST_FAIL(message)
* Snippets for CMock mocks
    * FuncBeingMocked.e<TAB> => FuncBeingMocked_Expect(<parameters>)
    * FuncBeingMocked.er<TAB> => FuncBeingMocked_ExpectAndReturn(<parameters>)
