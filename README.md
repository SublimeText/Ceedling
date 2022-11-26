# Ceedling for Sublime Text 3+

The Ceedling for Sublime Text package has been substantially rewritten and currently supports:

- Sublime Text 3+
- Ceedling gem v0.28.1 or later

The package has been developed on macOS, and tested on Windows 10 and Ubuntu 22.04 LTS.

## Important Note

This update has breaking changes with the previous version and no longer supports invoking commands using `rake`.

This reflects changed behaviour introduced in v0.28.1 of the Ceedling gem:

> Using a modern version of Ceedling means that you issue commands like ceedling test:all instead of rake test:all. If you have a continuous integration server or other calling service, it may need to be updated to comply.

> Similarly, older versions of Ceedling actually placed a rakefile in the project directory, allowing the project to customize its own flow. For the most part this went unused and better ways were later introduced. At this point, the rakefile is more trouble than its worth and often should just be removed.

Refer to [CeedlingUpgrade.md](https://github.com/ThrowTheSwitch/Ceedling/blob/master/docs/CeedlingUpgrade.md) for details.


## Additional Requirements
To use the Ceedling plugin you'll need:
- Ruby version supported by Ceedling (3.0.x recommended)
- GCC compiler for default builds
- Ceedling 0.28.1 or later (tested with 0.31.1)

## Installation

### Plugin
The preferred method of installing the Ceedling plugin is using `Package Control`.
[Install Package Control](https://packagecontrol.io/installation) if you haven't done so previously then:
- Open the command palette
- Select `Package Control: Install Packages`
- Type `Ceedling`
- Click the package listing to install.

When you launch Sublime Text, it will pick up the contents of this package so that you can consume the goodness that it provides.

## Functionality in Ceedling

### New Project
`New Project` comes in two flavours.
* The default `Ceedling: New Project` is a bare bones install containing `project.yml`, `src` and `test` folders.
* `Ceedling: New Project (Local)` adds a `ceedling` executable bash script, and `vendor` directory which contains the current version of the Ceedling framework.


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


### Key mapping
A number of key commands for working with modules are predefiend. The main shortcuts follow the naming scheme *h*eader, *s*ource, *t*est and *m*odule.

| Key command | Function |
|:--|:--|
|`super-ctrl-h` | Open Header File |
|`super-ctrl-s` | Open Source File |
|`super-ctrl-t` | Open Test File |
|`super-ctrl-m` | Open Module Files |
|`super-ctrl-right` | Cycle through module files |
|`super-ctrl-x` |  Clean project |

### Commands

| Command Name | Description |
|:--|:--|
| Ceedling: New Project | `ceedling new name`|
| Ceedling: New Project (Local) | `ceedling --local new name` |
| Ceedling: Clean Project | `ceedling clean` |
| Ceedling: Clobber Project | `ceedling clobber`|
| Ceedling: Create New Module | `ceedling create:module name`|
| Ceedling: Open Module Header | Opens header for current module |
| Ceedling: Open Module Source | Opens source for current module |
| Ceedling: Open Module Test | Open test for current module |
| Ceedling: Open Next Module File | Cycle through header, source and test for current module |
| Ceedling: Open Module Files | Open all module files in 2 column layout |
| Ceedling: Edit Project Configuration | Opens `project.yml` |
| Ceedling: Test Summary | Print summary of previously run tests |
| Ceedling: Version | Print version information for ceedling used in current project. |
| Ceedling: Environment | Display ENV variables set by ceedling |

### Completions and Snippets

Completions are scope sensitive and requires use of a C/C++ syntax that identifies function blocks.

The plugin will work with:
- Built-in Sublime Text `C` and `C++` syntaxes
- [C99](https://packagecontrol.io/packages/C99)
- [C Improved](https://packagecontrol.io/packages/C%20Improved)

Completions are available if the active file includes "unity.h".

Placing the caret/cursor within:
- a C/C++ file activates snippets for template test functions.
- a function activates snippets for Unity assertions.

There are completions for most Unity assertions.
The triggers follow a basic schema using the first letter of the key being targeted.


af - TEST_ASSERT_FALSE
afms - TEST_ASSERT_FALSE_MESSAGE
at - TEST_ASSERT_TRUE
atms - TEST_ASSERT_TRUE_MESSAGE
ig - TEST_IGNORE
igms - TEST_IGNORE_MESSAGE

eei - TEST_ASSERT_EACH_EQUAL_INT
ei  - TEST_ASSERT_EQUAL_INT
eia - TEST_ASSERT_EQUAL_INT_ARRAY
gti - TEST_ASSERT_GREATER_THAN_INT
goi - TEST_ASSERT_GREATER_OR_EQUAL_INT
loi - TEST_ASSERT_LESS_OR_EQUAL_INT
lti - TEST_ASSERT_LESS_THAN_INT
iaw - TEST_ASSERT_INT_ARRAY_WITHIN
nei - TEST_ASSERT_NOT_EQUAL_INT

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

