% -*- Mode: Prolog -*-

% Creates a group of agents sending and reading mail.

:- style_check(-singleton).
:- style_check(-discontiguous).
:- style_check(-atom).

:- dynamic(lastAgentBuilt/0).


goalRequirements(startGroup, [doNothing]) :-
  lastAgentBuilt, !.

% Starting the group involves deciding which agents to create, in what
% order and whether with pauses between them.
goalRequirements(startGroup, [startAgent(mailSender), startAgent(mailReader)]).

% When you hear success about the last agent you're done
updateBeliefs(startAgent(mailReader),1)
  :- assert(lastAgentBuilt).
updateBeliefs(_,_).

state('built group') :- lastAgentBuilt.
state('still to build group').

goal(startGroup).

goalWeight(startGroup, 1) :- started.
goalWeight(waiting, 1).

%started.
