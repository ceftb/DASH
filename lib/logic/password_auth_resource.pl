:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(accountExists/2).
:- dynamic(signedIn/3).
:- dynamic(createAccount/3).
:- dynamic(signIn/3).
:- dynamic(signOut/3).

:- consult('agentGeneral').

goal(handleRequests).
goalWeight(handleRequests, 1).

subGoal(handleRequest(createAccount(ID, Username, Password))).
subGoal(handleRequest(signIn(ID, Username, Password))).
subGoal(handleRequest(signOut(ID, Username, Password))).

primitiveAction(resetRequirements).
primitiveAction(doNothing).

% handle requests from various users
goalRequirements(handleRequests, [handleRequest(createAccount(ID, Username, Password))]) :- createAccount(ID, Username, Password), retract(createAccount(ID, Username, Password)), assert(requirementsSet([handleRequest(createAccount(ID, Username, Password))])).
goalRequirements(handleRequests, [handleRequest(signIn(ID, Username, Password))]) :- signIn(ID, Username, Password), retract(signIn(ID, Username, Password)), assert([handleRequest(signIn(ID, Username, Password))]).
goalRequirements(handleRequests, [handleRequest(signOut(ID, Username, Password))]) :- signOut(ID, Username, Password), retract(signOut(ID, Username, Password)), assert([handleRequest(signOut(ID, Username, Password))]).
goalRequirements(handleRequests, [doNothing]).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% handle account creation request
%   - if account has not been created yet, create the account, else do not.
%   - also, let the requester know whether the attempt was successful.
%   - this could be extended for username password requirements.
%   for example, if a username or password is deemed weak, a failure message
%   could indicate what password requirements were not met.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
goalRequirements(handleRequest(createAccount(RequesterID, Username, Password)), [callPerson(RequesterID, createAccountResult(MyID, Username, Password, success)), resetRequirements])
:- id(MyID), not(accountExists(Username, Password)), assert(accountExists(Username, Password)).

goalRequirements(handleRequest(createAccount(RequesterID, Username, Password)), [callPerson(RequesterID, createAccountResult(MyID, Username, Password, accountExists)), resetRequirements])
:- id(MyID), accountExists(Username, Password).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% handle sign in request
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

goalRequirements(handleRequest(signIn(RequesterID, Username, Password)), [callPerson(RequesterID, signInResult(MyID, Username, Password, success)), resetRequirements])
:- id(MyID), not(signedIn(_, Username, Password)), assert(signedIn(RequesterID, Username, Password)).

goalRequirements(handleRequest(signIn(RequesterID, Username, Password)), [callPerson(RequesterID, signInResult(MyID, Username, Password, alreadySignedIn)), resetRequirements])
:- id(MyID), signedIn(RequesterID, Username, Password).

goalRequirements(handleRequest(signIn(RequesterID, Username, Password)), [callPerson(RequesterID, signInResult(MyID, Username, Password, signedInElsewhere)), resetRequirements])
:- id(MyID), signedIn(AnotherID, Username, Password), not(AnotherID is RequesterID).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% handle sign out request
%   - temporarily always results in success
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

goalRequirements(handleRequest(signOut(RequesterID, Username, Password)), [callPerson(RequesterID, signOutResult(MyID, Username, Password, success)), resetRequirements])
:- id(MyID), retractall(signedIn(_, Username, Password)).

updateBeliefs(resetRequirements) :- retract(requirementsSet(X)).

updateBeliefs(_,_).