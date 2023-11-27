import networkx as nx
import logging
from typing import Tuple
from up_graphene_engine.engine import  GrapheneEngine
from gui import Gui

from unified_planning.shortcuts import *
import unified_planning as up
import unified_planning.engines
import unified_planning.model
import unified_planning.model.metrics

get_environment().credits_stream = None



def planning(engine: GrapheneEngine, gui: Gui, reload_page):
    logging.info("Generating planning problem...")

    Match = UserType("Match")
    Fuse = UserType("Fuse")
    handfree = Fluent("handfree")
    light = Fluent("light", IntType())
    match_used = Fluent("match_used", BoolType(), match=Match)
    fuse_mended = Fluent("fuse_mended", BoolType(), fuse=Fuse)
    light_match = DurativeAction("light_match", m=Match)
    m = light_match.parameter("m")
    light_match.set_fixed_duration(gui.input_values["d_match"])
    light_match.add_condition(StartTiming(), Not(match_used(m)))
    light_match.add_effect(StartTiming(), match_used(m), True)
    light_match.add_effect(StartTiming(), light, light+1)
    light_match.add_effect(EndTiming(), light, light-1)
    mend_fuse = DurativeAction("mend_fuse", f=Fuse)
    f = mend_fuse.parameter("f")
    mend_fuse.set_fixed_duration(gui.input_values["d_fuse"])
    mend_fuse.add_condition(StartTiming(), handfree)
    mend_fuse.add_condition(ClosedTimeInterval(StartTiming(), EndTiming()), GT(light, 0))
    mend_fuse.add_effect(StartTiming(), handfree, False)
    mend_fuse.add_effect(EndTiming(), fuse_mended(f), True)
    mend_fuse.add_effect(EndTiming(), handfree, True)
    problem = Problem("MatchCellar")
    problem.add_fluent(handfree, default_initial_value=True)
    problem.add_fluent(light, default_initial_value=0)
    problem.add_fluent(match_used, default_initial_value=False)
    problem.add_fluent(fuse_mended, default_initial_value=False)
    problem.add_action(light_match)
    problem.add_action(mend_fuse)
    for i in range(1, int(gui.input_values["n_match"])+1):
        m = problem.add_object(f"match_{i}", Match)
    for i in range(1, int(gui.input_values["n_fuse"])+1):
        f = problem.add_object(f"fuse_{i}", Fuse)
        problem.add_goal(fuse_mended(f))

    logging.info("Planning...")

    res = engine.solve(problem)
    plan = res.plan

    return plan
