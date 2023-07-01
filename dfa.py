from typing import Dict, Set, Tuple, List, Optional

import numpy

from schemas import Symbols
from fa import Fa
from nfa import Nfa


class Dfa(Fa):
    FA_TYPE = Symbols.DFA_TYPE

    states: Set[str]
    initial_state: str
    final_states: Set[str]
    transactions: Dict[str, Dict[str, str]]
    alphabets: Set[str]

    @classmethod
    def nfa_to_dfa(cls, nfa: Nfa) -> 'Dfa':
        initial_state: Tuple[str, ...] = tuple(Nfa.get_epsilon_closure(nfa=nfa, state=nfa.initial_state))
        alphabets: Set[str] = nfa.alphabets.copy()
        alphabets.remove(Symbols.EPSILON)

        dfa = cls(
            states=set(),
            initial_state='',
            final_states=set(),
            transactions=dict(),
            alphabets=alphabets
        )

        stack: List[Tuple[str]] = [initial_state]
        states_table: Dict[Tuple[str, ...], str] = {}
        counter: int = 1
        while stack:
            current_tuple_states: Tuple[str] = stack.pop()
            current_tuple_states_transactions = dict()

            state_name: str = states_table.get(current_tuple_states, '')
            if not state_name:
                state_name = f"{Symbols.STATE_NAME_PREFIX}{counter}"
                states_table[current_tuple_states] = state_name
                counter += 1

            for alphabet in alphabets:
                new_set_states: Set[str] = set()
                for state in current_tuple_states:
                    state_alphabet_transactions: Optional[Set[str]] = nfa.transactions.get(
                        state, {}).get(alphabet, None)
                    if state_alphabet_transactions:
                        for destination_state in state_alphabet_transactions:
                            new_set_states = new_set_states.union(
                                Nfa.get_epsilon_closure(nfa=nfa, state=destination_state))

                new_tuple_states = tuple(new_set_states) if new_set_states else Symbols.TRAP_STATE
                if new_tuple_states not in states_table:
                    stack.append(new_tuple_states)
                    new_state_name = (Symbols.TRAP_STATE if new_tuple_states ==
                                      Symbols.TRAP_STATE else f"{Symbols.STATE_NAME_PREFIX}{counter}")
                    states_table[new_tuple_states] = new_state_name
                    counter += 1

                current_tuple_states_transactions[alphabet] = states_table[new_tuple_states]

            if state_name not in dfa.states:
                dfa.states.add(state_name)
                if any(set(current_tuple_states) & nfa.final_states):
                    dfa.final_states.add(state_name)
                elif current_tuple_states == initial_state:
                    dfa.initial_state = state_name
            dfa.transactions[state_name] = current_tuple_states_transactions

        return dfa

    @property
    def reachable_states(self) -> Tuple[Dict[str, int], Dict[int, str], List[str]]:
        reachable_states: Dict[str, int] = dict()
        reachable_states_reverse: Dict[int, str] = dict()
        final_reachable_states: List[str] = []

        stack: List[str] = [self.initial_state]
        counter: int = 0
        while stack:
            current_state: str = stack.pop()
            reachable_states[current_state] = counter
            reachable_states_reverse[counter] = current_state
            if current_state in self.final_states:
                final_reachable_states.append(current_state)

            counter += 1

            for alphabet in self.alphabets:
                destination_state = self.transactions[current_state][alphabet]
                if destination_state not in reachable_states and destination_state not in stack:
                    stack.append(destination_state)

        return reachable_states, reachable_states_reverse, final_reachable_states

    @classmethod
    def minimize_dfa(cls, dfa: 'Dfa') -> 'Dfa':
        dfa_reachable_states: Dict[str, int]
        dfa_reachable_states_reverse: Dict[int, str]
        final_reachable_states: List[str]
        dfa_reachable_states, dfa_reachable_states_reverse, final_reachable_states = dfa.reachable_states
        dfa_reachable_states_count: int = len(dfa_reachable_states)

        table = numpy.zeros((dfa_reachable_states_count, dfa_reachable_states_count))

        for row in range(dfa_reachable_states_count):
            for col in range(row):
                table[row][col] = (
                    dfa_reachable_states_reverse[row] in dfa.final_states) != (
                    dfa_reachable_states_reverse[col] in dfa.final_states)

        while True:
            is_marked: bool = False

            for row in range(dfa_reachable_states_count):
                for col in range(row):
                    if table[row][col] == 0:
                        state_1: str = dfa_reachable_states_reverse[row]
                        state_2: str = dfa_reachable_states_reverse[col]

                        for alphabet in dfa.alphabets:
                            destination_state_1: str = dfa.transactions[state_1][alphabet]
                            destination_state_2: str = dfa.transactions[state_2][alphabet]
                            destination_state_1_num: int = dfa_reachable_states[destination_state_1]
                            destination_state_2_num: int = dfa_reachable_states[destination_state_2]

                            pairs: int = (table[destination_state_1_num][destination_state_2_num]
                                          if destination_state_1_num >= destination_state_2_num
                                          else table[destination_state_2_num][destination_state_1_num])

                            table[row][col] = pairs
                            if pairs:
                                is_marked = True
                                break

            if not is_marked:
                break

        parent = {}
        for state in dfa_reachable_states.keys():
            parent[state] = {"value": state, "states": [state]}

        def get_parent(current_state, all=False):
            parent_state = parent[current_state]
            while parent_state["value"] != current_state:
                current_state = parent_state["value"]
                parent_state = parent[current_state]
            if all:
                return parent_state
            else:
                return tuple(parent_state["states"])

        for row in range(dfa_reachable_states_count):
            for col in range(row):
                if table[row][col] == 0:
                    state_1: str = dfa_reachable_states_reverse[row]
                    state_2: str = dfa_reachable_states_reverse[col]
                    parent_state_1 = get_parent(state_1, all=True)
                    parent_state_2 = get_parent(state_2, all=True)
                    parent[parent_state_2["value"]]["value"] = parent_state_1["value"]
                    parent[parent_state_1["value"]]["states"] = list(
                        set(parent_state_1["states"]) | set(parent_state_2["states"]))

        new_dfa = cls(
            states=set(),
            initial_state='',
            final_states=set(),
            transactions=dict(),
            alphabets=dfa.alphabets
        )
        new_dfa.states = set([get_parent(state) for state in dfa_reachable_states.keys()])
        new_dfa.initial_state = get_parent(dfa.initial_state)
        new_dfa.final_states = set([get_parent(state) for state in final_reachable_states])

        new_dfa.transactions = {}
        for state in new_dfa.states:
            new_dfa.transactions[state] = {}
            for alphabet in new_dfa.alphabets:
                new_dfa.transactions[state][alphabet] = get_parent(
                    dfa.transactions[state[0]][alphabet])

        return new_dfa
