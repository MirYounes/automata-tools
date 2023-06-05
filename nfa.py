import uuid
import pprint
from typing import List, Dict, Set

from schemas import Symbols


class Nfa:
    states: Set[uuid.UUID]
    initial_state: uuid.UUID
    final_states: Set[uuid.UUID]
    transactions: Dict[uuid.UUID, Dict[str, Set[uuid.UUID]]]
    alphabets: Set[str]

    def __init__(
        self,
        states: Set[uuid.UUID],
        initial_state: uuid.UUID,
        final_states: Set[uuid.UUID],
        transactions: Dict[uuid.UUID, Dict[str, Set[uuid.UUID]]],
        alphabets: Set[str]
    ) -> None:
        self.states = states
        self.initial_state = initial_state
        self.final_states = final_states
        self.transactions = transactions
        self.alphabets = alphabets

    @classmethod
    def init_nfa(cls, character: str) -> 'Nfa':
        initial_state = uuid.uuid4()
        final_state = uuid.uuid4()
        return cls(
            initial_state=initial_state,
            final_states={final_state},
            states={initial_state, final_state},
            transactions={initial_state: {character: {final_state}}},
            alphabets={character}
        )

    def __repr__(self) -> str:
        return pprint.pformat({
            "alphabets": self.alphabets,
            "states": self.states,
            "initial_state": self.initial_state,
            "final_states": self.final_states,
            "transactions": self.transactions
        })

    @staticmethod
    def add_concat_symbol(regex: str) -> str:
        new_regex = ""
        for current_char in regex:
            if (len(new_regex) > 0):
                prev_char = new_regex[-1]
                if (
                    (prev_char in [Symbols.CLOSE_PARENTHESIS, Symbols.ZERO_OR_MORE,
                                   Symbols.ONE_OR_MORE, Symbols.ZERO_OR_ONE] or Symbols.is_alphabet(prev_char))
                    and (current_char == Symbols.OPEN_PARENTHESIS or Symbols.is_alphabet(current_char))
                ):
                    new_regex += Symbols.CONCAT
            new_regex += current_char
        return new_regex

    @classmethod
    def regex_to_postfix(cls, regex: str) -> str:
        postfix_regex = ""
        operator_stack: List[str] = []
        regex = cls.add_concat_symbol(regex=regex)

        for current_char in regex:
            if Symbols.is_alphabet(current_char):
                postfix_regex += current_char
            elif current_char == Symbols.OPEN_PARENTHESIS:
                operator_stack.append(current_char)
            elif current_char == Symbols.CLOSE_PARENTHESIS:
                top = operator_stack.pop()
                while top != Symbols.OPEN_PARENTHESIS:
                    postfix_regex += top
                    top = operator_stack.pop()
            else:
                if len(operator_stack) == 0:
                    operator_stack.append(current_char)
                else:
                    top = operator_stack[-1]
                    while (top != Symbols.OPEN_PARENTHESIS and Symbols.PRIORITIES[top]
                           >= Symbols.PRIORITIES[current_char]):
                        postfix_regex += top
                        operator_stack.pop()
                        if len(operator_stack) > 0:
                            top = operator_stack[-1]
                        else:
                            break
                    operator_stack.append(current_char)
        while len(operator_stack) != 0:
            postfix_regex += operator_stack.pop()

        return postfix_regex
