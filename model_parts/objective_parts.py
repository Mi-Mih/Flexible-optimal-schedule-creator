import pyomo.environ as pyo
from configuration import Configuration


class ObjectiveParts:
    def __init__(self, config: Configuration):
        self.config = config

    def get_objective(self, model: pyo.ConcreteModel) -> pyo.Expression:

        main_part = self.get_main_part_objective(model)

        movement_part = self.get_movement_part_objective(model)

        return sum([main_part, movement_part])

    @staticmethod
    def get_main_part_objective(model: pyo.ConcreteModel) -> pyo.Expression:
        return sum(model.match[home_team, guest_team, period] for home_team, guest_team, period in model.events)

    def get_movement_part_objective(self, model: pyo.ConcreteModel) -> pyo.Expression:
        return sum(model.match[home_team, guest_team, period] for home_team, guest_team, period in model.movement if period != self.config.start_period)
