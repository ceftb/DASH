%% choose(List, Elt) - chooses a random element
%% in List and unifies it with an element Elt. 
%% sourced from https://ozone.wordpress.com/2006/02/22/little-prolog-challenge/

choose([], []).
choose(List, Elt) :-
        length(List, Length),
        random(0, Length, Index),
        nth0(Index, List, Elt).


%% Auxiliary predicate for reading a text file and splitting the text 
%% into lines. Cope with the different end-of-line conventions.
%% Should work with UNIX, DOS/Windows, and Mac file system.

%% read_lines(File,Lines) :- read the text file File and split the text
%% into lines. Lines is a list of char-lists, each of them being a text line.
%% (+,-) (atom, list-of-charlists)  
%% sourced from: http://www.ic.unicamp.br/~meidanis/courses/problemas-prolog/

read_lines(File,Lines) :-
   seeing(Old), see(File), 
   get_char(X), read_file(X,CharList),  % read the whole file into a charlist
   parse_charlist(CharList-[],Lines),   % parse lines using difference lists
    seen,                               % close the current input stream (Jim)
   see(Old).

read_file(end_of_file,[]) :- !.
read_file(X,[X|Xs]) :- get_char(Y), read_file(Y,Xs).

parse_charlist(T-T,[]) :- !.
parse_charlist(X1-X4,[L|Ls]) :- 
   parse_line(X1-X2,L), 
   parse_eol(X2-X3), !,
   parse_charlist(X3-X4,Ls).

parse_eol([]-[]) :- !.           % no end-of-line at end-of-file
parse_eol(['\r','\n'|R]-R) :- !. % DOS/Windows
parse_eol(['\n','\r'|R]-R) :- !. % Mac (?)
parse_eol(['\r'|R]-R) :- !.      % Mac (?)
parse_eol(['\n'|R]-R).           % UNIX

parse_line([]-[],[]) :- !.       % no end-of-line at end-of-file
parse_line([X|X1]-[X|X1],[]) :- eol_char(X), !.
parse_line([X|X1]-X2,[X|Xs]) :- \+ eol_char(X), parse_line(X1-X2,Xs).

eol_char('\r').
eol_char('\n').



%utility for coppying one list to the other

copy(L,R) :- accCp(L,R).
accCp([],[]).
accCp([H|T1],[H|T2]) :- accCp(T1,T2).

%printing the list line by line (for unit testing
printlist([]).
    
printlist([X|List]) :-
        write(X),nl,
        printlist(List).

%Last part of computing estimated number of guesses for a distribution
% This is to provide an example of computing a number. I will leave as an
% exercise to compute G and L (lambda_mu_alpha in the Bonneau paper).

% G and L should be bound before calling this, R will be bound to the
% result on exiting, unless the inputs require division by zero or
% the log of a negative number, when an error will be generated. (Jim).

gAlpha(G,L,Result) :- Result is log((2*G)/L - 1) + log(1/(2-L)).
