:- consult('services.pl').

:- dynamic(id/1).
:- dynamic(observations/2).
:- dynamic(i/1).
:- dynamic(generateObservation/3).
:- dynamic(determineResult/3).
:- dynamic(printWorldState/0).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%% IMPORTANT %%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% world logic is used to:
%  - determine results of actions
%  - generate observations when actions are carried out
%  - maintain global state that changes as a result of actions taken

% this short section is for the coder who wants to program
% results of actions and generate appropriate observations

% add statements of form below to determine results of actions.
%
%     determineResult(Action, ID, Result).

% add statements of form below to generate observations.
% this can be used to determine observations for observer observer
% once ID takes action A and its result is determined to be R.
% note that if no observation should be generated, the predicate
% should not be satisfied.
% the observation Observation will be added to Observer's knowledge base
% during the next detergent cycle
%     generateObservation(Observer, actionResult(Action, ID, Result), Observation).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% by default, the result is default
% if, however, determineResult(A, ID, R) does exist we use that to determine the result
processAction(A, ID, R) :- determineResult(A, ID, R), forall(id(Observer), updateObservations(Observer, actionResult(A, ID, R))), ansi_format([fg(red)], 'processed action ~w by user ~w. result: ~w\n', [A, ID, R]), printWorldStateWrapper.
processAction(A, ID, default) :- not(determineResult(A, ID, _)), forall(id(Observer), updateObservations(Observer, actionResult(A, ID, default))), ansi_format([fg(red)], 'processed action ~w by user ~w. result: ~w\n', [A, ID, R]), printWorldStateWrapper.

printWorldStateWrapper :- not(printWorldState), !.
printWorldStateWrapper :- printWorldState, !.

% we should always have observations(ID, L) if ID is legitimate. L may be [].
% if generateObservation(Observer, ActionResult, Observation) exists, we use this to determine what the observer observes
updateObservations(Observer, ActionResult) :- generateObservation(Observer, ActionResult, Observation), observations(Observer, L), retract(observations(Observer, L)), assert(observations(Observer, [Observation | L])).
updateObservations(Observer, ActionResult) :- not(generateObservation(Observer, ActionResult, _)).

getObservations(Observer, observations(Observations)) :- observations(Observer, Observations), printObservations(Observer, Observations), retract(observations(Observer, Observations)), assert(observations(Observer, [])).

printObservations(Observer, L) :- format('Retrieving observations for ~w:', [Observer]), printObservations(L).
printObservations([]) :- format('\n').
printObservations([H | T]) :- format(' ~w -', [H]), printObservations(T).

generateObservation(Observer, actionResult(A, ID, R), observation(A, ID, R)).
