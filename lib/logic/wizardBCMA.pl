% -*- Mode: Prolog -*-

% This file is not changed by the wizard and contains whatever extra prolog
% is needed to make the agent work.

:-consult('wizardBCMA_agent').

createProtocol(Patient,Meds,[eMAR_Review(Patient),
	 retrieveMeds(Patient, Meds),
	 scan(Patient),
         scan(Meds),
         deliver(Meds, Patient),
         document(Meds, Patient)]).


% If system 1 doesn't make a decision about whether an action is ok,
% envision and see if we prefer the plan.
% WARNING: ONLY WORKS WHEN THE ACTION IS THE FIRST STEP IN THE PLAN.
system2Fact(ok(performInPlan(Action,[Action|Rest]))) :- 
	incr(envision), preferPlan([Action|Rest],Rest,[]).

% Mental model stuff is being added into the wizard using bcma.pl as an 
% example.

% This prolog goal should be added from the protocol clause (which is
% the only reason it's there) allowing me to add this in the wizard
requiredMeds(johnDoe, [percocet]).
