% this is a simple prolog file
% that may be useful in
% understanding agentGeneral

% to run:
% swipl -s candy.pl -g run.

:- dynamic(initialWorld/1).
:- consult('agentGeneral').

run :- kIterations(25).
kIterations(K) :- integer(K), K > 1, oneIteration, KMinusOne is K - 1, kIterations(KMinusOne).
kIterations(1) :- oneIteration.

oneIteration :- do(X), updateBeliefs(X, 1), format('chose action ~w\n', X).

goal(eatCandiesWithoutFallingSick).
goalWeight(eatCandiesWithoutFallingSick, 1).

subGoal(getCandyBag).
subGoal(eatCandies).

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

primitiveAction(play).

goalRequirements(eatCandiesWithoutFallingSick, [getCandyBag, eatCandies, play, nap]).

goalRequirements(getCandyBag, [walkToPantry, grabBag, returnFromPantry, putDownBag]).

goalRequirements(eatCandies, [grabCandyFromBag, openCandyWrapper, eatCandy]).

repeatable(eatCandies) :- inCurrentWorld(totalCandiesEaten(K), _), K < 5.
repeatable(eatCandies) :- inCurrentWorld(totalCandiesEaten(K), _), ansi_format([fg(red)], 'If I eat anymore candy and don\'t play, I might get sick!\n', []), K < 5.

repeatable(play).

updateBeliefs(eatCandy, Result) :- format('\n\nupdateBeliefs called with ~w, ~w \n\n', [eatCandy, Result]), addToWorld(performed(eatCandy)), inCurrentWorld(totalCandiesEaten(J), I), removeFromWorld(totalCandiesEaten(J)), K is J + 1, addToWorld(totalCandiesEaten(K)), !.

updateBeliefs(Action, Result) :-  format('\n\nupdateBeliefs called with ~w, ~w \n\n', [Action, Rresult]), addToWorld(performed(Action)).

% regarding world

initialWorld([totalCandiesEaten(0)]).

inCurrentWorld(Fact, World) :- initialWorld(World), member(Fact, World).

addToWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), assert(initialWorld([Fact|I])), assert(Fact).
removeFromWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), delete(I,Fact,J), assert(initialWorld(J)).
