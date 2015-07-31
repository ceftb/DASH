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
