import sublime
import sublime_plugin

TEST_FUNCTIONS = [
    [
        "test\tskeleton test",
        "void test_${1:function}_should_${2:behavior}(void)\n{\n\t${3}\n}\n",
    ],
    [
        "testf\tskeleton test fail",
        'void test_${1:function}_should_${2:behavior}(void)\n{\n\tTEST_FAIL_MESSAGE("${3:Implement me!}");\n}\n',
    ],
    [
        "testi\tskeleton test ignore",
        'void test_${1:function}_should_${2:behavior}(void)\n{\n\tTEST_IGNORE_MESSAGE("${3:Implement me!}");\n}\n',
    ],
]

TEST_ASSERTIONS_MSG = [
    [
        "test fail message",
        'TEST_FAIL("${1:message}");',
    ],
    [
        "test pass message",
        'TEST_PASS("${1:message}");',
    ],
    [
        "test ignore message",
        'TEST_IGNORE("${1:message}");',
    ],
    [
        "test message",
        'TEST_MESSAGE("${1:message}");',
    ],
    [
        "test assert message",
        'TEST_ASSERT_MESSAGE( ${1:condition}, "${2:message}");',
    ],
    [
        "test assert true message",
        'TEST_ASSERT_TRUE_MESSAGE(${1:condition, "${2:message}"});',
    ],
    [
        "test assert false message",
        'TEST_ASSERT_FALSE_MESSAGE(${1:condition}, "${2:message}");',
    ],
    [
        "test assert unless message",
        'TEST_ASSERT_UNLESS_MESSAGE(${1:condition}, "${2:message}");',
    ],
    [
        "test assert null message",
        'TEST_ASSERT_NULL_MESSAGE(${1:pointer}, "${2:message}");',
    ],
    [
        "test assert empty message",
        "TEST_ASSERT_EMPTY_MESSAGE(${1:pointer}, '${2:message}');",
    ],
    [
        "test assert not empty message",
        "TEST_ASSERT_NOT_EMPTY_MESSAGE(${1:pointer}, '${2:message}');",
    ],
    [
        "test assert equal int message",
        "TEST_ASSERT_EQUAL_INT_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert equal int8 message",
        "TEST_ASSERT_EQUAL_INT8_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert equal int16 message",
        "TEST_ASSERT_EQUAL_INT16_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert equal int32 message",
        "TEST_ASSERT_EQUAL_INT32_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert equal int64 message",
        "TEST_ASSERT_EQUAL_INT64_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert equal uint message",
        "TEST_ASSERT_EQUAL_UINT_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert equal uint8 message",
        "TEST_ASSERT_EQUAL_UINT8_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert equal uint16 message",
        "TEST_ASSERT_EQUAL_UINT16_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert equal uint32 message",
        "TEST_ASSERT_EQUAL_UINT32_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert equal uint64 message",
        "TEST_ASSERT_EQUAL_UINT64_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert equal HEX message",
        "TEST_ASSERT_EQUAL_HEX_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert equal HEX8 message",
        "TEST_ASSERT_EQUAL_HEX8_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert equal HEX16 message",
        "TEST_ASSERT_EQUAL_HEX16_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert equal HEX32 message",
        "TEST_ASSERT_EQUAL_HEX32_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert equal HEX64 message",
        "TEST_ASSERT_EQUAL_HEX64_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert equal char message",
        "TEST_ASSERT_EQUAL_CHAR_MESSAGE(${1:expected}, ${2:actual}, '${3:message}');",
    ],
    [
        "test assert bits message",
        "TEST_ASSERT_BITS_MESSAGE(${1:mask}, ${2:expected}, ${3:actual}, '${4:message}')",
    ],
    [
        "test assert bits high message",
        "TEST_ASSERT_BITS_HIGH_MESSAGE(${1:mask}, ${2:actual}, '${3:message}')",
    ],
    [
        "test assert bits low message",
        "TEST_ASSERT_BITS_LOW_MESSAGE(${1:mask}, ${2:actual}, '${3:message}')",
    ],
    [
        "test assert bit high message",
        "TEST_ASSERT_BIT_HIGH_MESSAGE(${1:bit}, ${2:actual}, '${3:message}')",
    ],
    [
        "test assert bit low message",
        "TEST_ASSERT_BIT_LOW_MESSAGE(${1:bit}, ${2:actual}, '${3:message}')",
    ],
]

TEST_ASSERTIONS = [
    [
        "test fail",
        "TEST_FAIL()",
    ],
    [
        "test pass",
        "TEST_PASS()",
    ],
    [
        "test ignore",
        "TEST_IGNORE()",
    ],
    [
        "test assert",
        "TEST_ASSERT( ${1:condition});",
    ],
    [
        "test assert true",
        "TEST_ASSERT_TRUE(${1:condition});",
    ],
    [
        "test assert false",
        "TEST_ASSERT_FALSE(${1:condition});",
    ],
    [
        "test assert unless",
        "TEST_ASSERT_UNLESS(${1:condition});",
    ],
    [
        "test assert null",
        "TEST_ASSERT_NULL(${1:pointer});",
    ],
    [
        "test assert empty",
        "TEST_ASSERT_EMPTY(${1:pointer});",
    ],
    [
        "test assert not empty",
        "TEST_ASSERT_NOT_EMPTY(${1:pointer});",
    ],
    [
        "test assert equal int",
        "TEST_ASSERT_EQUAL_INT(${1:expected}, ${2:actual});",
    ],
    [
        "test assert equal int8",
        "TEST_ASSERT_EQUAL_INT8(${1:expected}, ${2:actual});",
    ],
    [
        "test assert equal int16",
        "TEST_ASSERT_EQUAL_INT16(${1:expected}, ${2:actual});",
    ],
    [
        "test assert equal int32",
        "TEST_ASSERT_EQUAL_INT32(${1:expected}, ${2:actual});",
    ],
    [
        "test assert equal int64",
        "TEST_ASSERT_EQUAL_INT64(${1:expected}, ${2:actual});",
    ],
    [
        "test assert equal uint",
        "TEST_ASSERT_EQUAL_UINT(${1:expected}, ${2:actual});",
    ],
    [
        "test assert equal uint8",
        "TEST_ASSERT_EQUAL_UINT8(${1:expected}, ${2:actual});",
    ],
    [
        "test assert equal uint16",
        "TEST_ASSERT_EQUAL_UINT16(${1:expected}, ${2:actual});",
    ],
    [
        "test assert equal uint32",
        "TEST_ASSERT_EQUAL_UINT32(${1:expected}, ${2:actual});",
    ],
    [
        "test assert equal uint64",
        "TEST_ASSERT_EQUAL_UINT64(${1:expected}, ${2:actual});",
    ],
    [
        "test assert equal HEX",
        "TEST_ASSERT_EQUAL_HEX(${1:expected}, ${2:actual});",
    ],
    [
        "test assert equal HEX8",
        "TEST_ASSERT_EQUAL_HEX8(${1:expected}, ${2:actual});",
    ],
    [
        "test assert equal HEX16",
        "TEST_ASSERT_EQUAL_HEX16(${1:expected}, ${2:actual});",
    ],
    [
        "test assert equal HEX32",
        "TEST_ASSERT_EQUAL_HEX32(${1:expected}, ${2:actual});",
    ],
    [
        "test assert equal HEX64",
        "TEST_ASSERT_EQUAL_HEX64(${1:expected}, ${2:actual});",
    ],
    [
        "test assert equal char",
        "TEST_ASSERT_EQUAL_CHAR(${1:expected}, ${2:actual});",
    ],
    [
        "test assert bits",
        "TEST_ASSERT_BITS(${1:mask}, ${2:expected}, ${3:actual})",
    ],
    [
        "test assert bits high",
        "TEST_ASSERT_BITS_HIGH(${1:mask}, ${2:actual})",
    ],
    [
        "test assert bits low",
        "TEST_ASSERT_BITS_LOW(${1:mask}, ${2:actual})",
    ],
    [
        "test assert bit high",
        "TEST_ASSERT_BIT_HIGH(${1:bit}, ${2:actual})",
    ],
    [
        "test assert bit low",
        "TEST_ASSERT_BIT_LOW(${1:bit}, ${2:actual})",
    ],
]


class CeedlingCompletions(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if not any(
            view.match_selector(caret, "(source.c | source.c++ | source.c99)")
            for caret in locations
        ):
            return None

        # Autocomplete if unity.h has been included
        if not any(
            "unity.h" in view.substr(region)
            for region in view.find_by_selector(
                "(string.quoted.double.include.c | string.quoted.double.include.c++)"
            )
        ):
            return None

        if all(
            view.match_selector(caret, "meta.function & meta.block")
            for caret in locations
        ):
            if prefix.endswith("me"):
                return (
                    TEST_ASSERTIONS_MSG,
                    sublime.INHIBIT_WORD_COMPLETIONS
                    | sublime.INHIBIT_EXPLICIT_COMPLETIONS,
                )
            else:
                return (
                    TEST_ASSERTIONS,
                    sublime.INHIBIT_WORD_COMPLETIONS
                    | sublime.INHIBIT_EXPLICIT_COMPLETIONS,
                )

        else:
            return (
                TEST_FUNCTIONS,
                sublime.INHIBIT_WORD_COMPLETIONS
                | sublime.INHIBIT_EXPLICIT_COMPLETIONS,
            )
