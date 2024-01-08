import pyomo.environ as pyo
from typing import Union
from configuration import Configuration


class ConstraintRules:
    def __init__(self, config: Configuration):
        self.config = config

    @staticmethod
    def one_team_one_location_rule(model: pyo.ConcreteModel, home_team: int, guest_team: int, period: int) -> Union[pyo.Constraint, pyo.Constraint.Skip]:
        if (home_team, guest_team, period) in model.events:
            return model.match[home_team, guest_team, period] + model.match[guest_team, home_team, period] <= 1
        return pyo.Constraint.Skip

    @staticmethod
    def one_team_one_period_rule(model: pyo.ConcreteModel, home_team: int, guest_team: int) -> Union[pyo.Constraint, pyo.Constraint.Skip]:
        if home_team != guest_team:
            return sum([model.match[home_team, guest_team, period] for period in model.periods if
                        (home_team, guest_team, period) in model.events]) == 1
        return pyo.Constraint.Skip

    @staticmethod
    def require_play_home_game_rule(model: pyo.ConcreteModel, home_team: int) -> Union[pyo.Constraint, pyo.Constraint.Skip]:
        constraint = [model.match[home_team, guest_team, period] for period in model.periods for guest_team in
                      model.guest_teams if (home_team, guest_team, period) in model.events]
        if constraint:
            return sum(constraint) == len(model.home_teams) - 1
        return pyo.Constraint.Skip

    @staticmethod
    def require_play_guest_game_rule(model: pyo.ConcreteModel, guest_team: int) -> Union[pyo.Constraint, pyo.Constraint.Skip]:
        constraint = [model.match[home_team, guest_team, period] for period in model.periods for home_team in
                      model.home_teams if (home_team, guest_team, period) in model.events]
        if constraint:
            return sum(constraint) == len(model.guest_teams) - 1
        return pyo.Constraint.Skip

    def connect_movement_match_vars_rule(self, model: pyo.ConcreteModel) -> None:

        for home_team, guest_team, period in model.events:
            if period == self.config.start_period:
                continue

            for possible_home_opponent in model.home_teams:
                if possible_home_opponent == guest_team:
                    continue
                for possible_guest_opponent in model.guest_teams:
                    if possible_guest_opponent == home_team:
                        continue
                    constraint = (model.movement[home_team, guest_team, period]
                                  >= model.match[home_team, possible_guest_opponent, period - 1] + model.match[guest_team, possible_home_opponent, period] - 1)

                    model.connect_movement_game_var_rule.add(constraint)
