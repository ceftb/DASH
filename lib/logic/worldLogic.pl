:- dynamic(id/1).
:- dynamic(observations/2).
:- dynamic(i/1).
i(0).

%processAction(_, ID, I) :- i(I), retract(i(I)), J is I + 1, assert(i(J)).

%processACtion(_, ID, I) :- J is ID mod 2, J is 0,

% by default, the result is just res
processAction(A, ID , res) :- forall(id(Observer), updateObservations(Observer, observation(A, ID, res))).

% we should always have observations(ID, L) if ID is legitimate. L may be [].
%updateObservations(Observer, Observation) :- not(observations(Observer, L)), assert(observations(Observer, [Observation])).
updateObservations(Observer, Observation) :- observations(Observer, L), retract(observations(Observer, L)), assert(observations(Observer, [Observation | L])).

getObservations(Observer, Observations) :- observations(Observer, Observations), retract(observations(Observer, Observations)), assert(observations(Observer, [])).