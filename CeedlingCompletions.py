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
        'void test_${1:function}_should_${2:behavior}(void)\n{\n\tTEST_FAIL_MESSAGE ("${3:Implement me!}");\n}\n',
    ],
    [
        "testi\ttemplate test ignore",
        'void test_${1:function}_should_${2:behavior}(void)\n{\n\tTEST_IGNORE_MESSAGE ("${3:Implement me!}");\n}\n',
    ],
]


# Base tyoes used
TYPES_INTEGER = {
    "INT": ["", "8", "16", "32", "64"],
    "UINT": ["", "8", "16", "32", "64"],
    "size_t": [""],
    "HEX": ["", "8", "16", "32", "64"],
    "CHAR": [""],
}

TYPES_NUMERIC = {
    "FLOAT": [""],
    "DOUBLE": [""],
}

TYPES_ARRAY = {
    "PTR": [""],
    "STRING": [""],
    "MEMORY": [""],
}

TYPES_STRUCT_STRING = {
    "STRING_LEN": [""],
}

ASSERTIONS_BASIC = [
    {"cmp3": "FAIL"},
    {"cmp3": "IGNORE"},
    {"cmp3": "ONLY"},
    {"cmp3": "PASS"},
]

ASSERTIONS_BOOL = [
    {"cmp3": "TRUE"},
    {"cmp3": "UNLESS"},
    {"cmp3": "FALSE"},
]

ASSERTIONS_PTR = [
    {
        "cmp2": "NULL",
    },
    {
        "cmp2": "NOT",
        "cmp3": "NULL",
    },
    {
        "cmp2": "EMPTY",
    },
    {
        "cmp2": "NOT",
        "cmp3": "EMPTY",
    },
]

ASSERTIONS_COMMON = [
    {
        "cmp1": "EQUAL",
        "extra": ["numeric", "array", "struct"],
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
        "extra": ["numeric"],
    },
    {
        "p4": "ARRAY",
        "p5": "WITHIN",
    },
    {
        "cmp1": "EQUAL",
        "p4": "ARRAY",
        "extra": ["array", "numeric"],
    },
    {
        "cmp1": "EACH",
        "cmp2": "EQUAL",
        "extra": ["array", "numeric"],
    },
]


class CeedlingCompletions(sublime_plugin.EventListener):

    pattern = None

    def __init__(self):

        self.parser = re.compile(
            "".join(
                [
                    r"(",
                    r"(?:(?P<basic>^pa|^fa|^ig))|",
                    r"(?:(?P<simple>^a(?=ms)|(^a((?P<bool>[tfu])|(?P<ptr>n?[ne])))))|",
                    r"(?:(?P<cmp1>[engl])(?P<cmp2>[eto])?)?",
                    r"(?:",
                    r"(?P<utype>([uihc]|sz))(?P<bits>(8|16|32|64)?)|",
                    r"(?P<stype>sl)|",
                    r"(?P<atype>p|s|m(?!s))|",
                    r"(?P<ntype>d|f)",
                    r")?",
                    r"(?:(?P<array>a)?)?",
                    r"(?:(?P<within>w)?)?",
                    r")",
                    r"(?:(?P<msg>ms$))?",
                ]
            )
        )

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
            return (
                self.completions(prefix),
                sublime.INHIBIT_WORD_COMPLETIONS | sublime.DYNAMIC_COMPLETIONS,
            )

        else:
            return (TEST_FUNCTIONS, sublime.INHIBIT_WORD_COMPLETIONS)

    def completions(self, prefix):

        r = self._completion_filter(prefix)
        types, matches = r.pop("types"), r.pop("matches")

        if not all((types, matches)):
            return []

        return [
            x
            for m in matches
            for x in self._generate_completions(types, m, **r)
        ]

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

        tokens = self.parser.match(prefix)

        if not any(tokens.groups()):
            return {
                "types": None,
                "matches": None,
                "msg": False,
            }

        tokens = tokens.groupdict()

        msg = True if tokens.pop("msg") else False

        if tokens.get("basic"):
            return {
                "types": {"": [""]},
                "matches": ASSERTIONS_BASIC.copy(),
                "msg": msg,
                "params": [""],
                "text": "",
            }

        elif tokens.get("simple"):

            if tokens.get("bool"):
                p = ["condition"]
                m = ASSERTIONS_BOOL.copy()

            elif tokens.get("ptr"):
                p = ["pointer"]
                m = ASSERTIONS_PTR.copy()

            else:
                m = {"": [""]}
                p = ["condition"]

            return {
                "types": {"": [""]},
                "matches": m,
                "msg": msg,
                "params": p,
            }

        match = ASSERTIONS_COMMON.copy()
        types = TYPES_INTEGER.copy()

        cmp1 = tokens.pop("cmp1")
        cmp2 = tokens.pop("cmp2")

        if cmp1 is not None:
            match = self._match_filter(match, cmp1, "cmp1")

        if cmp2:
            match = self._match_filter(match, cmp2, "cmp2")

        elif any(tokens.values()):
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

        return {
            "types": types,
            "matches": match,
            "msg": msg,
        }

    def _generate_completions(
        self,
        types,
        definition,
        msg=False,
        text="ASSERT",
        params=["expected", "actual"],
    ):
        """Return list of trigger:content pairs."""
        result = []
        message = "MESSAGE" if msg else ""
        param = params[:]

        if definition.get("cmp1") in ("NOT", "GREATER", "LESS"):
            param[0] = "threshold"

        if definition.get("p4") or definition.get("cmp1") == "EACH":
            param.append("num_elements")

        if definition.get("p5"):
            param.insert(0, "delta")

        for k, v in types.items():
            p = param[:]

            if "threshold" in p and k == "HEX":
                try:
                    v.remove("")
                except ValueError:
                    pass

            if k in ("STRING_LEN", "MEMORY"):
                p.insert(2, "len")

            for val in v:

                assert_text = [
                    w
                    for w in (
                        "TEST",
                        "{}".format(text),
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

                p_out = []

                if p[0] != "":
                    p_out.extend(
                        "${{{}:{}}}".format(i, d) for i, d in enumerate(p, 1)
                    )

                if msg:
                    p_out.append('"${{{}:message}}"'.format(len(p_out) + 1))

                content += ", ".join(p_out)
                content += ");"
                result.append([trigger, content])

        return result
