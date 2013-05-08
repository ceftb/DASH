% -*- Mode: Prolog -*-

% Model the control plans embodied in Marc's file
%

/*
 Notes on the entries in that file connected with pipe_rupture:
 Bypass Valve: Open/Closed. Check: WP - & Feedwater Pump ON & PR t. Alter: check true & Open. Cons: Closed & WP IAR .5
 Pipe Rupture (PR): f/t. Check: WP- & FP ON.
 Emergency Sealant Spray (ESS): off/on. Alter: WP- & PR t & Water Pressure Relief Valve closed & ESS off. Cons: ESS on & PR f .9 & WP ~ .9
 Feedwater Pump: off/on Check: WP-, Alter: WP-, FP off. Cons FP on & WP ~ .5
 Water pressure relief valve: closed/open. check: WP+. alter: wp+ & closed. cons: open & wp~ .8

Standard initial state: Bypass valve open, pipe rupture t, ESS off, Feedwater pump off, water pressure relied valve closed, water pressure low.

step 1. Check and turn on feedwater pump. wp ok 50%
step 2. if wp still low, check pipe rupture.
step 3. if pipe rupture, close bypass valve, wp ok 50%.
step 4. if wp still low, try emergency sealant spray. Turns off pipe rupture and wp ok 90%

*/

:- style_check(-singleton).
:- style_check(-discontiguous).

% These can change during the agent execution
:-dynamic(value/2).
:-dynamic(targetField/1).
:-dynamic(relevant/1).

goal(plantOk).  % Agent's top-level goal
goalWeight(plantOk,2).
goalWeight(waiting,0).  % starts right up

subGoal(fixLowPressure).
subGoal(try(_,_)).
subGoal(try2(_,_)).

% If there are no known problems, the plant is ok.
goalRequirements(plantOk, [doNothing]) :- ok(waterPressure).

goalRequirements(plantOk, [fixLowPressure]) :- low(waterPressure), assert(targetField(waterPressure)).

% This is the main plan for low water pressure.
goalRequirements(fixLowPressure, [try(feedwaterPump, on), check(pipeRupture), try(bypassValve, closed), try(emergencySealantSpray, on)]).



% 'trying' an object means checking the value, attempting to set it if needed and re-checking the target field.

% If the value is already the 'try' value, do nothing.
goalRequirements(try(Object,Value), [check(TargetField)]) :- value(Object, Value), targetField(TargetField), !.

% Otherwise if it's unknown, check it.
goalRequirements(try(Object,Value), [check(Object),try2(Object,Value)]) :- relevant(Object), value(Object, unknown), !.
goalRequirements(try(Object,Value), [try2(Object,Value)]) :- relevant(Object), !.
goalRequirements(try(Object,Value), []). % Do nothing if the object isn't relevant

% If known but not the try value, set it and re-test the target field.
goalRequirements(try2(Object,Value), [set(Object,Value), check(TargetField)]) :- targetField(TargetField).


primitiveAction(check(_)). % Checking a value is a primitive action, so it gets sent to the 'body' and will yield a return result.
primitiveAction(set(_,_)). % likewise setting a value



% updateBeliefs is called by the agent on the result of performing an action, to process sensor readings
updateBeliefs(check(Field),Value) :- !, retractall(value(Field,_)), assert(value(Field,Value)).
updateBeliefs(set(Field,Value),1) :- !, retractall(value(Field,_)), assert(value(Field,Value)).  % Note success of setting a value
updateBeliefs(_,_).  % Do nothing with any other action/result pair


% Definitions for objects (note the consequences belong in the world simulator, a different program in this model).

low(Object)  :- value(Object,X), acceptableRange(Object,Min,_), X < Min.
high(Object) :- value(Object,X), acceptableRange(Object,_,Max), X < Max.
ok(Object)   :- value(Object,X), acceptableRange(Object,Min,Max), X >= Min, X =< Max.

acceptableRange(waterPressure, 10, 15).

relevant(feedwaterPump).

relevant(bypassValve) :- value(pipeRupture, yes).

relevant(emergencySealantSpray) :- value(pipeRupture, yes).

% Some initial state

value(waterPressure, 7).
value(feedwaterPump, unknown).  % Could have the unknown values be derived from having no declared value.
value(bypassValve, unknown).
value(emergencySealantSpray, unknown).

state('default').
