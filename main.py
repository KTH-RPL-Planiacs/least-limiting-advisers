from agent_synth_game import AgentSynthGame
from adviser_framework import AdviserFramework
from models import *


def running_example_direction():
    agents = [AgentSynthGame(mdp=corridor_directions_mdp(r_id='A', init_state='end_l_fr'),
                             formula='F(era) & G!(crita & critb)'),
              AgentSynthGame(mdp=corridor_directions_mdp(r_id='B', init_state='end_r_fl'),
                             formula='F(elb) & G!(critb & crita)')]
    framework = AdviserFramework(agents)
    framework.complete_strategy_synthesis(verbose=True)


def intersection():
    agents = [AgentSynthGame(mdp=intersection_no_turn_symmetric_labels_mdp(r_id='A', init_state='end_top'),
                             formula='F(eba) & G!(crita & critb | crita & critc | crita & critd)'),
              AgentSynthGame(mdp=intersection_no_turn_symmetric_labels_mdp(r_id='B', init_state='end_bot'),
                             formula='F(etb) & G!(critb & crita | critb & critc | critb & critd)'),
              AgentSynthGame(mdp=intersection_no_turn_symmetric_labels_mdp(r_id='C', init_state='end_left'),
                             formula='F(erc) & G!(critc & crita | critc & critb | critc & critd)'),
              AgentSynthGame(mdp=intersection_no_turn_symmetric_labels_mdp(r_id='D', init_state='end_right'),
                             formula='F(eld) & G!(critd & crita | critd & critb | critd & critc)')]
    framework = AdviserFramework(agents)
    framework.complete_strategy_synthesis(verbose=True)


def office_example():
    agents = [AgentSynthGame(mdp=office_clean_mdp(r_id='A', init_state='4,0'),
                             formula='F(officetra & clean & !officetrc) & '
                                     'F(officetla & clean & !officetlb)'),
              AgentSynthGame(mdp=office_clean_mdp(r_id='D', init_state='5,0'),
                             formula='F(officebrd & clean & !officebrc) & '
                                     'F(officebld & clean & !officeblb)'),
              AgentSynthGame(mdp=office_bins_mdp(r_id='B', init_state='5,9'),
                             formula='F(officeblb & bin) & '
                                     'F(officetlb & bin)'),
              AgentSynthGame(mdp=office_bins_mdp(r_id='C', init_state='4,9'),
                             formula='F(officebrc & bin) & '
                                     'F(officetrc & bin)')]
    framework = AdviserFramework(agents)
    framework.complete_strategy_synthesis(verbose=True)


if __name__ == '__main__':
    running_example_direction()
