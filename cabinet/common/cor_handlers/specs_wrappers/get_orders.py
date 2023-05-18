from common.cor_handlers import AbstractCORHandler
from common.cor_states.wrappers import WrapperSpecsState


class SpecsOrdersHandler(AbstractCORHandler):
    def __init__(self, state: WrapperSpecsState):
        self.state: WrapperSpecsState = state

    def handle(self):
        for field, label in self.state.ordering_fields.items():

            self.state.ordering.append(
                dict(label=label.format(type="убыванию"), value=f"-{field}")
            )
            self.state.ordering.append(
                dict(label=label.format(type="возрастанию"), value=f"{field}")
            )
        return self.state
