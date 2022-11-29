import re
import sublime
import sublime_plugin


class CeedlingFlags:
    Pending = 1
    NoMatch = 2


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

CEEDLING_ASSERT_COMMON = [
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

        if sublime.version().startswith("4"):
            self.flags = (
                sublime.DYNAMIC_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
            )
        else:
            self.flags = sublime.INHIBIT_WORD_COMPLETIONS

        self.parser = re.compile(
            "".join(
                [
                    r"(?:",
                    r"(?P<basic>^pa|fa|ig)|",
                    r"(?:((?P<bool>^a[tfu])|(?P<ptr>^an?[ne])))|",
                    r"(?:(?P<cmp1>[engl])(?P<cmp2>[eto])?)?",
                    r"(?:",
                    r"(?P<utype>sz|c|[uih])(?P<bits>(?<=[uih])(?:8|16|32|64))?|",
                    r"(?P<ntype>(?:(?<=e)[df])|(?:[df](?=[wind])))|",
                    r"(?P<stype>sl)|",
                    r"(?<=e)(?P<atype>p|s|m(?!s))",
                    r")?",
                    r"(?P<p4>a)?",
                    r"(?P<p5>w)?",
                    r")",
                    r"(?P<msg>ms$)?",
                ]
            )
        )

        self._matches_filtered = [
            {
                k: v[0].lower()
                for k, v in m.items()
                if k in ("cmp1", "cmp2", "p4", "p5")
            }
            for m in CEEDLING_ASSERT_COMMON
        ]

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

            result = self.completions(prefix)
            return result if result is None else (result, self.flags)

        else:
            return (TEST_FUNCTIONS, self.flags)

    def completions(self, prefix):

        r = self._completion_filter(prefix)

        if r is CeedlingFlags.NoMatch:
            return None

        elif r is CeedlingFlags.Pending:
            # return a empty placeholder to prevent
            # document matches overriding completions
            return [
                ["Ceedling: ambiguous match...", ""],
            ]

        types, matches = r.pop("types"), r.pop("matches")

        if not all((types, matches)):
            return []

        return [
            x
            for t, m in zip(types, matches)
            for x in self._generate_completions(t, m, **r)
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

        if len(prefix) == 1 and prefix in ("a", "p", "f", "i", "g", "l"):
            return CeedlingFlags.Pending

        tokens = self.parser.match(prefix)

        if not any(tokens.groups()):
            return CeedlingFlags.NoMatch

        tokens = tokens.groupdict()

        msg = True if tokens.pop("msg") else False

        if tokens.pop("basic"):
            return {
                "types": [{"": [""]}] * len(ASSERTIONS_BASIC),
                "matches": ASSERTIONS_BASIC.copy(),
                "msg": msg,
                "params": [""],
                "text": "",
            }

        elif tokens.pop("bool"):
            return {
                "types": [{"": [""]}] * len(ASSERTIONS_BOOL),
                "matches": ASSERTIONS_BOOL.copy(),
                "msg": msg,
                "params": ["condition"],
            }

        elif tokens.pop("ptr"):
            return {
                "types": [{"": [""]}] * len(ASSERTIONS_PTR),
                "matches": ASSERTIONS_PTR.copy(),
                "msg": msg,
                "params": ["pointer"],
            }

        match = CEEDLING_ASSERT_COMMON.copy()

        # check values from parser against
        # base assert definitions
        tokens_filtered = {
            k: v
            for k, v in tokens.items()
            if k in ("cmp1", "cmp2", "p4", "p5")
            if v is not None
        }

        c, p = [], []
        for i in self._matches_filtered:
            c.append(
                sum(
                    tokens_filtered.get(j, "token") == i.get(j, "match")
                    for j in ("cmp1", "cmp2")
                )
            )

            p.append(
                sum(
                    tokens_filtered.get(j, "token") == i.get(j, "match")
                    for j in ("p4", "p5")
                )
            )
        pairsums = [l + m for l, m in zip(c, p)]

        match = [
            m
            for t, m in zip([k == max(pairsums) for k in pairsums], match)
            if t is True
        ]

        if len(match) == 0:
            return None
        # If the request is valid one def should match.
        match_types = []

        for m in match:
            types = TYPES_INTEGER.copy()
            for t in m.get("extra", []):

                if t == "numeric":
                    types.update(TYPES_NUMERIC)
                elif t == "array":
                    types.update(TYPES_ARRAY)
                elif t == "struct":
                    types.update(TYPES_STRUCT_STRING)
            match_types.append(types)

        return {
            "types": match_types,
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

                trigger = " ".join(assert_text[1 if k == "" else 2 :]).lower()

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
