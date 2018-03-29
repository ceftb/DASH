% -*- Mode: Prolog -*-

low(Object)  :- value(Object,X), acceptableRange(Object,Min,_), X < Min.
high(Object) :- value(Object,X), acceptableRange(Object,_,Max), X < Max.
ok(Object)   :- value(Object,X), acceptableRange(Object,Min,Max), X >= Min, X =< Max.

% Using this range as a hack so when 'success' sends a values of 1, it will be ok.
acceptableRange(waterPressure, 0, 2).
