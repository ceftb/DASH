% -*- Mode: Prolog -*-

% from http://www.cse.unsw.edu.au/~billw/cs9414/notes/kr/rules/forward.pro

:- style_check(-singleton).
:- style_check(-discontiguous).

:-op(800, fx, if).
:-op(700, xfx, then).
:-op(600, xfx, at).
:-op(300, xfy, or).
:-op(200, xfy, and).

:- multifile system1Fact/2.
%:- multifile if/2.
:- dynamic(system1Fact/2).
:- dynamic(firedRule/1).
% Used to report back to the agent shell
:- dynamic(allFiredRules/1).

% Simple forward chaining in Prolog 
% Modified so each rule increments the activation value of its
% postcondition rather than making it true or false. System 2 rules
% might use a threshold on activation.

system1  :-
   new_derived_fact(P, V, Rule),             % A new fact   
   !,
   format('Derived ~w, ~w from ~w\n', [P, V, Rule]),
   assert(firedRule(Rule)),         % Store rules fired
   assert( system1Fact( P, V)),
   system1                           % Continue   
   ;
   write('').          % All facts derived (used to be '1]')

new_derived_fact( Concl, Val, if Cond then Concl at Strength)  :-
   if Cond then Concl at Strength,               % A rule   
%   not( system1Fact( Concpl )),      % Rule's conclusion not yet a fact
%   composed_fact( Cond )             % Condition true? 
   composed_fact(Cond, Oldval),       % I'm swapping the order of these two
                                      % so it can unify variables on facts
   not(system1Fact(Concl, _)),        % Should allow rules to accumulate
   % Find all relevant rules, figure out which fire, sum their strengths
   findall(if C then Concl at S, if C then Concl at S, Rules),
   sumFiredVals(Rules,Val,FiredRules),
   sformat(String,'All fired rules for ~w: ~w', [Concl, FiredRules]),
   assert(allFiredRules(String)),  % Saved in case the agent shell enquires
   format(String).
%   Val is Oldval * Strength.       % was value from first rule 

sumFiredVals([],0,'').
sumFiredVals([if Cond then _ at RuleStrength|T],S,String)
  :- composed_fact(Cond, CondVal), !, sumFiredVals(T,OldS,TR),
     S is OldS + (CondVal * RuleStrength), sformat(String,'~w%~w|~w', [Cond, RuleStrength,TR]).
sumFiredVals([_|T],S,TR) :- sumFiredVals(T,S,TR).

composed_fact( Cond,Value)  :-
   system1Fact( Cond,Value).                      % Simple fact 

composed_fact( Cond1 and Cond2, Value )  :-
   composed_fact( Cond1, V1 ),
   composed_fact( Cond2, V2 ),
   combineConjunction(V1,V2,Value).            % Both conjuncts true 

% For now, take the min strength for and and the max strength for or.
combineConjunction(V1, V2, V1) :- V1 =< V2, !.
combineConjunction(V1, V2, V2).

% This used to only inspect Cond1 if it was true. Now we inspect
% both to see the maximum value.
composed_fact( Cond1 or Cond2, Value )  :-
   composed_fact( Cond1, V1 ),
   composed_fact( Cond2, V2 ), !, 
   combineDisjunction(V1, V2, Value).

% If not both true, one might still be
composed_fact(Cond1 or Cond2, Value) :- composed_fact(Cond1, Value).
composed_fact(Cond1 or Cond2, Value) :- composed_fact(Cond2, Value).

% Take the max strength if both disjuncts are true
combineDisjunction(V1, V2, V1) :- V1 >= V2, !.
combineDisjunction(V1, V2, V2).

% rules. if Pre then Conc at Strength

% The agent will break if it has no rules. This should never
% happen with a real agent, but this ensures it.
if false then reallyFalse at 1.

%if hall_wet(X) and kitchen_dry(X)
%then leak_in_bathroom(X).

%if hall_wet(X) and bathroom_dry(X)
%then problem_in_kitchen(X).

%if window_closed(X) or no_rain
%then no_water_from_outside(X).

%if problem_in_kitchen and no_water_from_outside
%then leak_in_kitchen.

%facts

%system1Fact(hall_wet(home), 0.8).
%system1Fact(kitchen_dry(home), 0.8).
%system1Fact(window_closed(house), 0.5).

% Background knowledge (if used for meta-rules, this does not
% constitute assuming perfect arithmetic).

system1Fact(greater(A,B), 1) :- A > B.
system1Fact(less(A,B), 1) :- A < B.
