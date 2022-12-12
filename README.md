# Ceedling for Sublime Text 3+

Ceedling is a set of tools and libraries for testing and building C applications.
This package adds support to Sublime Text 3+ for developing C applications using Ceedling.


## Important Note

Ceedling for Sublime Text 3+ contains breaking changes with the original Sublime Text 2 version and no longer supports invoking commands using `rake`.

This reflects changed behaviour introduced in v0.28.1 of the Ceedling gem:

> Using a modern version of Ceedling means that you issue commands like ceedling test:all instead of rake test:all. If you have a continuous integration server or other calling service, it may need to be updated to comply.

> Similarly, older versions of Ceedling actually placed a rakefile in the project directory, allowing the project to customize its own flow. For the most part this went unused and better ways were later introduced. At this point, the rakefile is more trouble than its worth and often should just be removed.

Refer to [CeedlingUpgrade.md](https://github.com/ThrowTheSwitch/Ceedling/blob/master/docs/CeedlingUpgrade.md) for details.


## Requirements
To use the Ceedling plugin you'll need:
- Ruby version supported by Ceedling (3.0.x recommended)
- GCC compiler for default builds
- Ceedling 0.28.1 or later (tested with 0.31.1)

The project wiki has some addition [setup information](https://github.com/SublimeText/Ceedling/wiki/Installing-Ceedling).

## Installation
### Plugin
The preferred method of installing the Ceedling for ST3+ plugin is using [Package Control](https://packagecontrol.io/installation).

With Package Control installed:

- Open the command palette
- Select `Package Control: Install Packages`
- Type `Ceedling`
- Click the package listing to install.

Unity test assert completions are now provided by the [`Unity Test Completions`](https://packagecontrol.io/packages/Unity%20Test%20Completions) package. This package is a recommended install.

To install both packages in one step:
- Open the command palatte
- Select `Package Control: Advanced Install Packages`
- Enter `Ceedling, Unity Test Completions` 
- Hit return/enter

When you launch Sublime Text, it will pick up the contents of these package so that you can consume the goodness they provide.

## Features

### New Project
`New Project` comes in two flavours.

* The default `Ceedling: New Project` is basic install containing `project.yml`, `src` and `test` folders.
* `Ceedling: New Project (Local)` adds a `ceedling` executable script, and a `vendor` directory which contains the current version of the Ceedling framework.


#### Creating a New Project
1. Open the command palette (Tools > Command Palette) and type `cnp` to narrow down the options.
1. Select `Ceedling: New Project` or `Ceedling: New Project (Local)`
1. A new window will open
1. Enter project folder location in the panel.

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




### Commands

| Command Name | Description |
|:--|:--|
| Ceedling: New Project | `ceedling new name`|
| Ceedling: New Project (Local) | `ceedling --local new name` |
| Ceedling: Clean Project | `ceedling clean` |
| Ceedling: Clobber Project | `ceedling clobber` Removes all generated files including logs |
| Ceedling: Create New Module | `ceedling create:module name`|
| Ceedling: Destroy Current Module | Closes all views for test, source and header files associated with current file then calls `ceedling destroy:module name`|
| Ceedling: Open Module Header | Opens header for current module |
| Ceedling: Open Module Source | Opens source for current module |
| Ceedling: Open Module Test | Open test for current module |
| Ceedling: Open Next Module File | Cycle through header, source and test for current module |
| Ceedling: Open Module Files | Open test, source, header files for the currently active file in 2 column layout |
| Ceedling: Toggle Logging | Toggle current logging setting |
| Ceedling: Toggle Verbose | Toggle verbose output |
| Ceedling: Edit Project Configuration | Opens `project.yml` |
| Ceedling: Test Summary | Print summary of previously run tests |
| Ceedling: Version | Print version information for ceedling used in current project. |
| Ceedling: Environment | Display ENV variables set by ceedling |


### Key mappings

Note: key mappings are disabled by default.

| Key command | Function |
|:--|:--|
|`ctrl+super-h` | Open Header File |
|`ctrl+super-s` | Open Source File |
|`ctrl+super-t` | Open Test File |
|`ctrl+super-.` | Open Module Files in 2 column layout |
|`ctrl+super-right` | Cycle through module files |


To use these key mappings go to `Preferences » Package Settings » Ceedling » Key Bindings`. Copy the commented bindings from the left panel to the User `Default.sublime-keymap` on the right and uncomment by selecting then `Edit » Comments » Toggle Block Comments`.

See the [Key Bindings](https://www.sublimetext.com/docs/key_bindings.html) documetation for more information on setting key assignments.


## Snippets

Unity test snippets are now provided by the `Unity Test Completions` package.
The package provides 467 snippets covering 99.79% of Unity tests.

Unity Test Completions package can be installed using PackageControl.
- [Unity Test Completions](https://github.com/pajacobson/unity_test_completions)

