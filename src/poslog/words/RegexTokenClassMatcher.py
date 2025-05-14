from enum import Enum
from re import Pattern
import re

class TokenClass(Enum):
    NUMBER = 'Number'
    IDENTIFIER = 'Identifier'
    KEY_VALUE_PAIR = 'KeyValuePair'
    DATE_TIME = 'DateTime'
    # Location, Path, Socket, IP, URL
    LOCATION = 'Location'
    VARIABLE = 'Variable'
    SYMBOL = 'Symbol'
    PUNCTUATION = 'Punctuation'
    MISC = 'Misc'
    UNKNOWN = 'Unknown'


class _RegexPatternEntry():
    def __init__(self, pattern: str, token_class: TokenClass, description: str):
        self.pattern: Pattern = re.compile(pattern)
        self.token_class: TokenClass = token_class
        self.description: str = description

class RegexTokenClassMatcher:

    def __init__(self):
        self.regex_list: list[_RegexPatternEntry] = self._fill_regex_list()
 
 
    def token_classes(self, tokens: list[str]) -> list[TokenClass]:
        return [self.token_class(token) for token in tokens]

    def token_class(self, token: str) -> TokenClass:
        token_class=TokenClass.UNKNOWN
        for rmp in self.regex_list:
            if rmp.pattern.fullmatch(token):
                token_class=rmp.token_class #(rmp.token_class, rmp.description)
                break
        return token_class


    ######################
    # Regex List
    ######################

    def _fill_regex_list(self) -> list[_RegexPatternEntry]:
        regex_list: list[_RegexPatternEntry] = []

        # try casting number into float should be done in KnownWordsDetector already
        # Numbers
        # e.g. '123', '123.45', '-123.45', '1e.0', '1e-0'
        # This is done by test for float instead
        # regex_list.append(
        #     RegexMaskPattern(
        #         r'-?\d+(\.\d+)?([eE]-?\d+)?',
        #         RegexMaskPattern.T_mask.NUMBER,
        #         'Numbers'
        #     ))

        # key value pairs
        regex_list.append(_RegexPatternEntry(
            r'\w+=\w+',
            TokenClass.KEY_VALUE_PAIR,
            'key-value-pairs simple'
        ))
        regex_list.append(_RegexPatternEntry(
            r'[^=]+=[^=]+',
            TokenClass.KEY_VALUE_PAIR,
            'key-value-pairs greedy'
        ))

        # TODO Note, these two will even match e.g. "=x" and "x="
        # unclean key-value pairs
        # if contains only one '='
        regex_list.append(_RegexPatternEntry(
            r'^[^=]*=[^=]+$',
            TokenClass.KEY_VALUE_PAIR,
            'key-value-pairs incomplete left'
        ))
        regex_list.append(_RegexPatternEntry(
            r'^[^=]+=[^=]*$',
            TokenClass.KEY_VALUE_PAIR,
            'key-value-pairs incomplete right'
        ))

        # multiple key-value pairs
        # comma separated

        regex_list.append(
            _RegexPatternEntry(
                r'[^=]+=[^=]+(,[^=]+=[^=]+)+',
                TokenClass.KEY_VALUE_PAIR,
                'key-value-pairs comma-separated'
            ))
        # Version numbers
        # v0.100', 'v0.97', 'v6.1.7601.23505',
        regex_list.append(
            _RegexPatternEntry(
                r'v\.?\d+(\.\d+[a-z]?)+',
                TokenClass.IDENTIFIER,
                'version numbers'
            ))

        # UUID
        # e.g. '12345678-1234-5678-1234-567812345678'
        regex_list.append(
            _RegexPatternEntry(
                r'[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}',
                TokenClass.IDENTIFIER,
                'UUID'
            ))

        # Hexadecimal numbers
        regex_list.append(
            _RegexPatternEntry(
                r'0x[0-9a-fA-F]+',
                TokenClass.NUMBER,
                'hexadecimal numbers prefixed'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'[0-9a-fA-F]{8}',
                TokenClass.NUMBER,
                'hexadecimal numbers without prefix, 8 digits'
            ))

        # Sockets
        regex_list.append(
            _RegexPatternEntry(
                r'(\d{1,3}\.){3}\d{1,3}:\d+',
                TokenClass.LOCATION,
                'sockets (ip+port)'
            ))

        # IP addresses
        regex_list.append(
            _RegexPatternEntry(
                r'(\d{1,3}\.){3}\d{1,3}',
                TokenClass.LOCATION,
                'IP addresses'
            ))

        # MAC-Addresses
        regex_list.append(
            _RegexPatternEntry(
                r'([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}',
                TokenClass.IDENTIFIER,
                'MAC addresses'
            ))

        # Filenames
        import mimetypes
        # len(mimetypes.types_map) #1032
        common_file_extensions = '|'.join(
            [k[1:] for k in mimetypes.types_map.keys()])

        regex_list.append(
            _RegexPatternEntry(
                r'[^\./\\]+\.('+common_file_extensions+')',
                TokenClass.LOCATION,
                'file names'
            ))

        # TODO Here are some sockets that begins with slash ;/

        # Pathes

        regex_list.append(
            _RegexPatternEntry(
                r'(/[^/ ]*)+/?',
                TokenClass.LOCATION,
                'Linux paths'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'([a-zA-Z]:)?(\\[^\\ ]*)+\\{,2}',
                TokenClass.LOCATION,
                'Windows paths'
            ))

        # TODO: This matches packages, pathes and filenames also

        # regex from: https://stackoverflow.com/questions/3809401/what-is-a-good-regular-expression-to-match-a-url
        # url_regex=re.compile(r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
        # url_regex=re.compile(r'([a-zA-Z]+://)?[a-zA-Z0-9\.-]+\.[a-zA-Z]{2,6}(:[0-9]{1,5})?(/.*)?')
        regex_list.append(
            _RegexPatternEntry(
                # r'([a-zA-Z]+://)?[a-zA-Z0-9][a-zA-Z0-9\.-]*\.[a-zA-Z]+[a-zA-Z0-9]+(:[0-9]{1,5})?(/.*)?',
                # Assumption: Most likely url contain only lowercase letters
                r'([a-zA-Z]+://)?[a-z0-9][a-zA-Z0-9\.-]*\.[a-zA-Z]+[a-zA-Z0-9]+(:[0-9]{1,5})?(/.*)?',
                TokenClass.LOCATION,
                'URLs'
            ))
        # Leftover packages

        # url with lower AND uppercase? AND underscore

        # OR? Combine urls and packages as LocationUrlOrPackage ?

        # TODO

        # Times
        # 2016/9/27:20:40:54.787
        regex_list.append(
            _RegexPatternEntry(
                r'\d{4}/\d{1,2}/\d{1,2}:\d{1,2}:\d{2}:\d{2}.\d+',
                TokenClass.DATE_TIME,
                'date-times slash'
            ))

        # 2017-07-03_13,48,39.308188
        regex_list.append(
            _RegexPatternEntry(
                r'\d{4}-\d{1,2}-\d{1,2}_\d{1,2},\d{2},\d{2}.\d+',
                TokenClass.DATE_TIME,
                'date-times dash milliseconds'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'\d{4}-\d{1,2}-\d{1,2}_\d{1,2},\d{2},\d{2}',
                TokenClass.DATE_TIME,
                'date-times dash seconds'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'\d{4}-\d{1,2}-\d{1,2}',
                TokenClass.DATE_TIME,
                'dates dash'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'\d{4}/\d{1,2}/\d{1,2}',
                TokenClass.DATE_TIME,
                'dates slash'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'\d{1,2}:\d{2}:\d{2}.\d+',
                TokenClass.DATE_TIME,
                'times float seconds'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'\d{1,2}:\d{2}:\d{2}',
                TokenClass.DATE_TIME,
                'times seconds'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'\d{1,2}:\d{2}',
                TokenClass.DATE_TIME,
                'times minutes'
            ))

        # TODO: Find unix timestamps as integer of a specific interval BEFORE numbers are matched

        # Now it's getting blurred

        # Look like normal words "Hello"
        regex_list.append(
            _RegexPatternEntry(
                r'[A-Z][a-z]+',
                TokenClass.VARIABLE,
                'words leading uppercase'
            ))

        # only uppercase words
        regex_list.append(
            _RegexPatternEntry(
                r'[A-Z]+',
                TokenClass.VARIABLE,
                'uppercase words'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'[a-z]+',
                TokenClass.VARIABLE,
                'lowercase words'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'[a-zA-Z]+\d+',
                TokenClass.VARIABLE,
                'words with trailing digits'
            ))

        # camelCase words

        regex_list.append(
            _RegexPatternEntry(
                r'[a-zA-Z]+([A-Z][a-z]+)+',
                TokenClass.VARIABLE,
                'camelCase words'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'[a-zA-Z]+([A-Z][a-z]+)+\d+',
                TokenClass.VARIABLE,
                'camelCase words with trailing digits'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'_+[a-zA-Z]+([A-Z][a-z]+)+',
                TokenClass.VARIABLE,
                'camelCase words with leading underscore'
            ))

        # snake_case (underscore separated) words

        regex_list.append(
            _RegexPatternEntry(
                r'[a-z]+(_[a-z]+)+',
                TokenClass.VARIABLE,
                'snake_case words'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'[a-z]+(_[a-z]+)+\d+',
                TokenClass.VARIABLE,
                'snake_case words with trailing digits'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'_+[a-z]+(_[a-z]+)+',
                TokenClass.VARIABLE,
                'snake_case words with leading underscore'
            ))

        # kebap (dash separated) words

        regex_list.append(
            _RegexPatternEntry(
                r'[a-z]+(-[a-z]+)+',
                TokenClass.VARIABLE,
                'kebap words only lowercase'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'[a-zA-Z]+(-[a-zA-Z]+)+',
                TokenClass.VARIABLE,
                'kebap words (lower and uppercase)'
            ))

        # words with underscore, digits and camelCase
        # job_1445144423722_0020Job
        regex_list.append(
            _RegexPatternEntry(
                r'[a-z]+[a-zA-Z0-9_-]+',
                TokenClass.VARIABLE,
                'mixed leading lowercase'
            ))

        regex_list.append(
            _RegexPatternEntry(
                r'[A-Z]+[a-zA-Z0-9_-]+',
                TokenClass.VARIABLE,
                'mixed leading uppercase'
            ))

        # more key-value with colon BUT word characters on the left

        regex_list.append(
            _RegexPatternEntry(
                r'(\w+):[^:]+',
                TokenClass.KEY_VALUE_PAIR,
                'key-value-pairs with colon'
            ))
        # unit values
        # 2.5MB, 2.5MB/s, 1024Kbytes, 3.60GHz, 300ms

        regex_list.append(
            _RegexPatternEntry(
                r'\d+(\.\d+)?[a-zA-Z/]+',
                TokenClass.NUMBER,
                'unit values'
            ))
        # Version number without 'v' prefix, but at least two dots, since numbers are already covered
        # Note: After numbers AND ip addresses AND units

        regex_list.append(
            _RegexPatternEntry(
                r'\d+(\.\d+[a-z]?)+',
                TokenClass.IDENTIFIER,
                'version numbers without v'
            ))
        # collect leftover hex-values
        # Numbers and words are already covered

        regex_list.append(
            _RegexPatternEntry(
                r'[0-9a-fA-F]+',
                TokenClass.NUMBER,
                'hexadecimal numbers leftover'
            ))
        
        # hex-values with seperators 
        # 00:06:6a:00:01:00:02:15 
        regex_list.append(
            _RegexPatternEntry(
                r'([0-9a-fA-F]{2}:)+[0-9a-fA-F]{2}',
                TokenClass.NUMBER,
                'hexadecimal numbers leftover with colons'
            ))


        # punctuation
        #import string
        #string.punctuation
        #!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
        # These punctuation mess up SYM and PUNCT, so they were separated
        
        punct_chars=re.escape(r""".,;:!?()[]{}_…“”‘’"'/\|·«»`~¿¡•""")
        
        regex_list.append(
            _RegexPatternEntry(
                r'['+punct_chars+']',
                TokenClass.PUNCTUATION,
                'single punctuation'
            ))

        # multiple punctuation
        regex_list.append(
            _RegexPatternEntry(
                r'['+punct_chars+']+',
                TokenClass.PUNCTUATION,
                'multiple punctuation'
            ))
        
        # symbols
        sym_chars=re.escape(r"""+-=*^%$&§¤#@<>©®™°±×÷√∞∑∏∫∆µπΩ≠≈∈∩∪⊂⊃∅∇⊕⊗⇒⇔""")
        regex_list.append(
            _RegexPatternEntry(
                r'['+sym_chars+']',
                TokenClass.SYMBOL,
                'single symbol'
            ))
        # multiple symbols
        regex_list.append(
            _RegexPatternEntry(
                r'['+sym_chars+']+',
                TokenClass.SYMBOL,
                'multiple symbols'
            ))

        return regex_list

