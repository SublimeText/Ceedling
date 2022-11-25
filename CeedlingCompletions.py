import sublime
import sublime_plugin

TEST_FUNCTIONS = [
    [
        "test\ttemplate test",
        "void test_${1:function}_should_${2:behavior}(void)\n{\n\t${3}\n}\n",
    ],
    [
        "testf\ttemplate test fail",
        'void test_${1:function}_should_${2:behavior}(void)\n{\n\tTEST_FAIL_MESSAGE("${3:Implement me!}");\n}\n',
    ],
    [
        "testi\ttest ignore",
        'void test_${1:function}_should_${2:behavior}(void)\n{\n\tTEST_IGNORE_MESSAGE("${3:Implement me!}");\n}\n',
    ],
]

TYPES_INTEGER = {
    "INT": ["", "8", "16", "32", "64"],
    "UINT": ["", "8", "16", "32", "64"],
    "size_t": [""],
    "HEX": ["", "8", "16", "32", "64"],
    "CHAR": [""],
}

TYPES_ARRAY = {
    "PTR": [""],
    "STRING": [""],
    "MEMORY": [""],
}

ASSERTIONS_COMMON = [
    {
        "cmp1": "EQUAL",
        "extra": TYPES_ARRAY,
    },
    {
        "cmp1": "NOT",
        "cmp2": "EQUAL",
    },
    {
        "cmp1": "GREATER",
        "cmp2": "THAN",
    },
    {
        "cmp1": "LESS",
        "cmp2": "THAN",
    },
    {
        "cmp1": "GREATER",
        "cmp2": "OR",
        "cmp3": "EQUAL",
    },
    {
        "cmp1": "LESS",
        "cmp2": "OR",
        "cmp3": "EQUAL",
    },
    {
        "p5": "WITHIN",
    },
    {
        "p4": "ARRAY",
        "p5": "WITHIN",
    },
    {
        "cmp1": "EQUAL",
        "p4": "ARRAY",
    },
    {
        "cmp1": "EACH",
        "cmp2": "EQUAL",
    },
]


class CeedlingCompletions(sublime_plugin.EventListener):
    _cache = {}

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

        if view.match_selector(locations[0], "meta.function & meta.block"):
            print(prefix)
            if prefix.endswith("ms"):
                print("msg detect")
                return (
                    self.completions(msg=True),
                    sublime.INHIBIT_WORD_COMPLETIONS
                    | sublime.DYNAMIC_COMPLETIONS,
                )
            else:
                return (
                    self.completions(),
                    sublime.INHIBIT_WORD_COMPLETIONS
                    | sublime.DYNAMIC_COMPLETIONS,
                )

        else:
            return (
                TEST_FUNCTIONS,
                sublime.INHIBIT_WORD_COMPLETIONS
                | sublime.INHIBIT_EXPLICIT_COMPLETIONS,
            )

    def completions(self, msg=False):
        k = "msg" if msg else "nomsg"

        if k in self._cache.keys():
            print("cached", k)
            return self._cache[k]

        self._cache[k] = [
            y
            for x in (
                self._generate_completions(TYPES_INTEGER, assert_def, msg=msg)
                for assert_def in ASSERTIONS_COMMON
            )
            for y in x
        ]

        return self._cache[k]

    def _generate_completions(self, types, definition, msg=False):
        """Return list of trigger:content pairs."""
        message = "MESSAGE" if msg else ""
        result = []
        base_p = ["expected", "actual"]

        types = types.copy()
        types.update(definition.get("extra", {}))

        if definition.get("cmp1") in ("NOT", "GREATER", "LESS"):
            base_p[0] = "threshold"

        if "WITHIN" == definition.get("p5", ""):
            base_p.insert(0, "delta")

        elif "ARRAY" == definition.get("p4", ""):
            base_p.append("num_elements")

        for k, v in types.items():
            p = base_p[:]

            if p[0] == "threshold" and k == "HEX":
                v = v[1:]

            if k in ("STRING_LEN", "MEMORY"):
                p.insert(2, "len")

            for val in v:

                assert_text = [
                    w
                    for w in (
                        "test",
                        "assert",
                        "{}".format(definition.get("cmp1", "")),
                        "{}".format(definition.get("cmp2", "")),
                        "{}".format(definition.get("cmp3", "")),
                        "{}{}".format(k, val),
                        "{}".format(definition.get("p4", "")),
                        "{}".format(definition.get("p5", "")),
                        "{}".format(message),
                    )
                    if w != ""
                ]

                trigger = " ".join(assert_text[2:]).lower()

                content = "_".join(assert_text).upper()
                content += " ("

                params = [
                    "${{{}:{}}}".format(i, d) for i, d in enumerate(p, 1)
                ]

                if msg:
                    params.append('"${{{}:message}}"'.format(len(params) + 1))

                content += ", ".join(params)
                content += ");"
                result.append([trigger, content])

        return result
