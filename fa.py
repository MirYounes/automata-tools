import uuid
import pprint
from typing import List, Dict, Set, Union, Tuple

from schemas import Symbols

from graphviz import Digraph


class Fa:
    FA_TYPE: str = Symbols.FA_TYPE

    def __init__(
        self,
        states: Set[str],
        initial_state: str,
        final_states: Set[str],
        transactions: Dict[str, Dict[str, Union[Set[str], str]]],
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

    def draw(self, directory: str, title: str = '') -> List[str]:
        title = title or self.FA_TYPE

        images: List[str] = []
        graph = Digraph(format='png')
        graph.attr(rankdir='LR')

        # add an initial edge
        initial_state_name = self.get_state_name(state=self.initial_state)
        graph.node(name='', shape='none')
        graph.node(name=initial_state_name, shape='circle', style='filled', color=Symbols.INITIAL_STATE_COLOR)
        graph.edge("", initial_state_name)

        drawed_states: Set[str] = {self.initial_state}
        state_stack: List[str] = [self.initial_state]
        step = 1
        while state_stack:
            new_state_stack: List[str] = []
            is_changed = False

            while state_stack:
                state = state_stack.pop(0)
                state_transactions = self.transactions.get(state)
                state_transactions_reverse: Dict[str, Set[str]] = dict()
                state_name = self.get_state_name(state=state)

                if not state_transactions:
                    continue

                for alphabet, alphabet_transactions in state_transactions.items():
                    alphabet_transactions = alphabet_transactions if self.FA_TYPE == Symbols.NFA_TYPE else {
                        alphabet_transactions}
                    for destination_state in alphabet_transactions:
                        destination_state_transaction = state_transactions_reverse.get(destination_state, set())
                        destination_state_transaction.add(alphabet)
                        state_transactions_reverse[destination_state] = destination_state_transaction

                        if destination_state not in drawed_states:
                            state_color = Symbols.MIDDLE_STATE_COLOR
                            if destination_state == self.initial_state:
                                state_color = Symbols.INITIAL_STATE_COLOR
                            elif (destination_state == Symbols.TRAP_STATE) or (Symbols.TRAP_STATE in destination_state):
                                state_color = Symbols.TRAP_STATE_COLOR
                            elif destination_state in self.final_states:
                                state_color = Symbols.FINAL_STATE_COLOR

                            state_shape = 'doublecircle' if destination_state in self.final_states else 'circle'
                            graph.node(name=self.get_state_name(state=destination_state), shape=state_shape,
                                       style='filled', color=state_color)
                            new_state_stack.append(destination_state)
                            drawed_states.add(destination_state)

                for destination_state, alphabets in state_transactions_reverse.items():
                    graph.edge(tail_name=state_name, head_name=self.get_state_name(state=destination_state),
                               label=",".join(alphabets))
                    is_changed = True

            if is_changed:
                label = f"{title}_step_{step}"
                graph.attr(label=label, fontsize='30')
                image = graph.render(filename=label, directory=directory)
                images.append(image)
                step += 1
            state_stack = new_state_stack

        return images

    @staticmethod
    def get_state_name(state: Union[str, Tuple[str, ...]]) -> str:
        return state if isinstance(state, str) else ",".join(state)
