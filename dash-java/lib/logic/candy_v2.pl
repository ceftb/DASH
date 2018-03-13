:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(initialWorld/1).
:- dynamic(system2Fact/1).
:- consult('agentGeneral').

run :- kIterations(30).
kIterations(K) :- integer(K), K > 1, oneIteration, KMinusOne is K - 1, kIterations(KMinusOne).
kIterations(1) :- oneIteration.

oneIteration :- format('\n\nchoosing action...\n'), system1, do(X), format('chose action ~w\n', X), updateBeliefs(X, 1), system1.

goal(eatCandiesWithoutFallingSick).
goalWeight(eatCandiesWithoutFallingSick, 1).

subGoal(getCandyBag).
subGoal(eatCandies).
subGoal(decide(eatCandies)).

executable(decideToEatCandy).
primitiveAction(walkToPantry).
primitiveAction(grabBag).
primitiveAction(putDownBag).
primitiveAction(returnFromPantry).

primitiveAction(grabCandyFromBag).
primitiveAction(openCandyWrapper).
primitiveAction(eatCandy).
primitiveAction(putCandyAside).

primitiveAction(nap).

primitiveAction(doNothing).

primitiveAction(play).

primitiveAction(eatDinner).

goalRequirements(eatCandiesWithoutFallingSick, [getCandyBag, decide(eatCandies), play, nap, eatDinner, doNothing]).

goalRequirements(getCandyBag, [walkToPantry, grabBag, returnFromPantry, putDownBag]).

goalRequirements(eatCandies, [grabCandyFromBag, openCandyWrapper, eatCandy]).

system2Fact(ok(eatCandies)) :- initialWorld(I), preferPlan([eatCandies, play, nap, eatDinner, doNothing], [play, nap, eatDinner, doNothing], I), !.
system2Fact(ok(eatCandies)) :- retract(system2Fact(iWantCandy)), fail.


repeatable(decide(eatCandies)) :- system2Fact(iWantCandy).

repeatable(play) :- not(system1Fact(shouldStopPlaying, _)).
repeatable(play) :- system1Fact(shouldStopPlaying, J), J < 0.1.

repeatable(nap).

updateBeliefs(eatCandy, Result) :- format('updateBeliefs called with ~w, ~w\n', [eatCandy, Result]), addToWorld(performed(eatCandy)), initialWorld(I), inCurrentWorld(totalCandiesEaten(J), I), removeFromWorld(totalCandiesEaten(J)), K is J + 1, addToWorld(totalCandiesEaten(K)), !.

updateBeliefs(play, Result) :- format('updateBeliefs called with ~w, ~w\n', [play, Result]), addToWorld(performed(eatCandy)), initialWorld(I), inCurrentWorld(timeIHavePlayed(J), I), removeFromWorld(timeIHavePlayed(J)), K is J + 1, addToWorld(timeIHavePlayed(K)), !.

updateBeliefs(Action, Result) :-  format('updateBeliefs called with ~w, ~w\n', [Action, Result]), addToWorld(performed(Action)).

% system 1 logic

system1Fact(hungry, 0.25) :- inCurrentWorld(timeIHavePlayed(K), _), K > 2.

system1Fact(exhausted, 0.5) :- inCurrentWorld(timeIHavePlayed(K), _), K > 4.

if hungry and exhausted then shouldStopPlaying at 0.75.

% system 2 logic

system2Fact(iWantCandy).

mentalModel([boy]).

addSets(Action,_,_,[[1.0, performed(Action)]]).

utility(World, Utility) :- candiesEatenInWorld(World, K), member(performed(eatDinner), World), J is K + 2, J < 6, !, Utility is J, format('utility: ~w\n', J).
utility(World, Utility) :- candiesEatenInWorld(World, K), member(performed(eatDinner), World), J is K + 2, J >= 6, !, Utility is -1, format('utility: ~w\n', -1).

utility(World, Utility) :- candiesEatenInWorld(World, K), not(member(performed(eatDinner), World)), K < 6, !, Utility is K, format('utility: ~w\n', K).
utility(World, Utility) :- candiesEatenInWorld(World, K), not(member(performed(eatDinner), World)), K >= 6, !, Utility is -1, format('utility: ~w\n', -1).

candiesEatenInWorld([H|T], L) :- H = totalCandiesEaten(J), candiesEatenInWorld(T, K), L is J + K.
candiesEatenInWorld([H|T], K + 1) :- H = performed(eatCandies), candiesEatenInWorld(T, K).
candiesEatenInWorld([H|T], K) :- not(H = performed(eatCandies)), candiesEatenInWorld(T, K).
candiesEatenInWorld([], 0).

decisionTheoretic. % process of decision making... we use this

% regarding world

initialWorld([totalCandiesEaten(0), timeIHavePlayed(0)]).

inCurrentWorld(Fact, World) :- initialWorld(World), member(Fact, World).

addToWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), assert(initialWorld([Fact|I])), assert(Fact).
removeFromWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), delete(I,Fact,J), assert(initialWorld(J)).

% Have this here so we do not crash
trigger(World, _, [World], 0).  % by default, nothing happens when a world enters a particular state.
