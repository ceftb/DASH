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