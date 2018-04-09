:- consult('agentGeneral').

:- dynamic(timesDone/1).
:- dynamic(timesToDo/1).

timesDone(0).
timesToDo(3).

goal(doWork).
goalWeight(doWork, 1).

primitiveAction(startWork).
subGoal(repeatSG).
primitiveAction(doNotRepeat).
primitiveAction(repeatMe).
primitiveAction(penultimateStep).
primitiveAction(endWork).
executable(nonsense).

execute(nonsense).

goalRequirements(doWork, [startWork, repeatSG, penultimateStep, endWork]) :- sleep(1).

goalRequirements(repeatSG, [nonsense, repeatMe]).

repeatable(repeatSG) :- timesDone(X), timesToDo(Y), X < Y.

updateBeliefs(repeatMe, R) :- timesDone(X), Y is X + 1, retract(timesDone(X)), assert(timesDone(Y)), printDoneStatements.

updateBeliefs(_,_) :- printDoneStatements.

printDoneStatements :- ansi_format([fg(red)], 'Printing done statements...\n', []), foreach(done(X,Y), ansi_format([fg(red)], 'done(~w, ~w)\n', [X, Y])).