import uuid
import pprint
from typing import List, Dict, Set, Union

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

    def draw(self, directory: str) -> List[str]:
        images: List[str] = []
        graph = Digraph(format='png')
        graph.attr(rankdir='LR')

        # add an initial edge
        graph.node(name='', shape='none')
        graph.node(name=self.initial_state, shape='circle')
        graph.edge("", self.initial_state)

        drawed_states: Set[str] = {self.initial_state}
        state_stack: List[str] = [self.initial_state]
        step = 1
        while state_stack:
            new_state_stack: List[str] = []
            is_changed = False

            while state_stack:
                state = state_stack.pop(0)
                state_transactions = self.transactions.get(state)
                if not state_transactions:
                    continue
                for alphabet, alphabet_transactions in state_transactions.items():
                    for destination_state in alphabet_transactions:
                        if destination_state not in drawed_states:
                            state_shape = 'doublecircle' if destination_state in self.final_states else 'circle'
                            graph.node(name=destination_state, shape=state_shape)
                            new_state_stack.append(destination_state)
                            drawed_states.add(destination_state)
                        graph.edge(tail_name=state, head_name=destination_state,
                                   label=Symbols.EPSILON_UNICODE if alphabet == Symbols.EPSILON else alphabet)
                        is_changed = True

            if is_changed:
                label = f"{self.FA_TYPE}_step_{step}"
                graph.attr(label=label, fontsize='30')
                image = graph.render(filename=label, directory=directory)
                images.append(image)
                step += 1
            state_stack = new_state_stack

        return images
