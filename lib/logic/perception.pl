% note that we reverse the observations as the observations
% are provided in reverse chronological order from the hub
% - it is more efficient to reverse it at one time here

:- dynamic(observations/1).
:- dynamic(perceive/1).

perception :- observations(Observations), reverse(Observations, L), perception(L).
perception :- not(observations(Observations)).

perception([]).

perception([H | T]) :- not(perceive(H)), format('no perceive exists for: ~w\n', [H]), perception(T), !.
perception([H | T]) :- perceive(H), format('perceive exists for: ~w\n', [H]), perception(T), !.
