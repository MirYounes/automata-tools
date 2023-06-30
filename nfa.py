import uuid
from typing import List, Dict, Set, Optional

from schemas import Symbols
from utils import merge_dict
from fa import Fa


class Nfa(Fa):
    FA_TYPE = Symbols.NFA_TYPE

    states: Set[str]
    initial_state: str
    final_states: Set[str]
    transactions: Dict[str, Dict[str, Set[str]]]
    alphabets: Set[str]

    def normalize(self) -> None:
        states_table: Dict[str, str] = {}

        new_states: Set[str] = set()
        new_final_states: Set[str] = set()
        new_initial_state: str = ''
        new_transactions: Dict[str, Dict[str, Set[str]]] = {}

        state_counter = 1
        stack: List[str] = [self.initial_state]
        while stack:
            state = stack.pop()

            new_state = states_table.get(state)
            if not new_state:
                new_state = f"{Symbols.STATE_NAME_PREFIX}{state_counter}"
                states_table[state] = new_state
                state_counter += 1

            new_state_transactions: Dict[str, Set[str]] = {}
            for alphabet in self.transactions.get(state, {}).keys():
                new_state_transactions[alphabet] = set()

                for destination_state in self.transactions[state][alphabet]:
                    new_destination_state = states_table.get(destination_state)

                    if not new_destination_state:
                        new_destination_state = f"{Symbols.STATE_NAME_PREFIX}{state_counter}"
                        states_table[destination_state] = new_destination_state
                        state_counter += 1
                        stack.append(destination_state)

                    new_state_transactions[alphabet].add(new_destination_state)

            new_states.add(new_state)
            if state == self.initial_state:
                new_initial_state = new_state
            elif state in self.final_states:
                new_final_states.add(new_state)

            if new_state_transactions:
                new_transactions[new_state] = new_state_transactions

        self.states = new_states
        self.initial_state = new_initial_state
        self.final_states = new_final_states
        self.transactions = new_transactions

    def kleene_star(self) -> None:
        if len(self.final_states) > 1:
            new_final_state = str(uuid.uuid4())
            old_final_states = self.final_states
            self.final_states = {new_final_state}
            self.states.add(new_final_state)
            for state in old_final_states:
                if state not in self.transactions:
                    self.transactions[state] = dict()
                state_epsilon_transactions: Set[str] = self.transactions[state].get(Symbols.EPSILON, set())
                state_epsilon_transactions.add(new_final_state)
                self.transactions[state][Symbols.EPSILON] = state_epsilon_transactions

        final_state = list(self.final_states)[0]
        if self.initial_state not in self.transactions:
            self.transactions[self.initial_state] = dict()
        initial_state_epsilon_transactions: Set[str] = self.transactions[self.initial_state].get(Symbols.EPSILON, set())
        initial_state_epsilon_transactions.add(final_state)
        self.transactions[self.initial_state][Symbols.EPSILON] = initial_state_epsilon_transactions

        if final_state not in self.transactions:
            self.transactions[final_state] = dict()
        final_state_epsilon_transactions: Set[str] = self.transactions[final_state].get(Symbols.EPSILON, set())
        final_state_epsilon_transactions.add(self.initial_state)
        self.transactions[final_state][Symbols.EPSILON] = final_state_epsilon_transactions

    def kleene_one(self) -> None:
        if len(self.final_states) > 1:
            new_final_state = str(uuid.uuid4())
            old_final_states = self.final_states
            self.final_states = {new_final_state}
            self.states.add(new_final_state)
            for state in old_final_states:
                if state not in self.transactions:
                    self.transactions[state] = dict()
                state_epsilon_transactions: Set[str] = self.transactions[state].get(Symbols.EPSILON, set())
                state_epsilon_transactions.add(new_final_state)
                self.transactions[state][Symbols.EPSILON] = state_epsilon_transactions

        final_state = list(self.final_states)[0]
        if self.initial_state not in self.transactions:
            self.transactions[self.initial_state] = dict()
        initial_state_epsilon_transactions: Set[str] = self.transactions[self.initial_state].get(Symbols.EPSILON, set())
        initial_state_epsilon_transactions.add(final_state)
        self.transactions[self.initial_state][Symbols.EPSILON] = initial_state_epsilon_transactions

    def kleene_plus(self) -> None:
        if len(self.final_states) > 1:
            new_final_state = str(uuid.uuid4())
            old_final_states = self.final_states
            self.final_states = {new_final_state}
            self.states.add(new_final_state)
            for state in old_final_states:
                if state not in self.transactions:
                    self.transactions[state] = dict()
                state_epsilon_transactions: Set[str] = self.transactions[state].get(Symbols.EPSILON, set())
                state_epsilon_transactions.add(new_final_state)
                self.transactions[state][Symbols.EPSILON] = state_epsilon_transactions

        final_state = list(self.final_states)[0]
        if final_state not in self.transactions:
            self.transactions[final_state] = dict()
        final_state_epsilon_transactions: Set[str] = self.transactions[final_state].get(Symbols.EPSILON, set())
        final_state_epsilon_transactions.add(self.initial_state)
        self.transactions[final_state][Symbols.EPSILON] = final_state_epsilon_transactions

    @classmethod
    def union(cls, nfa1: 'Nfa', nfa2: 'Nfa') -> 'Nfa':
        states = nfa1.states.union(nfa2.states)
        initial_state = str(uuid.uuid4())
        states.add(initial_state)
        nfa = cls(
            initial_state=initial_state,
            states=states,
            final_states=nfa1.final_states.union(nfa2.final_states),
            alphabets=nfa1.alphabets.union(nfa2.alphabets),
            transactions=merge_dict(nfa1.transactions, nfa2.transactions)
        )
        nfa.transactions[nfa.initial_state] = {Symbols.EPSILON: {nfa1.initial_state, nfa2.initial_state}}
        return nfa

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
    def concat(cls, nfa1: 'Nfa', nfa2: 'Nfa') -> 'Nfa':
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

    @classmethod
    def regex_to_nfa(cls, regex: str) -> 'Nfa':
        postfix_exp = cls.regex_to_postfix(regex=regex)

        nfa_stack: List[Nfa] = []
        for character in postfix_exp:
            if Symbols.is_alphabet(character):
                nfa_stack.append(cls.init_nfa(character=character))
            elif character == Symbols.CONCAT:
                nfa2 = nfa_stack.pop()
                nfa1 = nfa_stack.pop()
                nfa_stack.append(cls.concat(nfa1=nfa1, nfa2=nfa2))
            elif character == Symbols.UNION:
                nfa2 = nfa_stack.pop()
                nfa1 = nfa_stack.pop()
                nfa_stack.append(cls.union(nfa1=nfa1, nfa2=nfa2))
            elif character == Symbols.ZERO_OR_MORE:
                nfa = nfa_stack.pop()
                nfa.kleene_star()
                nfa_stack.append(nfa)
            elif character == Symbols.ZERO_OR_ONE:
                nfa = nfa_stack.pop()
                nfa.kleene_one()
                nfa_stack.append(nfa)
            elif character == Symbols.ONE_OR_MORE:
                nfa = nfa_stack.pop()
                nfa.kleene_plus()
                nfa_stack.append(nfa)
        nfa = nfa_stack.pop()
        return nfa

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

    @staticmethod
    def get_epsilon_closure(nfa: 'Nfa', state: str) -> Set[str]:
        result: Set[str] = set()
        stack: List[str] = [state]

        while stack:
            current_state: str = stack.pop()

            result.add(current_state)

            current_state_epsilon_transactions: Optional[Set[str]] = nfa.transactions.get(
                current_state, {}).get(Symbols.EPSILON, None)

            if current_state_epsilon_transactions:
                for state in current_state_epsilon_transactions:
                    if state not in result:
                        stack.append(state)

        return result
