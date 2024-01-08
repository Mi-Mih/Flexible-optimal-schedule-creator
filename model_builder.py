import pyomo.environ as pyo
from typing import List, Tuple
import itertools
from dataclasses import field

from model_parts.constraints_rules import ConstraintRules
from model_parts.objective_parts import ObjectiveParts
from configuration import Configuration


class ModelBuilder:

    def __init__(self, config: Configuration, name: str = "scheduler"):
        self.model = pyo.ConcreteModel(name=name)
        self.config = config

    def build(self, teams=field(default_factory=[]), periods=field(default_factory=[])) -> pyo.ConcreteModel:
        """
        Метод построения модели
        """

        # добавление индексов
        self.add_sets(teams, periods)
        # добавление переменных
        self.add_vars()
        # добавление ограничений
        self.add_constraints()
        # добавление ЦФ
        self.add_objective()

        return self.model

    @staticmethod
    def create_unique_match_set(teams: List[int], periods: List[int]) -> List[Tuple[int, int, int]]:
        """
        Метод создания множества всех возможных пар матча
        При условии, что команда не играет сама с собой
        """
        decart_set = list(itertools.product(*[teams, teams, periods]))
        decart_set = [combination for combination in decart_set if combination[1] != combination[0]]
        return decart_set

    def add_sets(self, teams: List[int], periods: List[int]) -> None:
        """
        Метод создания множеств
        """

        self.model.home_teams = pyo.Set(initialize=teams, doc="home teams")
        self.model.guest_teams = pyo.Set(initialize=teams, doc="guest teams")
        self.model.periods = pyo.Set(initialize=periods, doc="periods")
        self.model.events = pyo.Set(initialize=self.create_unique_match_set(teams, periods), doc="h_teams * g_teams * periods")

    def add_vars(self) -> None:
        """
        Метод создания переменных
        """
        self.model.match = pyo.Var(self.model.home_teams, self.model.guest_teams, self.model.periods,
                                   doc="var played match",
                                   name="match",
                                   domain=pyo.Binary)

        self.model.movement = pyo.Var(self.model.home_teams, self.model.guest_teams, self.model.periods,
                                     doc="movement between stadiums",
                                     name="movement",
                                     domain=pyo.Binary)

    def add_constraints(self) -> None:
        """
        Метод создания ограничений модели
        """

        constraints_rules = ConstraintRules(self.config)

        # За 1 период можно сыграть 1 матч на одном стадионе - либо дома, либо в гостях
        self.model.one_team_one_location_rule = pyo.Constraint(self.model.home_teams, self.model.guest_teams,
                                                               self.model.periods,
                                                               rule=constraints_rules.one_team_one_location_rule,
                                                               doc="one location at one period",
                                                               )

        # команда должна сыграть с каждой командой чемпионата
        self.model.one_team_one_period_rule = pyo.Constraint(self.model.home_teams, self.model.guest_teams,
                                                             rule=constraints_rules.one_team_one_period_rule,
                                                             doc="all_to_all_teams")

        # команда должна сыграть с каждой командой дома
        self.model.require_play_home_game_rule = pyo.Constraint(self.model.home_teams,
                                                                rule=constraints_rules.require_play_home_game_rule,
                                                                doc="play match at home")

        # команда должна сыграть с каждой командой в гостях
        self.model.require_play_guest_game_rule = pyo.Constraint(self.model.guest_teams,
                                                                 rule=constraints_rules.require_play_guest_game_rule,
                                                                 doc="play match at guest")

        # ограничение - связь переменных перемещения между стадионами и признаком состоявшейся игры
        self.model.connect_movement_game_var_rule = pyo.ConstraintList()
        constraints_rules.connect_movement_match_vars_rule(self.model)

    def add_objective(self) -> None:
        """
        Метод создания ЦФ модели
        """
        objective_parts = ObjectiveParts(self.config)
        self.model.objective = pyo.Objective(rule=objective_parts.get_objective, sense=pyo.minimize)


if __name__ == "__main__":
    ...
