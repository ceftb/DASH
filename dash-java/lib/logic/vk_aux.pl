%%%% old version for sinmple terms

replaceOccurrences(Item, NewItem, [Head | Rest], [NewItem | NewRest])
:- Head = Item, replaceOccurrences(Item, NewItem, Rest, NewRest), !.

replaceOccurrences(Item, NewItem, [Head | Rest], [Head | NewRest])
:- replaceOccurrences(Item, NewItem, Rest, NewRest).

replaceOccurrences(_, _, [], []).

%%%% updated version for compound terms

substituteOccurrences(Item, NewItem, [Head | Rest], [NewHead | NewRest])
:- functor(Head, Item, NumArgs), functor(NewHead, NewItem, NumArgs), argsEqual(Head, NewHead, NumArgs), substituteOccurrences(Item, NewItem, Rest, NewRest), !.

substituteOccurrences(Item, NewItem, [Head | Rest], [Head | NewRest])
:- substituteOccurrences(Item, NewItem, Rest, NewRest).

substituteOccurrences(_, _, [], []).

%%%% check whether num of args are the same and the args have the same value

argsEqual(A, B, K)
    :- K > 0, KMinusOne is K - 1, argsEqual(A, B, KMinusOne), arg(K, A, X), arg(K, B, X).

argsEqual(A, B, 0)
    :- functor(A, X, N), functor(B, Y, N).

%%%% generates 1 with provided probability

chooseWithProbability(P, 1)
    :- X is random_float, X < P, !.

chooseWithProbability(P, 0).

%%%% choose an integer in a given range with pseudo-uniform distribution

%%%% this is a bit flawed... e.g.: if Min = 0, Max = 2, 0 will appear with prob 1/4, 1 will appear with prob 1/2, 2 will appear with prob 1/4
% chooseInRange(Min, Max, Result)
% :- Difference is Max - Min, X is random_float, Offset is round(X * Difference), Result is Min + Offset.

%%%% fixed version
chooseInRange(Min, Max, Result)
:- Min =< Max, DifferencePlusOne is Max - Min + 1, X is random_float, Offset is floor(X * DifferencePlusOne), Result is Min + Offset.


%%%% used to add an element to the end of a list
addToEnd([H|R], Item, [H|NewList])
:- addToEnd(R, Item, NewList).

addToEnd([], Item, [Item]).