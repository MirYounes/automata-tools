class Symbols:
    UNION = '|'
    ZERO_OR_MORE = '*'
    ONE_OR_MORE = '+'
    ZERO_OR_ONE = '?'
    CONCAT = '.'

    PRIORITIES = {
        ZERO_OR_MORE: 3,
        ONE_OR_MORE: 3,
        ZERO_OR_ONE: 3,
        CONCAT: 2,
        UNION: 1,
    }

    OPEN_PARENTHESIS = '('
    CLOSE_PARENTHESIS = ')'

    @classmethod
    def is_alphabet(cls, char: str) -> bool:
        return char not in cls.PRIORITIES and char not in [cls.OPEN_PARENTHESIS, cls.CLOSE_PARENTHESIS]
