import re
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
    def __init__(self):

        pattern = "".join(
            [
                r"(?:(?P<basic>tp|tf|ti)?)?",
                r"(?:(?P<bool>at|af|aun|anu|ann|aem|ane)?)",
                r"(?:(?P<cmp1>[engl])(?P<cmp2>[eto])?)?",
                r"(?:",
                r"(?P<utype>[uihc]|sz)(?P<bits>(8|16|32|64)?)|",
                r"(?P<stype>sl)|",
                r"(?P<atype>p|s|m(?!s))|",
                r"(?P<ntype>d|f)",
                r")?",
                r"(?:(?P<array>a)?)?",
                r"(?:(?P<within>w)?)?",
                r"(?:(?P<msg>ms$))?",
            ]
        )

        self.pattern = re.compile(pattern)

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
    def _num_filter(self, match, key):
        return [i for i in match if key in i.get("extra", "")]

    def _type_filter(self, type_dict, key):
        return {
            i: t
            for i, t in type_dict.items()
            if i.lower().startswith(key[0].lower())
        }

    def _match_filter(self, match, token, key):
        return [
            match[i]
            for i, a in enumerate(match)
            if token == a.get(key, "-")[0].lower()
        ]

    def _completion_filter(self, prefix):

        tokens = self.pattern.match(prefix)

        if not any(tokens.groups()):
            return None, None, None

        tokens = tokens.groupdict()
        print(tokens)
        if tokens.get("basic"):
            print("Basic Fail Pass")
            return None, None, None

        if tokens.get("bool"):
            print("Boolean")
            return None, None, None

        match = ASSERTIONS_COMMON.copy()
        types = TYPES_INTEGER.copy()

        if tokens.get("cmp1") is not None:
            match = self._match_filter(match, tokens.get("cmp1"), "cmp1")

        if tokens.get("cmp2"):
            match = self._match_filter(match, tokens.get("cmp2"), "cmp2")

        elif any(
            (
                tokens.get("ntype"),
                tokens.get("utype"),
                tokens.get("atype"),
                tokens.get("stype"),
                tokens.get("array"),
                tokens.get("within"),
            )
        ):
            match = [i for i in match if not i.get("cmp2")]

        if tokens.get("array"):
            match = self._match_filter(match, tokens.get("array"), "p4")

            if not tokens.get("within"):
                match = [i for i in match if not i.get("p5")]

        if tokens.get("within"):

            match = self._match_filter(match, tokens.get("within"), "p5")
            if not tokens.get("array"):
                match = [i for i in match if not i.get("p4")]

        if tokens.get("ntype"):

            match = self._num_filter(match, "numeric")
            types = self._type_filter(TYPES_NUMERIC, tokens.get("ntype"))

        elif tokens.get("atype"):

            match = self._num_filter(match, "array")
            types = self._type_filter(TYPES_ARRAY, tokens.get("atype"))

        elif tokens.get("stype"):

            match = self._num_filter(match, "struct")
            types = self._type_filter(TYPES_STRUCT_STRING, tokens.get("stype"))

        elif tokens.get("utype"):
            types = self._type_filter(types, tokens.get("utype"))

            if tokens.get("bits"):
                bit_value = tokens.get("bits")
                for k, v in types.items():
                    if bit_value in v:
                        types[k] = [bit_value]

        return types, match, True if tokens.get("msg") else False

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
                        "TEST",
                        "ASSERT",
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

                trigger = " ".join(assert_text[1:]).lower()

                content = "_".join(assert_text)
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
