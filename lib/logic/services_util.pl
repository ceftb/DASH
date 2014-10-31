%%%%%%%%%%%
% general %
%%%%%%%%%%%

% merge two lists
%   first argument is first list
%   second argument is second list
%   third argument is merged list
mergeLists([First | Rest], List2, [First | NewList]) :- mergeLists(Rest, List2, NewList), !.
mergeLists([], List2, List2).

% maxPairList
% find the pair with maximum weight in a list of form [(Value1, Weight1), (Value2, Weight2), ...]
maxPairList([(V1, W1) | Rest], (VMax, WMax)) :- maxPairListHelper([(V1, W1) | Rest], (V1, W1), (VMax,WMax)).

maxPairListHelper([(V1, W1) | Rest], (VPrevMax, WPrevMax), (VMax, WMax)) :- maxPair((V1, W1), (VPrevMax, WPrevMax), (VNew, WNew)), maxPairListHelper(Rest, (VNew, WNew), (VMax, WMax)).
maxPairListHelper([], (VMax, WMax), (VMax, WMax)).

maxPair((V1, W1), (V2, W2), (V1, W1)) :- W1 >= W2.
maxPair((V1, W1), (V2, W2), (V2, W2)) :- W1 < W2.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% username and password parsing %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% given a string String and a set of requirements Requirements, this generates
% a list of requirements from Requirements that are not met
getUnsatisfiedRequirements(String, Requirements, UnsatisfiedRequirements) :- atom_codes(String, Codes), getStringStatistics(Codes, Statistics), getUnsatisfiedReqs(String, Statistics, Requirements, UnsatisfiedRequirements), !.

% helper for getUnsatisfiedRequirements
getUnsatisfiedReqs(String, Statistics, [H|T], [H|URT]) :- not(satisfiesReq(String, Statistics, H)), getUnsatisfiedReqs(String, Statistics, T, URT).
getUnsatisfiedReqs(String, Statistics, [H|T], URT) :- satisfiesReq(String, Statistics, H), getUnsatisfiedReqs(String, Statistics, T, URT).
getUnsatisfiedReqs(String, Statistics, [], []).


% this is met if String satisfies the requirements specified in Requirements
satisfiesRequirements(String, Requirements) :- getUnsatisfiedRequirements(String, Requirements, UnsatisfiedRequirements), UnsatisfiedRequirements = [].

%%%%%%
%%% AN ALTERNATIVE IMLPEMENTATION... this is faster, but other has only one point of failure (easier to maintain)
%%% satisfiesRequirements(String, Requirements) :- atom_codes(String, Codes), getStringStatistics(Codes, Statistics), satisfiesReqs(String, Statistics, Requirements), !.

%%%% helper for satisfiesRequirements
%%% satisfiesReqs(String, Statistics, [H|T]) :- satisfiesReq(String, Statistics, H), satisfiesReqs(String, Statistics, T), !.
%%% satisfiesReqs(String, Statistics, []) :- !.
%%%%%%

% used to determine whether a particular requirement is satisfied
%   the first argument is the string String
%   the second is the statistics for String
%   the third is a particular requirement
satisfiesReq(String, [L, U, D, S], minLength(X)) :- Length is L + U + D + S, Length >= X, !.
satisfiesReq(String, [L, U, D, S], maxLength(X)) :- Length is L + U + D + S, Length =< X, !.
satisfiesReq(String, [L, U, D, S], minLower(X)) :- L >= X, !.
satisfiesReq(String, [L, U, D, S], minUpper(X)) :- U >= X, !.
satisfiesReq(String, [L, U, D, S], minDigit(X)) :- D >= X, !.
satisfiesReq(String, [L, U, D, S], minSpecial(X)) :- S >= X, !.
satisfiesReq(String, [L, U, D, S], isNot(X)) :- not(String = X), !.

% the first argument is the string represented as a list of character codes
% the second argument is a list of statistics of form:
%   [#lower, #upper, #digits, #special]
%   where #X means the number of occurrences of X in the string represented
%   by the the character codes given in the first argument
getStringStatistics([H|T], [NewL, U, D, S]) :- char_type(H, lower), getStringStatistics(T, [L, U, D, S]), NewL is L + 1.
getStringStatistics([H|T], [L, NewU, D, S]) :- char_type(H, upper), getStringStatistics(T, [L, U, D, S]), NewU is U + 1.
getStringStatistics([H|T], [L, U, NewD, S]) :- char_type(H, digit), getStringStatistics(T, [L, U, D, S]), NewD is D + 1.
getStringStatistics([H|T], [L, U, D, NewS]) :- not(char_type(H, alnum)), getStringStatistics(T, [L, U, D, S]), NewS is S + 1.
getStringStatistics([], [0, 0, 0, 0]).