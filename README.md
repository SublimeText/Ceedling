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
The preferred method of installing the Ceedling for ST3+ plugin is using [Package Control](https://packagecontrol.io/installation).

With Package Control installed:
- Open the command palette
- Select `Package Control: Install Packages`
- Type `Ceedling`
- Click the package listing to install.

When you launch Sublime Text, it will pick up the contents of this package so that you can consume the goodness that it provides.

## Functionality in Ceedling for Sublime Text 3+

### New Project
`New Project` comes in two flavours.

* The default `Ceedling: New Project` is basic install containing `project.yml`, `src` and `test` folders.
* `Ceedling: New Project (Local)` adds a `ceedling` executable script, and a `vendor` directory which contains the current version of the Ceedling framework.


#### Creating a New Project
1. Open a `File » New Window` in Sublime Text
1. Open the command palette (Tools > Command Palette) and type `cnp` to narrow down the options.
1. Select `Ceedling: New Project` or `Ceedling: New Project (Local)`
1. Enter project folder location in the panel.\
For example `~/projects/drsurly` will create a project folder `drsurly` within the `projects` folder.\
`~` expands to the current user home directory.
1. Hit return/enter.

The project folder should open in the current window .

#### Customising New Project creation
The default parent folder for new projects is set to `~` by default.

To change the default folder open the Ceedling settings `Preferences » Package Settings » Ceedling » Settings`.

Add the following entry to `User Settings`, update the path as desired, then save.


```JSON
{
    "default_project_folder": "~/path/to/parent/folder/",
    "project_options": ["--gitignore", "--docs"]
}
```

`project_options` provides additional control over project creation.

Options are disabled by default. Adding an option to `project_options` will enable.

```sh
--docs  "Add docs in project vendor directory"

--local  "Create a copy of Ceedling in the project vendor directory"

--gitignore  "Create a gitignore file for ignoring ceedling generated files"

--no_configs  "Don't install starter configuration files"
```

#### Adding Ceedling to existing projects
The `New Project` module can be used to add Ceedling support to exisiting source code.\
Existing files and folders are not overwritten or modified in the process.\
Use the path of the existing project when prompted for the location.


### Create New Module

The `Create New Module` command now uses paths relative to the project folder.

Specifying `basename` will generate the files `test/test_basename.c`, `src/basename.h` and `src/basename.c` by default.

Additional naming schemes are supported using an abbreviated format identifiers:

| Abbreviation | Naming Scheme | Files |
|:--|:--|--:|
| src | header, source, test (default) | 3 |
| test | test file only | 1 |
| mch | model, conductor, hardware | 9 |
| mvp | model, view, presenter | 9 |
| dhi | driver, hardware, interrupt | 9 |
| dh | driver, hardware | 6 |

`mch`, `mvp`, `dhi` and `dh` schemes generate header, source and test files for each of the named modules.

### Running tests
The Sublime Text build system is used to run all tests.

From `Tools » Build System` menu select `Ceedling` as the build system for the project.

| Variant | Ceedling Task | Notes |
|:--|:--|:--|
| Default | `test:filename` | Test current module|
| Test All | `test:all` | Test all modules|
| Test Changes | `test:delta` | Test changed modules |
| Test Build only | `test:build_only`  | Build all without testing |
| Clean and Test file | `clean test:filename` | |
| Release | `release` | The release config is disabled in new project.yml. |

Select variants using `Control-Shift-B` (Windows, Linux) /`Command-Shift-B` (macOS).

Run last selected build variant using `Control-B` (Windows, Linux) / `Command-B`(macOS).


### Key mappings

A number of key commands for working with modules are predefined.

| Key command | Function |
|:--|:--|
|`super-ctrl-h` | Open Header File |
|`super-ctrl-s` | Open Source File |
|`super-ctrl-t` | Open Test File |
|`super-ctrl-m` | Open Module Files in 2 column layout |
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

## Completions
There are now around 200 completions  with matching `message` versions.

Completions are scope sensitive and require use of a C/C++ syntax that correctly identifies function blocks.

The completions are known to work with:
- Built-in Sublime Text `C` and `C++` syntaxes
- [C99](https://packagecontrol.io/packages/C99)
- [C Improved](https://packagecontrol.io/packages/C%20Improved)

**Completions are only active if the current file includes "unity.h"**

### Unit Test Function Templates

Unit test method function templates are active when the caret is outside a function body.

| Shortcut | Assertion |
|:--|:--|
| `test` | unit test function template |
| `testi` | unit test function template with TEST_IGNORE(message) |
| `testf` | unit test function template with TEST_FAIL(message) |

### Assert Completions

To keep response snappy the completions are filtered based on the shortcut sequence.

Assert completions are active when the caret is within a function body.

#### Basic fail and ignore
| Shortcut  | Assertion |
|:--|:--|
| `p` | `TEST_PASS` |
| `f` | `TEST_FAIL` |
| `i` | `TEST_IGNORE` |

#### `boolean` types

| Shortcut | Assertion  |
|:--|:--|
| `at` | `TEST_ASSERT_TRUE` |
| `au` | `TEST_ASSERT_UNLESS` |
| `af` |  |
|  |  |
|  |  |

#### `integer` types
| Shortcut | Assertion |
|:--|:--|
|`ex` | TEST_ASSERT_EQUAL_X |
|`eex` | TEST_ASSERT_EACH_EQUAL_X |
|`gx` | TEST_ASSERT_GREATER_THAN_X |
|`gox` | TEST_ASSERT_GREATER_OR_EQUAL_X |
|`lx` | TEST_ASSERT_LESS_THAN_X |
|`lox` | TEST_ASSERT_LESS_OR_EQUAL_X |
|`nex` | TEST_ASSERT_NOT_EQUAL_X |
|`xw` | TEST_ASSERT_X_WITHIN |
|`xa` | TEST_ASSERT_EQUAL_X_ARRAY |
|`xaw` | TEST_ASSERT_X_ARRAY_WITHIN |

Where `x` is:
- `i`, `i8`, `i16`, `i32`, `i64`
- `u`, `u8`, `u16`, `u32`, `u64`
- `h`, `h8`, `h16`, `h32`, `h64`
- `c`: char
- `sz`: size_t

#### `double` and `float` types
| Shortcut | Assertion |
|:--|:--|
|`xw` | TEST_ASSERT_X_WITHIN |
|`ex` | TEST_ASSERT_EQUAL_X  |
|`exa` | TEST_ASSERT_EQUAL_X_ARRAY |
|`eex` | TEST_ASSERT_EACH_EQUAL_X |

Where `x` is:
- `d`: double
- `f`: float


#### `struct` and `string` types
| Shortcut | Assertion |
|:--|:--|
|`eex` | TEST_ASSERT_EACH_EQUAL_X |
|`ex`  | TEST_ASSERT_EQUAL_X |
|`exa` | TEST_ASSERT_EQUAL_X_ARRAY |

Where `x` is:
- `p`: pointer
- `s`: string
- `m`: memory


### Messages
Append `ms` to a shortcut to access the message variant.



## Previous version features currently missing

* ~~Snippets for CMock mocks~~
    * ~~FuncBeingMocked.e + [TAB] => FuncBeingMocked_Expect(<parameters>)~~
    * ~~FuncBeingMocked.er + [TAB] => FuncBeingMocked_ExpectAndReturn(<parameters>)~~

