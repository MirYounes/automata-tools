from typing import Dict, Set, Tuple, List, Optional

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
