import uuid
import pprint
from typing import List, Dict, Set

from schemas import Symbols


class Nfa:
    states: Set[str]
    initial_state: str
    final_states: Set[str]
    transactions: Dict[str, Dict[str, Set[str]]]
    alphabets: Set[str]

    def __init__(
        self,
        states: Set[str],
        initial_state: str,
        final_states: Set[str],
        transactions: Dict[str, Dict[str, Set[str]]],
        alphabets: Set[str]
    ) -> None:
        self.states = states
        self.initial_state = initial_state
        self.final_states = final_states
        self.transactions = transactions
        self.alphabets = alphabets

    def __repr__(self) -> str:
        return pprint.pformat({
            "alphabets": self.alphabets,
            "states": self.states,
            "initial_state": self.initial_state,
            "final_states": self.final_states,
            "transactions": self.transactions
        })

    def normalize(self) -> None:
        states_table: Dict[str, str] = {}

        state_counter = 1
        new_states: Set[str] = set()
        new_final_states: Set[str] = set()
        new_initial_state: str = ''
        for state in self.states:
            new_state = f"{Symbols.STATE_NAME_PREFIX}{state_counter}"
            states_table[state] = new_state
            new_states.add(new_state)
            if state == self.initial_state:
                new_initial_state = new_state
            if state in self.final_states:
                new_final_states.add(new_state)
            state_counter += 1

        new_transactions: Dict[str, Dict[str, Set[str]]] = {}
        for state in self.transactions.keys():
            new_state = states_table[state]
            new_transactions[new_state] = {}
            for alphabet in self.transactions[state].keys():
                new_transactions[new_state][alphabet] = set()
                for transactions_state in self.transactions[state][alphabet]:
                    new_transactions[new_state][alphabet].add(states_table[transactions_state])

        self.states = new_states
        self.initial_state = new_initial_state
        self.final_states = new_final_states
        self.transactions = new_transactions

    @classmethod
    def init_nfa(cls, character: str) -> 'Nfa':
        initial_state = str(uuid.uuid4())
        final_state = str(uuid.uuid4())
        return cls(
            initial_state=initial_state,
            final_states={final_state},
            states={initial_state, final_state},
            transactions={initial_state: {character: {final_state}}},
            alphabets={character, Symbols.EPSILON}
        )

    @classmethod
    def concat_nfa(cls, nfa1: 'Nfa', nfa2: 'Nfa') -> 'Nfa':
        merge = False
        if len(nfa1.final_states) == 1:
            nfa1_final_state = list(nfa1.final_states)[0]
            nfa2.states.remove(nfa2.initial_state)
            nfa2.states.add(nfa1_final_state)

            transactions = nfa2.transactions.pop(nfa2.initial_state)
            nfa2.transactions[nfa1_final_state] = transactions

            for state in nfa2.states:
                for alphabet in nfa2.alphabets:
                    if nfa2.transactions.get(state) and nfa2.initial_state in nfa2.transactions[state].get(
                            alphabet, {}):
                        nfa2.transactions[state][alphabet].remove(nfa2.initial_state)
                        nfa2.transactions[state][alphabet].add(nfa1_final_state)

            nfa2.initial_state = nfa1_final_state
            merge = True

        nfa = cls(
            states=nfa1.states.union(nfa2.states),
            initial_state=nfa1.initial_state,
            final_states=nfa2.final_states,
            alphabets=nfa1.alphabets.union(nfa2.alphabets),
            transactions={}
        )

        for state in nfa.states:
            if state in nfa1.states and state in nfa2.states:
                transactions = {}
                for alphabet in nfa.alphabets:
                    nfa1_alphabet_transactions = nfa1.transactions[state].get(
                        alphabet, set()) if nfa1.transactions.get(state) else set()
                    nfa2_alphabet_transactions = nfa2.transactions[state].get(alphabet, set())
                    if nfa1_alphabet_transactions or nfa2_alphabet_transactions:
                        transactions[alphabet] = nfa1_alphabet_transactions.union(
                            nfa2_alphabet_transactions) if nfa2.transactions.get(state) else set()
                nfa.transactions[state] = transactions
            elif state in nfa1.states and nfa1.transactions.get(state):
                nfa.transactions[state] = nfa1.transactions[state]
            elif state in nfa2.states and nfa2.transactions.get(state):
                nfa.transactions[state] = nfa2.transactions[state]

        if not merge:
            for state in nfa1.final_states:
                nfa.transactions[state][Symbols.EPSILON].add(nfa2.initial_state)

        return nfa

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
