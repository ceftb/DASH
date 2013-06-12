% -*- Mode: Prolog -*-

% Model the TMI control plans embodied in Marc's file
%
%
% 
% MHS  Flow:
% 0. Static facts, goals, helper functions etc..
%
% 1. Input: assertions from Java update beliefs
%		a. From body (sensors)
% 		*b. From emotional filter (mood, nodes)
% 		*c. From timer
%
% 2. Mental modeling of alternative plans and their utilities
% 		a. Utility function (unemotional)
% 			1) Belief function given inconsistency (likelihood; unemotional)
% 		b.*Utility function (emotional)
% 			*1) Belief function (likelihood; emotional)
%
% 3. Output the next primitive action to Java

%%% -----------------------------------------------------------------------

% MHS 0.
:- style_check(-singleton).
:- style_check(-discontiguous).

% These can change during the agent execution
:-dynamic(value/2).
:-dynamic(probability/2).
:-dynamic(belief/2).
:-dynamic(utility/2).
:-dynamic(targetField/1).
:-dynamic(relevant/1).
:-dynamic(needCheckSystem1/0).


% Definitions for objects (note the consequences belong in the world simulator, a different program in this model).

low(Object)  :- value(Object,X), acceptableRange(Object,Min,_), X < Min.
high(Object) :- value(Object,X), acceptableRange(Object,_,Max), X > Max.
ok(Object)   :- value(Object,X), acceptableRange(Object,Min,Max), X >= Min, X =< Max.

acceptableRange(coolantTemperature, 275, 475).
acceptableRange(waterPressure, 10, 20).
acceptableRange(coreExitTemperature, 275, 475).
acceptableRange(containmentTemperature, 400, 800).
acceptableRange(radiationLevel, 0, 2).

relevant(reactorCoolantPump).

relevant(coolantMakeupFlow) :- value(coolantLeak, yes).

% Some initial states

value(coolantTemperature, unknown).  % was 810 (high). Now the value is to be given from the simulator via the java shell.
value(reactorCoolantPump, unknown).  % Could have the unknown values be derived from having no declared value.

value(waterPressure, unknown).  % was 8 (low). Now comes from simulator.
value(waterPump, unknown).
value(reliefValve, unknown).
value(emergencyPipeRerouting, unknown).
value(emergencyWaterRelease, unknown).
value(emergencySteamRelease, unknown).
value(emergencyPump, unknown).

value(coreExitTemperature, 375).
value(auxiliaryCoolingRods, unknown).
value(unscheduledFuelAddition, unknown).

value(containmentTemperature, 600).
value(reactorCoolantPump, unknown).
value(containmentIsolationValve, unknown).
value(heatResidualExchanger, unknown).
value(coolantMakeupFlow, unknown).
value(containmentSpray, unknown).
value(emergencyContainmentPressurizer, unknown).

value(radiationLevel, 0).
value(filtrationFan, unknown).
value(containmentChamberAbsorptionGas, unknown).

value(emergencyShutdown, unknown).
value(controlRods, unknown).
value(insulatorDump, unknown).
value(sCRAMButton, unknown).

goal(plantOk).  % Agent's top-level goal
goalWeight(plantOk,2).

% MHS why isn't waiting explicitly set up as a goal or subgoal?
goalWeight(waiting,0).  % starts right up

% possible subgoals depending on beliefs, changing emotions, costs.  
subGoal(fixCoolantTemperature).

subGoal(fixWaterPressure).
subGoal(turnPumpOn).
subGoal(openReliefValve).
subGoal(emergencyPipeRerouting).
subGoal(emergencyWaterRelease).
subGoal(emergencySteamRelease).
%subGoal(emergencyPump).  % Made primitive for test

subGoal(fixCoreExitTemperature).
subGoal(deployAuxiliaryCoolingRods).
subGoal(unscheduledFuelAddition).

subGoal(fixContainmentTemperature).
subGoal(reactorCoolantPump).
subGoal(containmentIsolationValve).
subGoal(coolantMakeupFlow).
subGoal(residualHeatExchanger).
subGoal(containmentSpray).
subGoal(emergencyContainmentPressurizer).

subGoal(fixRadiationLevel).
subGoal(filtrationFan).
subGoal(containmentChamberAbsorptionGas).

subGoal(emergencyShutdown).
subGoal(controlRods).
subGoal(insulatorDump).
subGoal(SCRAMButton).

subGoal(try(_,_)).
subGoal(try2(_,_)).

% If there are no known problems, the plant is ok.
goalRequirements(plantOk, [check(coolantTemperature)]) :- value(coolantTemperature, unknown), !.
goalRequirements(plantOk, [doNothing]) :- ok(coolantTemperature).
goalRequirements(plantOk, [fixCoolantTemperature]) :- high(coolantTemperature), assert(targetField(coolantTemperature)).

% This is the main plan for high coolant temperature 
%% JB: The goalRequirements term links the goal to the plan substeps. Do you mean here to make the goal active 
%% under these circumstances or to specify substeps? 
goalRequirements(fixCoolantTemperature, [check(waterPressure)]) :- value(waterPressure, unknown), !.
goalRequirements(fixCoolantTemperature, [fixWaterPressure]) :- low(waterPressure).
goalRequirements(fixCoolantTemperature) :- high(containmentTemperature), assert(targetField(containmentTemperature)).
goalRequirements(fixCoolantTemperature) :- high(coreExitTemperature), assert(targetField(coreExitTemperature)).
goalRequirements(fixCoolantTemperature) :- high(waterPressure), assert(targetField(waterPressure)).
goalRequirements(fixCoolantTemperature) :- emergencyShutdown.

% Followup plans (simplified to one step for now)
goalRequirements(fixContainmentTemperature) :- 
%  [try(reactorCoolantPump, on), check(containmentTemperature), check(coolantTemperature), 
   [try(coolantMakeupFlow, on), check(containmentTemperature), check(coolantTemperature)].
%   try(heatResidualExchanger, on), 
%   check(containmentTemperature), check(coolantTemperature), emergencyShutdown].
   
goalRequirements(fixCoreExitTemperature) :- [try(deployAuxiliaryCoolantRods, on), check(coreExitTemperature), check(coolantTemperature)]. 
%   try(unscheduledFuelAddition, on), 
%   check(coreExitTemperature), check(coolantTemperature) emergencyShutdown].

% New version that uses model envisionment
goalRequirements(fixWaterPressure, [checkSystem1]) :- needCheckSystem1.  % Creates a dummy call out to emocog
goalRequirements(fixWaterPressure, [emergencyBypassPump]) :- preferPlan([emergencyBypassPump],[emergencyPump], []), !.
goalRequirements(fixWaterPressure, [emergencyPump]).
   
%goalRequirements(fixWaterPressure) :- [try(turnPumpOn, on), check(waterPressure), check(coolantTemperature)].
%   , try(openReliefValve, on), 
%   check(waterPressure), check(coolantTemperature), try(emergencyPipeRerouting, on),
%   check(waterPressure), check(coolantTemperature), try(emergencyWaterRelease, on),
%   check(waterPressure), check(coolantTemperature), try(emergencySteamRelease, on),
%   check(waterPressure), check(coolantTemperature), try(emergencyPump, on),
%   check(waterPressure), check(coolantTemperature), emergencyShutdown].

% 'trying' an object means checking the value, attempting to set it if needed and re-checking the target field.

% If the value is already the 'try' value, do nothing.
goalRequirements(try(Object,Value), [check(TargetField)]) :- value(Object, Value), targetField(TargetField), !.

% Otherwise if it's unknown, check it.
goalRequirements(try(Object,Value), [check(Object),try2(Object,Value)]) :- relevant(Object), value(Object, unknown), !.
goalRequirements(try(Object,Value), [try2(Object,Value)]) :- relevant(Object), !.
goalRequirements(try(Object,Value), []). % Do nothing if the object isn't relevant

% If known but not the try value, set it and re-test the target field.
goalRequirements(try2(Object,Value), [set(Object,Value), check(TargetField)]) :- targetField(TargetField).

%%% -----------------------------------------------------------------------

% MHS 1.
% updateBeliefs is called by the agent on the result of performing an action, to process sensor readings
% This is where the probabilities should go in terms of which plan to make
% 
% This is the input from Java sensors.
% Note that beliefs for check(Field) also need a belief rate (believability function)
% *Could also be used to update emotion-based values

% New 6/10/13: every other action leads to needCheckSystem1 being asserted, to force the system to check with 
% emoCog before doing the next thing.

updateBeliefs(check(Field),Value) :- !, retractall(value(Field,_)), assert(value(Field,Value)), assert(needCheckSystem1).
updateBeliefs(set(Field,Value),1) :- !, retractall(value(Field,_)), assert(value(Field,Value)), assert(needCheckSystem1).  % Note success of setting a value

% checkSystem1 returns a list of nodes and strengths which are asserted to system1
updateBeliefs(checkSystem1, []) :- !, retractall(needCheckSystem1).  % will be re-asserted after taking another primitive action
updateBeliefs(checkSystem1, [node(Node,Strength)|Rest]) :- 
  !, format('asserting ~w\n', [system1Fact(Node,Strength)]),
  retractall(system1Fact(Node,_)), assert(system1Fact(Node,Strength)), updateBeliefs(checkSystem1, Rest).
updateBeliefs(checkSystem1, X) :- format('unrecognized format in system 1 result: ~w\n', [X]).

updateBeliefs(_,_).  % Do nothing with any other action result pair

%%% -----------------------------------------------------------------------

% MHS 2.  
% Mental modeling and projections
%% addSets and trigger predicates define how to do forward projection on mentalModels.
%% The 'utility' predicate defines how to score final projected worlds.

% first check for inconsistency based on latest update of beliefs (this is the only inconsistency we care about for now)
inconsistency :- high(coolantTemperature), ok(waterPressure), ok(coreExitTemperature), ok(containmentTemperature).

% need to choose what model to believe in case of inconsistency.  
% 20% all readings are correct, 80% chance of possible reading failures split out as shown
%mentalModel([correct, .2]):- inconsistency.  % all readouts correct
%mentalModel([ok(coolantTemperature), .5]):- inconsistency. % (for now) only one readout at a time can be false
%mentalModel([high(containmentTemperature), .1]):- inconsistency. % 
%mentalModel([high(coreExitTemperature), .1]):- inconsistency. % 
%mentalModel([low(waterPressure), .1]):- inconsistency. % 

% We currently don't have weights on alternative mental models. This is not the place to put data uncertainty.
%mentalModel([correct,ok(coolantTemperature),high(containmentTemperature),high(coreExitTemperature),low(waterPressure)]) :-
%  inconsistency, !.
% We also don't have any projection rules below for 'correct'.
mentalModel([low(waterPressure)]) :- inconsistency, !.
% Need some mental model otherwise
mentalModel([correct]).

%% addSets for possible actions
% For now, believe at 100% that we'll successfully operate a control in the reactor.  This holds for all mental models.
%addSets(set(_,_), _, [[0.0], [1.0, wasSet(_,_)]]). This is a default case since I'm suggesting to do the rest with addSets, so should come at the end of the file.

% MHS need addSets for individual cases?

%% Triggers.  Very shallow planning for now.

% I'm thinking these should actually all be addSets, since they all discuss direct consequences of an action and few
% effects are shared across actions. See below.

% Ok, these are the addSets for the alternate beliefs. Arbitrary system 1 threshold.

addSets(emergencyBypassPump, _, [[1.0, emergencyBypassPump]]) :- system1Fact(pipeRupture, Strength), Strength > 0.5, !.
addSets(emergencyBypassPump, _, [[1.0, emergencyBypassPump, bad]]).

addSets(emergencyPump, _, [[1.0, emergencyPump, bad]]) :- system1Fact(pipeRupture, Strength), Strength > 0.5, !.
addSets(emergencyPump, _, [[1.0, emergencyPump]]).

% Test subconcious beliefs within consciousness.
% If this is above threshold, selects emergencyBypassPump, otherwise selects emergencyPump, based on projection.
system1Fact(pipeRupture, 0.4).


% In a world where all readings are correct, we shut down the reactor.  
%   Projected result: 100% chance of scrammed.
%trigger(World, correct, [[scrammed|World]], 1) :- wasSet(SCRAMButton)]).
% JB: This is the effect of the action regardless of what mental model the agent has. Also note anything starting with a capital letter
%     is a variable, so this addSet matched every set action!
addSets(set(sCRAMButton,on), _, [[1.0, scrammed]]) :- !.  % The :- ! construction basically says don't backtrack and look for different addsets.

% At the moment there are no probabilities on worlds produced by triggers. This could be changed but for now
% I'm re-working for the current system.

% In a world where coolantTemperature is ok, we want to do nothing.  
%   Projected result: 50% chance of meltdown vs. 50% chance success.
% JB: This seems confused. Neither triggers nor addSets talk about what we should do. And in a world where coolantTemperature is ok, why is there
%     a 50% chance of meltdown?
%trigger(World, ok(coolantTemperature), [[success|World, .5],[meltdown|World, .5]]).
%trigger(World, ok(coolantTemperature), [[success|World],[meltdown|World]],2) :- not(member(success,World)), not(member(meltdown,World)).  % To stop it continually adding this


% In a world where waterPressure is low, we want to start water pump.  
%   Projected result: 80% chance of scrammed vs. 20% chance of success, and additional 25% chance of irradiation.
%trigger(World, low(waterPressure), [[success|World, .2],[scrammed|World], .8]) :- wasSet(waterPump), !.
%trigger(World, low(waterPressure), [[World, .75],[irradiation|World, .25]]) :- wasSet(waterPump), !.
%trigger(World, low(waterPressure), [[success(waterPump)|World],[scrammed|World]], 2) :- wasSet(waterPump), not(member(success(waterPump),World)), not(member(scrammed,World)), !.
%trigger(World, low(waterPressure), [[noIrradiation,World],[irradiation|World]], 2) :- wasSet(waterPump), not(member(noIrradiation,World)), not(member(irradiation,World)), !.
% JB: The irradiation could be done as a trigger since it's an independent effect, but I've combined the two effects here for a simpler clause structure.

% Presumably things are worse in non-low water pressure worlds?
addSets(set(waterPump,on), low(waterPressure), 
        [[0.2, scrammed, irradiation], [0.6, scrammed], [0.05, success, irradiation], [0.15, success]]) :- !.

% Let's say that in our model of low(waterPressure), if you do nothing you get a meltdown:
trigger(World, low(waterPressure), [[meltdown|World]], 1) :- not(member(success,World)), not(member(scrammed,World)).

% In a world where coreExitTemperature is incorrect, we want to deploy auxiliary coolant rods.
%   Projected result: 80% chance of scrammed vs. 20% chance of success, and additional 40% chance of irradiation.
%trigger(World, mentalModel(high(coreExitTemperature)), [[success|World, .2],[scrammed|World], .8]) :- wasSet(deployAuxiliaryCoolantRods), !.
%trigger(World, mentalModel(high(coreExitTemperature)), [[World, .6],[irradiation|World, .4]]) :- wasSet(deployAuxiliaryCoolantRods), !.

%trigger(World, high(coreExitTemperature), [[success|World],[scrammed|World], .8]) :- wasSet(deployAuxiliaryCoolantRods), !.
%trigger(World, high(coreExitTemperature), [[World, .6],[irradiation|World, .4]]) :- wasSet(deployAuxiliaryCoolantRods), !.

addSets(set(deployAuxililiaryCoolantRods, on), high(coreExitTemperature),
        [[0.32, scrammed, irradiation], [0.48, scrammed], [0.12, success, irradiation], [0.08, success]]) :- !.

% In a world where containmentTemperature is incorrect, we want to deploy auxiliary coolant rods.
%   Projected result: 80% chance of scrammed vs. 20% chance of success, and additional 50% chance of irradiation.
%trigger(World, mentalModel(high(containmentTemperature)), [[success|World, .2],[scrammed|World], .8]) :- wasSet(coolantMakeupFlow), !.
%trigger(World, mentalModel(high(containmentTemperature)), [[World, .6],[irradiation|World, .4]]) :- wasSet(coolantMakeupFlow), !.
addSets(set(coolantMakeupFlow,on), high(containmentTemperature),
       [[0.4, scrammed, irradiation], [0.4, scrammed], [0.1, success, irradiation], [0.1, success]]) :- !.

%% 'doNothing' is a bogus action to allow triggers to happen on an otherwise empty plan:
addSets(doNothing, _, [[1.0,didNothing]]).

trigger(World, _, [World], 0).  % by default, nothing happens


%% Utility functions (assume decision theoretics). 

decisionTheoretic. % Have to say so.

% Utility of various worlds under any model. I will assume one model at a time here.
% mentalModel probability and trigger - state probability need to be associated with these utility functions too

utility(World, -10) :- member(bad, World), !.
utility(World, 5) :- member(emergencyBypassPump, World), !.
utility(World, 5) :- member(emergencyPump, World), !.

utility(World, -10) :- member(meltdown, World), !.
utility(World, -5) :- member(irradiation, World), !.
utility(World, -1) :- member(scrammed, World), !.
utility(World, 0) :- member(success, World), !.
utility(_,-0.5).  % Utility of any world not covered above is -0.5.

%% Link from projection to action?  Not sure how to build this statement.
takeAction(set(_,_)) :- preferPlan([Action],[],[buildWorld]).

%%% -----------------------------------------------------------------------

% MHS 3.
% These are the output functions to Java perceive or execute.
primitiveAction(check(_)). % Checking a value is a primitive action, so it gets sent to the 'body' and will yield a return result.
primitiveAction(set(_,_)). % likewise setting a value

primitiveAction(checkSystem1).  % Dummy primitive action that gets intercepted and sent to emocog to create an external system 1

% These are for the new test
primitiveAction(emergencyBypassPump).
primitiveAction(emergencyPump).


