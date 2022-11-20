## Reboot Note
The Ceedling support package is currently being rewritten and supports:
- Sublime Text 3+
- Ceedling 0.28.1 or later

The package has been tested for basic functionality on macOS, Windows 10 and Ubuntu 22.04 LTS.

## Description

[Ceedling](http://throwtheswitch.org/) is a set of tools and libraries for testing and building C applications. This package adds support to Sublime Text for developing Ceedling applications.

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

When you launch Sublime Text, it will pick up the contents of this package so that you can consume the goodness that it provides.

## Functionality in Ceedling

### New Project
`New Project` comes in two flavours.
* The default `Ceedling: New Project` is a bare bones install containing `project.yml`, `src` and `test` folders.
* `Ceedling: New Project (Local)` adds a `ceedling` executable bash script, and `vendor` directory.

#### Creating a New Project
1. Open a `File >> New Window` in Sublime Text
1. Open the command palette (Tools > Command Palette) and type `cnp` to narrow down the options.
1. Select `Ceedling: New Project` or `Ceedling: New Project (Local)`
1. Enter project folder location in the panel.\
For example `~/projects/drsurly` will create a project folder `drsurly` within the `projects` folder.\
`~` expands to the current user home directory.
1. Hit return/enter.

The project folder should open in the current window .

#### Customising New Project creation
The default parent folder for new projects is set to `~` by default.
To change this open the Ceedling settings `Preferences >> Package Settings >> Ceedling >> Settings`.

Add the following entry to the file on the right, update the path as desired, then save.

```JSON
{
    "default_project_folder": "~/path/to/parent/folder/",
    "project_options": ["--gitignore", "--docs"]
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

## Running tests
Sublime Text's build system is used to run tests.

From `Tools >> Build System` menu select `Ceedling` as the build system for the project.

| Variant | Ceedling Task | Notes |
|:--|:--|:--|
| Default | `test:filename` | Test current module|
| Test All | `test:all` | Test all modules|
| Test Changes | `test:delta` | Test changed modules |
| Test Build only | `test:build_only`  | Build all without testing |
| Clean and Test file | `clean test:filename` | |
| Release | `release` | The release config is disabled in new project.yml. |

Select variants using `ctrl-shift-b`/`command-shift-b`.
Run last selected build variant using `ctrl-b` / `command-b`.


## Key commands
| Key command | Function |
|:--|:--|
|`super-ctrl-h` | Open Header File |
|`super-ctrl-s` | Open Source File |
|`super-ctrl-t` | Open Test File |
|`super-ctrl-right` | Cycle through module files |
|`super-ctrl-x` |  Clean project |


## Features
* Ceedling.sublime-build for executing unit tests for the active module via `ctrl-b`/`command-b`
    * You must assign the build system for your project to 'Ceedling'
* Snippets for Unity unit testing framework macros
* Snippets for Unity unit test methods
	* test + [TAB] => unit test method template
	* testi + [TAB] => unit test method template with TEST_IGNORE(message)
	* testf + [TAB] => unit test method template with TEST_FAIL(message)
* Snippets for CMock mocks
    * FuncBeingMocked.e + [TAB] => FuncBeingMocked_Expect(<parameters>)
    * FuncBeingMocked.er + [TAB] => FuncBeingMocked_ExpectAndReturn(<parameters>)

