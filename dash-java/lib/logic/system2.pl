% -*- Mode: Prolog -*-

% Includes rules for migrating facts between system1 and system2 and
% also mental models and envisionment.

:- style_check(-discontiguous).

:- multifile system2Fact/1.

% Used to report back to the agent shell.
:- dynamic(modelSummary/1).

% System1 facts over the threshold are adopted as system2 facts.
system2Fact(Fact) :-
  system1Fact(Fact, Value), system2Threshold(Th), Value > Th, !, incr(sys1Used).
system2Fact(Fact) :-
  system1Fact(Fact, Value), system2Threshold(Th), Value < -Th, !, incr(sys1Used), fail.

%% Deciding whether to perform an action is currently hooked into the reactive planner
%% through the 'decide' goal. Should this be more explicitly BDI?
goalRequirements(decide(Action), [Action])
  :- system2Fact(ok(Action)), !.
% this was doNothing, but I want to skip to the next step in the plan.
%goalRequirements(decide(Action), []) :- format('Action ~w not chosen\n', [Action]).
goalRequirements(decide(Action), []).

subGoal(decide(_)).


%% Preferring outcomes - this is not part of the planning code at the moment.
%% Nor does it currently use System 1 to propose operators, outcomes or utilities,
%% but it probably should.

%% Initially just pick one mental model at a time

preferPlan(Plan1, Plan2, Initial) :-
  assert(modelSummary('')),
  mentalModel([Model|_]),
%  format('\ncomparing ~w\n and ~w\n in model ~w\n', [Plan1, Plan2, Model]),
  envisionOutcomes(Plan1, Model, Initial, Outcomes1), 
%  format('~w leads to ~w\n', [Plan1, Outcomes1]),
  envisionOutcomes(Plan2, Model, Initial, Outcomes2), 
%  format('~w leads to ~w\n', [Plan2, Outcomes2]),
  !,
  prefer(Outcomes1, Outcomes2).

% The envisioned outcomes are a weighted set of possible outcomes. Each possible outcome
% is a set of fluents that will be true in the world of the outcome and are different from the
% current world.

envisionOutcomes([], _, World, [[1, World]]).  % One outcome from the empty plan, which is the current world.

% Project the first step on the world, and project the rest of the plan on each of the outcomes
envisionOutcomes([Action|RestOfPlan], Model, World, Outcomes) :-
  project(Action,Model,World,NextWorlds), 
  combineProjections(RestOfPlan,Model,NextWorlds,Outcomes).

% How to project an action from a list of sets of adds with weights.
project(Action,Model,World,NextWorlds) :-
  addSets(Action, Model, World, AddSets), 
  combineAdds(World, AddSets, ActionWorlds),
  sformat(String, 'Project ~w on ~w to ~w', [Action, World, ActionWorlds]),
  retractall(modelSummary(_)),
  assert(modelSummary(String)),
%  format(String),
  triggerWorlds(ActionWorlds, Model, NextWorlds, 1).    % last arg is the max number of steps to model.
% Warning: currently dies for maxSteps > 1.

combineAdds(_, [], []).
combineAdds(World, [[Weight | Adds]|Rest], [[Weight, Next]|RestNext]) :-
  append(World, Adds, Next), combineAdds(World, Rest, RestNext).

% Iterate over the next projected worlds
combineProjections(Plan,_,[],[]).

combineProjections(Plan,Model,[[Weight, World]|T],Outcomes) :-
  envisionOutcomes(Plan,Model,World,FirstUnweightedOutcomes), 
  combineWeights(Weight,FirstUnweightedOutcomes,FirstOutcomes),
  combineProjections(Plan,Model,T,RestOutcomes), 
  append(FirstOutcomes,RestOutcomes,Outcomes).


combineWeights(Weight1, [[Weight2,World]|T], [[Weight,World]|CT]) :- 
  Weight is Weight1 * Weight2, combineWeights(Weight1, T, CT).

combineWeights(_,[],[]).


% Ways to prefer uncertain worlds.

% Decision-theoretic: compute the expected utility of each set of
% possible outcomes, treating the weight as a probability.
prefer(O1, O2) :-
  decisionTheoretic, expectedUtility(O1, U1), expectedUtility(O2, U2), 
%  ((U1 > U2, format('Prefer ~w\n over ~w\n since ~w > ~w\n', [O1, O2, U1, U2])) ; 
%   (format('Prefer ~w\n over ~w\n since ~w <= ~w\n', [O2, O1, U1, U2]), fail)).
  U1 > U2.

expectedUtility([],0).
expectedUtility([[Weight,World]|Rest],U) :- 
  utility(World,FirstU), 
  %format('Utility of ~w is ~w\n', [World, FirstU]), 
  expectedUtility(Rest,RestU), U is Weight * FirstU + RestU.

% Triggers store beliefs about exogenous acts during projection

% Model n steps forward through triggers, or until the triggers come to a halt
triggerWorlds(Worlds, Model, FinalWorlds, MaxSteps) :- 
  triggerAndCount(Worlds, Model, FinalWorlds, MaxSteps, NewWorldCount),
  (NewWorldCount is 0, ! ; format('~w new worlds created in simulation\n', [NewWorldCount])).

% Trigger one step looks for triggers for each world in the set. The fourth
% argument is a count of the number of new worlds created.
triggerAndCount([],_,[],_,0).
triggerAndCount([[Weight,World]|T],Model,Worlds,MaxSteps,NewCount) :-
  triggerNSteps(World,Model,HTrigger,MaxSteps,OneNewCount), 
  triggerAndCount(T,Model,Rest,MaxSteps,RestNewCount),
  distributeWeight(Weight,HTrigger,TriggeredWorlds), 
  sformat(String, 'Trigger ~w on ~w to ~w', [Model, World, TriggeredWorlds]),
  modelSummary(Old),
  retract(modelSummary(Old)),
  sformat(New, '~w|~w', [String, Old]),
  assert(modelSummary(New)),
  %format(String),
  append(TriggeredWorlds, Rest, Worlds),
  NewCount is OneNewCount + RestNewCount.

triggerNSteps(World,Model,[World],0,0).  % Stop when there are no more steps

triggerNSteps(World,Model,[World],Steps,0) :- % Also stop when no new world is created
  trigger(World,Model,_,New), New is 0, !.

triggerNSteps(World,Model,TriggerFinal,MaxSteps,FinalCount) :-
  trigger(World,Model,HTrigger,NewCount),
  RemainingSteps is MaxSteps - 1,
  triggerAllNext(Model,HTrigger,TriggerFinal,RemainingSteps,FurtherCount),
  FinalCount is NewCount + FurtherCount.

% Go through the list of all new worlds and look for new new worlds
triggerAllNext(_,[],[],_,0) :- !.
triggerAllNext(Model,[World|Rest],Final,RemainingSteps,NewCount) :-
  triggerNSteps(World,Model,WorldFinal,RemainingSteps,WorldCount),
  triggerAllNext(Model,Rest,RestFinal,RemainingSteps,RestCount),
  append(WorldFinal,RestFinal,Final),
  NewCount is WorldCount + RestCount.
  

distributeWeight(Weight, Worlds, WeightedWorlds) :-
  size(Worlds, Size), NewWeight is Weight / Size, attachWeight(NewWeight,Worlds,WeightedWorlds).

% 'size' is just the number of worlds for now, should include weighting
size([],0).
size([H|T],Size) :- size(T,SmallerSize), Size is SmallerSize + 1.

attachWeight(_,[],[]).
attachWeight(Weight,[H|T],[[Weight,H]|R]) :- attachWeight(Weight,T,R).
