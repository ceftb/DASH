:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(field/2).
:- dynamic(initialWorld/1).
:- dynamic(signedIn/3).
:- dynamic(requirementsSet/1).
:- dynamic(createAccountResult/4).
:- dynamic(signInResult/4).
:- dynamic(signOutResult/4).
:- dynamic(createdAccount/1).

:- dynamic(desiredUsername/2).
:- dynamic(desiredPassword/2).
:- dynamic(latestResult/2).

% this is asserted during updateBeliefs for the intializeUser primitiveAction
:- dynamic(services/1).
:- dynamic(count/1).

% we borrow maxList/2 from agentGeneral
:- consult('agentGeneral').
:- consult('services_util').

%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%
%%%% parameters %%%%
%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%

initialPasswordForgetRate(0.4).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% iteration stuff
% ...for testing in isolation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% iterations of loop
run :- kIterations(50).
kIterations(K) :- integer(K), K > 1, oneIteration, KMinusOne is K - 1, kIterations(KMinusOne).
kIterations(1) :- oneIteration.

oneIteration :- format('\n\nchoosing action...\n'), system1, do(X), format('chose action ~w\n', X), updateBeliefs(X, 1), system1.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% high level, general, and utility content %%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% high level and general goal content %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% top level goal
goal(doWork).
goalWeight(doWork, 1).

% high level subgoals that can be thought of tasks the agent is working on
subGoal(createAccount(Service)) :- serviceExists(Service).
subGoal(signIn(Service)) :- serviceExists(Service).
subGoal(signOut(Service)) :- serviceExists(Service).
subGoal(resetPassword(Service)) :- serviceExists(Service).

% goal requirements for various goals and subgoals
%goalRequirements(doWork, Requirements) :- sleep(1), not(true).
goalRequirements(doWork, Requirements) :- printUserState, printDoneStatements, not(true).
goalRequirements(doWork, Requirements) :- requirementsSet(Requirements), !.
goalRequirements(doWork, [initializeUser]) :- not(requirementsSet(X)), not(inCurrentWorld(userInitialized)), ansi_format([fg(blue)], 'initializing user.\n', []), !.
goalRequirements(doWork, Requirements) :- not(requirementsSet(X)), chooseService(Service), determineRequirements(Service, Requirements), assert(requirementsSet(Requirements)), ansi_format([fg(blue)], 'new requirements set: ~w\n', [Requirements]), !.

determineRequirements(Service, [createAccount(Service), resetRequirements]) :- not(inCurrentWorld(createdAccount(Service))), !.
%determineRequirements(Service, [Reqs, resetRequirements]) :- R is random(1), nth0(R, [resetPassword(Service)], Reqs), !.
%determineRequirements(Service, [Reqs, resetRequirements]) :- R is random(3), nth0(R, [signIn(Service), signOut(Service), resetPassword(Service)], Reqs), !.
determineRequirements(Service, [Reqs, resetRequirements]) :- R is random(2), nth0(R, [signIn(Service), signOut(Service)], Reqs), !.

% the primitiveAction initializeUser is the very first action the agent performs.
% the purpose is to synchronize the hub with the user
% as a response, the hub returns the list of services available to the user.
% this list of users is then asserted in updateBeliefs
% perhaps, later, we can instead have this result contain more information (e.g., other users)
primitiveAction(initializeUser) :- inCurrentWorld(userInitialized).
primitiveAction(initializeUser) :- not(inCurrentWorld(userInitialized)), initializeUserState.

updateBeliefsHelper(initializeUser, R) :- ansi_format([fg(red)], 'update beliefs called with initializeUser. result: ~w\n', [R]), addToWorld(performed(initializeUser)), addToWorld(R), addToWorld(userInitialized), !.

% this is used to reset the current task the user is working on
% it is executed as the last step to achieving a particular task
executable(resetRequirements).
execute(resetRequirements) :- retractall(requirementsSet(_)), removeFromWorld(setupApproachUsed(_, _)), format('executing ~w.\n', resetRequirements).

% this is ``called'' by initializeUser to initialize user state
initializeUserState :- FirstNameIndex is random(4), nth0(FirstNameIndex, [joe, bob, sally, carol], FirstName), addToWorld(firstName(FirstName)), addToWorld(cognitiveBurden(0)), addToWorld(cognitiveThreshold(15)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% general and utility content %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% check whether a service exists
serviceExists(Service) :- inCurrentWorld(services(Services)), member(Service, Services).

% choose a service at random
chooseService(Service) :- inCurrentWorld(services(Services)), length(Services, Length), ServiceIndex is random(Length), nth0(ServiceIndex, Services, Service).

printUserState :- inCurrentWorld(cognitiveBurden(B)), inCurrentWorld(cognitiveThreshold(T)), ansi_format([fg(magenta)], 'cognitive burden: ~w.\ncognitive threshold: ~w.\n', [B, T]), printUsernameBeliefs, printPasswordBeliefs, printForgetRates, !.
printUserState :- !.

printDoneStatements :- foreach(done(A, B), ansi_format([fg(yellow)], '~w.\n', [done(A, B)])).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% tracking changes to world %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% begin with an empty initial world
initialWorld([]).

% add Fact to world if it is not already part of the world
addToWorld(Fact) :- initialWorld(I), member(Fact, I), !.
addToWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), assert(initialWorld([Fact|I])), assert(Fact).

% remove Fact from world (once) if it is already part of the world
% still works if fact is not part of the world
removeFromWorld(Fact) :- initialWorld(I), not(member(Fact, I)), !.
removeFromWorld(Fact) :- initialWorld(I), member(Fact, I), select(Fact, I, J), retract(initialWorld(I)), assert(initialWorld(J)), !.

% we could have also used the following but it allows for duplicate facts
% -- this may not cause errors but seems semantically incorrect and may lead to errors down the road
% addToWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), assert(initialWorld([Fact|I])), assert(Fact).
% removeFromWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), delete(I,Fact,J), assert(initialWorld(J)), retract(Fact).

% check if a fact exists in the world
inCurrentWorld(Fact) :- initialWorld(World), member(Fact, World).

% check if an action is performed in the world
performed(Action, World) :- member(performed(Action), World).

%%%%%%%%%%%%%%%%%%%%
% planning content %
%%%%%%%%%%%%%%%%%%%%

% The set of mental models determines how the agent estimates the consequences of an action.
mentalModel([user]).

% catch all addSets used for projection
addSets(Action, _, _, [[1.0, performed(Action)]]).

%%%%%%%%%%%%%
% temporary %
%%%%%%%%%%%%%

executable(placeholder).
execute(placeholder).

%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%
%%%% createAccount %%%%
%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%

% remarks:
% - perhaps consider numerous methods for username/password construction... for example, correct-horse-battery-staple method
% - expand on memory model for memorizing and recalling passwords

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% subgoals, primitive actions, and executables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% %

subGoal(attemptCreateAccount(Service)).
primitiveAction(navigateToCreateAccountPage(Service)).
subGoal(enterDesiredUsernameSG(Service)).
primitiveAction(chooseUsername(Service)).
primitiveAction(enterDesiredUsername(Service, Username)) :- inCurrentWorld(desiredUsername(Service, Username)).
subGoal(enterDesiredPasswordSG(Service)).
primitiveAction(choosePassword(Service)).
primitiveAction(enterDesiredPassword(Service, Password)) :- inCurrentWorld(desiredPassword(Service, Password)).
primitiveAction(clickCreateAccountButton(Service, Username, Password)) :- inCurrentWorld(desiredUsername(Service, Username)), inCurrentWorld(desiredPassword(Service, Password)).
subGoal(setupForAccountRetrieval(Service)).
primitiveAction(memorizeUsername(Service)).
primitiveAction(memorizePassword(Service)).
primitiveAction(writeUsernameOnPostIt(Service)).
primitiveAction(writePasswordOnPostIt(Service)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% goal requirements and repeatables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
goalRequirements(createAccount(Service), [attemptCreateAccount(Service), setupForAccountRetrieval(Service)]).

goalRequirements(attemptCreateAccount(Service), [navigateToCreateAccountPage(Service), enterDesiredUsernameSG(Service), enterDesiredPasswordSG(Service), clickCreateAccountButton(Service, Username, Password)]).

goalRequirements(enterDesiredUsernameSG(Service), [chooseUsername(Service), enterDesiredUsername(Service, Username)]).
goalRequirements(enterDesiredPasswordSG(Service), [choosePassword(Service), enterDesiredPassword(Service, Password)]).

goalRequirements(setupForAccountRetrieval(Service), Approach) :- format('subgoal: setup for account retrieval - cp1.\n'), not(inCurrentWorld(setupApproachUsed(Service, _))), format('subgoal: setup for account retrieval - cp2.\n'), chooseSetupApproach(Service, Approach), format('subgoal: setup for account retrieval - cp3.\n'), addToWorld(setupApproachUsed(Service, Approach)).
goalRequirements(setupForAccountRetrieval(Service), Approach) :- inCurrentWorld(setupApproachUsed(Service, Approach)).


% if we only need to do setup for password retrieval
chooseSetupApproach(Service, [memorizePassword(Service)]) :- format('chooseSetupApproach - cp1.\n'), not(inCurrentWorld(usernameSetupRequired(Service, Username))), inCurrentWorld(passwordSetupRequired(Service, Password)), format('chooseSetupApproach - cp2.\n'), inCurrentWorld(cognitiveBurden(B)), inCurrentWorld(cognitiveThreshold(T)), format('chooseSetupApproach - cp3.\n'), X is B + 5, X < T, removeFromWorld(cognitiveBurden(B)), addToWorld(cognitiveBurden(X)), format('chosen setup approach: memorizing username and password.\n').
chooseSetupApproach(Service, [writePasswordOnPostIt(Service)]) :- not(inCurrentWorld(usernameSetupRequired(Service, Username))), inCurrentWorld(passwordSetupRequired(Service, Password)), inCurrentWorld(cognitiveBurden(B)), inCurrentWorld(cognitiveThreshold(T)), X is B + 5, X >= T, format('chosen setup approach: writing username and password to post it notes.\n').

% if we need to do setup for username and password retrieval
chooseSetupApproach(Service, [memorizeUsername(Service), memorizePassword(Service)]) :- format('chooseSetupApproach - cp1.\n'), inCurrentWorld(usernameSetupRequired(Service, Username)), inCurrentWorld(passwordSetupRequired(Service, Password)), format('chooseSetupApproach - cp2.\n'), inCurrentWorld(cognitiveBurden(B)), inCurrentWorld(cognitiveThreshold(T)), format('chooseSetupApproach - cp3.\n'), X is B + 10, X < T, removeFromWorld(cognitiveBurden(B)), addToWorld(cognitiveBurden(X)), format('chosen setup approach: memorizing username and password.\n').
chooseSetupApproach(Service, [writeUsernameOnPostIt(Service), writePasswordOnPostIt(Service)]) :- inCurrentWorld(usernameSetupRequired(Service, Username)), inCurrentWorld(passwordSetupRequired(Service, Password)), inCurrentWorld(cognitiveBurden(B)), inCurrentWorld(cognitiveThreshold(T)), X is B + 10, X >= T, format('chosen setup approach: writing username and password to post it notes.\n').

repeatable(attemptCreateAccount(Service)) :- not(inCurrentWorld(createdAccount(Service))).

repeatable(enterDesiredUsernameSG(Service)) :- inCurrentWorld(usernameProposalResult(Service, _, error(_))).

repeatable(enterDesiredPasswordSG(Service)) :- inCurrentWorld(passwordProposalResult(Service, _, error(_))).

%%%%%%%%%%%%
% executes %
%%%%%%%%%%%%

% if a username has been chosen, nothing need be done for the execute
%execute(chooseUsername(Service)) :- inCurrentWorld(desiredUsername(Service, _)), format('exec username - branch 0!\n', []), !.

% if a username has not been chosen, choose one!
% important: we do NOT try to unify the username in desiredUsername with that from usernameProposalResult
% when they both exist... this is because we may later want to take into account situations where the username
% that is typed in is subject to typos
updateBeliefsHelper(chooseUsername(Service), R) :- not(inCurrentWorld(usernameChosenButNotEntered(Service))), not(inCurrentWorld(desiredUsername(Service, _))), not(inCurrentWorld(usernameProposalResult(Service, _, _))), inCurrentWorld(usernameRequirements(Service, Requirements)), format('chooseUsername: trying to satisfy requirements: ~w.\n', [Requirements]), chooseUsernameHelper(Service, Requirements, '', Username), addToWorld(desiredUsername(Service, Username)), addToWorld(usernameChosenButNotEntered(Service)), format('exec username - branch 1!\n', []), !.

updateBeliefsHelper(chooseUsername(Service), R) :- not(inCurrentWorld(usernameChosenButNotEntered(Service))), inCurrentWorld(desiredUsername(Service, PreviousUsername)), inCurrentWorld(usernameProposalResult(Service, _, error(FailedUsernameRequirements))), inCurrentWorld(usernameRequirements(Service, InitialRequirements)), mergeLists(InitialRequirements, FailedUsernameRequirements, Requirements), removeFromWorld(usernameRequirements(Service, InitialRequirements)), addToWorld(usernameRequirements(Service, Requirements)), format('chooseUsername: trying to satisfy requirements: ~w.\n', [Requirements]), chooseUsernameHelper(Service, Requirements, PreviousUsername, Username), removeFromWorld(desiredUsername(Service, _)), addToWorld(desiredUsername(Service, Username)), addToWorld(usernameChosenButNotEntered(Service)), format('exec username - branch 2!\n', []), !.

%execute(chooseUsername(Service)) :- inCurrentWorld(usernameChosenButNotEntered(Service)), format('already chose a username so skipping this exec!\n', []), !.
updateBeliefsHelper(chooseUsername(Service), R) :- format('catch-all choose username exec!\n', []), !.

chooseUsernameHelper(Service, Requirements, _, 'username') :- satisfiesRequirements('username', Requirements).
chooseUsernameHelper(Service, Requirements, _, 'username1') :- satisfiesRequirements('username1', Requirements).
chooseUsernameHelper(Service, Requirements, _, 'Username12') :- satisfiesRequirements('Username12', Requirements).
chooseUsernameHelper(Service, Requirements, _, 'Us3rN4m3!234') :- satisfiesRequirements('Us3rN4m3!234', Requirements).
chooseUsernameHelper(Service, Requirements, _, Username) :- id(MyID), atom_concat('Us3rN4m3!234', MyID, Username), satisfiesRequirements(Username, Requirements).

%chooseUsernameHelper(Service, Requirements, '', 'username').
%chooseUsernameHelper(Service, Requirements, BaseUsername, Username) :- atom_concat(BaseUsername, '1', Username), !.
%chooseUsernameHelper(Service, Requirements, BaseUsername, Username) :- atom_concat(BaseUsername, 'ABC2', Username), !.
%chooseUsernameHelper(Service, Requirements, BaseUsername, Username) :- atom_concat(BaseUsername, '!3@4F!Nwee', Username), !.


% for passwords!
updateBeliefsHelper(choosePassword(Service), R) :- not(inCurrentWorld(passwordChosenButNotEntered(Service))), not(inCurrentWorld(desiredPassword(Service, _))), not(inCurrentWorld(passwordProposalResult(Service, _, _))), inCurrentWorld(passwordRequirements(Service, Requirements)), choosePasswordHelper(Service, Requirements, '', Password), addToWorld(desiredPassword(Service, Password)), addToWorld(passwordChosenButNotEntered(Service)), format('exec password - branch 1!\n', []), !.

updateBeliefsHelper(choosePassword(Service), R) :- not(inCurrentWorld(passwordChosenButNotEntered(Service))), inCurrentWorld(desiredPassword(Service, PreviousPassword)), inCurrentWorld(passwordProposalResult(Service, _, error(FailedPasswordRequirements))), inCurrentWorld(passwordRequirements(Service, InitialRequirements)), mergeLists(InitialRequirements, FailedPasswordRequirements, Requirements), removeFromWorld(passwordRequirements(Service, InitialRequirements)), addToWorld(passwordRequirements(Service, Requirements)), choosePasswordHelper(Service, Requirements, PreviousPassword, Password), removeFromWorld(desiredPassword(Service, _)), addToWorld(desiredPassword(Service, Password)), addToWorld(passwordChosenButNotEntered(Service)), format('exec password - branch 2!\n', []), !.

updateBeliefsHelper(choosePassword(Service), R) :- format('catch-all choose password exec!\n', []), !.

choosePasswordHelper(Service, Requirements, _, 'pass') :- satisfiesRequirements('pass', Requirements).
choosePasswordHelper(Service, Requirements, _, 'password') :- satisfiesRequirements('password', Requirements).
choosePasswordHelper(Service, Requirements, _, 'Password') :- satisfiesRequirements('Password', Requirements).
choosePasswordHelper(Service, Requirements, _, 'PassWord12') :- satisfiesRequirements('Password12', Requirements).
choosePasswordHelper(Service, Requirements, _, 'P@sSw0rd!234') :- satisfiesRequirements('P@sSw0rd1234', Requirements).
choosePasswordHelper(Service, Requirements, _, 'VeryLonP@sSw0rd!234!?') :- satisfiesRequirements('VeryLongP@sSw0rd1234!?', Requirements).
% instead of using the above model for generating passwords, we may want to do something more interesting with initialized user information

%%% This is the beginning of code for an approach that involves removing one requirement at a time
%%% ... It may be a bit tricky with some combinations of requirements... e.g., maxLength AND min* reqs
% % if there are no requirements left to meet and a base username is supplied use the base username given as the username
% chooseUsernameHelper(Service, [], BaseUsername, BaseUsername) :- BaseUsername \= ''.
%
% % if there are no requirements left to meet and no base username is supplied use the following as the base username
% chooseUsernameHelper(Service, [], '', FirstName) :- firstName(FirstName), !.
%
% % if requirements are left, satisfy the first req and then attempt to satisfy the rest
% chooseUsernameHelper(Service, [FirstReq | Rest], BaseUsername, NewUsername) :- chooseUsernameHelper(Service, Rest, BaseUsername, NewUsername).

%execute(chooseUsername(Service)) :- not(inCurrentWorld(latestResult(enterDesiredUsername(Service, Username), Result))), removeFromWorld(desiredUsername(Service, _)), addToWorld(desiredUsername(Service, test_un)), format('executing ~w - branch 1.\n', chooseUsername(Service)).
%execute(chooseUsername(Service)) :- inCurrentWorld(latestResult(enterDesiredUsername(Service, Username), error(tooShort))), removeFromWorld(desiredUsername(Service, _)), addToWorld(desiredUsername(Service, test_longer_username)), format('executing ~w - branch 2.\n', chooseUsername(Service)), !.
%execute(chooseUsername(Service)) :- not(inCurrentWorld(latestResult(enterDesiredUsername(Service, Username), Result))), inCurrentWorld(latestResult(createAccount(Service, Username, Password), [error(tooShort), _])), removeFromWorld(desiredUsername(Service, _)), addToWorld(desiredUsername(Service, test_longer_username)), format('executing ~w - branch 3.\n', chooseUsername(Service)), !.
%execute(chooseUsername(Service)) :- inCurrentWorld(latestResult(enterDesiredUsername(Service, Username), error(alreadyTaken))), removeFromWorld(desiredUsername(Service, _)), addToWorld(desiredUsername(Service, hopefully_this_is_not_taken)), format('executing ~w - branch 4.\n', chooseUsername(Service)), !.
%execute(chooseUsername(Service)) :- not(inCurrentWorld(latestResult(enterDesiredUsername(Service, Username), Result))), inCurrentWorld(latestResult(createAccount(Service, Username, Password), [error(alreadyTaken), _])), removeFromWorld(desiredUsername(Service, _)), addToWorld(desiredUsername(Service, hopefully_this_is_not_taken)), format('executing ~w - branch 5.\n', chooseUsername(Service)), !.

%execute(choosePassword(Service)) :- not(inCurrentWorld(latestResult(enterDesiredPassword(Service, Password), Result))), removeFromWorld(desiredPassword(Service, _)), addToWorld(desiredPassword(Service, test_pw)), format('executing ~w - branch 1.\n', choosePassword(Service)).
%execute(choosePassword(Service)) :- inCurrentWorld(latestResult(enterDesiredPassword(Service, Password), error(tooShort))), removeFromWorld(desiredPassword(Service, _)), addToWorld(desiredPassword(Service, password1)), format('executing ~w - branch 2.\n', choosePassword(Service)).
%execute(choosePassword(Service)) :- inCurrentWorld(latestResult(enterDesiredPassword(Service, Password), success(weak))), removeFromWorld(desiredPassword(Service, _)), addToWorld(desiredPassword(Service, password1234)), format('executing ~w - branch 3.\n', choosePassword(Service)).
%execute(choosePassword(Service)) :- not(inCurrentWorld(latestResult(enterDesiredPassword(Service, Password), Result))), inCurrentWorld(latestResult(createAccount(Service, Username, Password), [_, error(tooShort)])), removeFromWorld(desiredPassword(Service, _)), addToWorld(desiredPassword(Service, password1)), format('executing ~w - branch 4.\n', choosePassword(Service)).
%execute(choosePassword(Service)) :- not(inCurrentWorld(latestResult(enterDesiredPassword(Service, Password), Result))), inCurrentWorld(latestResult(createAccount(Service, Username, Password), [_, success(weak)])), removeFromWorld(desiredPassword(Service, _)), addToWorld(desiredPassword(Service, password1234)), format('executing ~w - branch 5.\n', choosePassword(Service)).

%%%%%%%%%%%%%%%%%
% updateBeliefs %
%%%%%%%%%%%%%%%%%

updateBeliefsHelper(navigateToCreateAccountPage(Service), success(usernameRequirements(UR), passwordRequirements(PR))) :- not(inCurrentWorld(userRequirements(Service, _))), not(inCurrentWorld(passwordRequirements(Service, _))), addToWorld(usernameRequirements(Service, UR)), addToWorld(passwordRequirements(Service, PR)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [navigateToCreateAccountPage(Service), success(usernameRequirements(UR), passwordRequirements(PR))]), !.
updateBeliefsHelper(navigateToCreateAccountPage(Service), success(usernameRequirements(UR), passwordRequirements(PR))) :- inCurrentWorld(usernameRequirements(Service, _)), inCurrentWorld(passwordRequirements(Service, _)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [navigateToCreateAccountPage(Service), success(usernameRequirements(UR), passwordRequirements(PR))]), !.
updateBeliefsHelper(navigateToCreateAccountPage(Service), Result) :- ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w/. Should not be here!\n', [navigateToCreateAccountPage(Service), Result]), !.

updateBeliefsHelper(enterDesiredUsername(Service, Username), Result) :- removeFromWorld(usernameProposalResult(Service, _, _)), addToWorld(usernameProposalResult(Service, Username, Result)), removeFromWorld(usernameChosenButNotEntered(Service)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [enterDesiredUsername(Service, Username), Result]), !.

updateBeliefsHelper(enterDesiredPassword(Service, Password), Result) :- removeFromWorld(passwordProposalResult(Service, _, _)), addToWorld(passwordProposalResult(Service, Password, Result)), removeFromWorld(passwordChosenButNotEntered(Service)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [enterDesiredPassword(Service, Password), Result]), !.

updateBeliefsHelper(clickCreateAccountButton(Service, Username, Password), success) :- removeFromWorld(usernameProposalResult(Service, _, _)), removeFromWorld(passwordProposalResult(Service, _, _)), removeFromWorld(desiredUsername(Service, _)), removeFromWorld(desiredPassword(Service, _)), removeFromWorld(passwordRequirements(Service, _)), addToWorld(createdAccount(Service)), addToWorld(usernameSetupRequired(Service, Username)), addToWorld(passwordSetupRequired(Service, Password)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [clickCreateAccountButton(Service, Username, Password), success]).
updateBeliefsHelper(clickCreateAccountButton(Service, Username, Password), error(UResult, PResult)) :- removeFromWorld(usernameProposalResult(Service, _, _)), removeFromWorld(passwordProposalResult(Service, _, _)), addToWorld(usernameProposalResult(Service, Username, UResult)), addToWorld(passwordProposalResult(Service, Password, PResult)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [clickCreateAccountButton(Service, Username, Password), error(UResult, PResult)]).


% usernameSetupRequired and passwordSetupRequired are temporarily used to store the username and password
% for agent recall, we must used something else that is set up here...
% right now, the basic model I am just using has form usernameBeliefs(Service, [(username1, strength1), (username2, strength2),...]
% the idea is that whenever a username is used correctly, belief in that username is set to 1 while the others are set to 0
% however, every agent "step" for which it is not used, the strengths of usernames used for the service is spread over all usernames
% used over all services. The rate of spread could also be a factor of how many times the username was remembered correctly for the service
% ... so, for example, if you use a username once, you're likely to forget it; if you use it 100 times, you'll be more likely to remember it in the future
% and the rate at which you forget it will decline.

updateBeliefsHelper(memorizeUsername(Service), Result) :- inCurrentWorld(usernameSetupRequired(Service, Username)), removeFromWorld(usernameSetupRequired(Service, Username)), addToWorld(usernameBeliefs(Service, [(Username, 1)])), format('memorized username ~w.\n', [Username]).
updateBeliefsHelper(memorizeUsername(Service), Result) :- not(inCurrentWorld(usernameSetupRequired(Service, _))).

updateBeliefsHelper(memorizePassword(Service), Result) :- inCurrentWorld(passwordSetupRequired(Service, Password)), removeFromWorld(passwordSetupRequired(Service, Password)), not(inCurrentWorld(passwordBeliefs(Service, _))), addToWorld(passwordBeliefs(Service, [(Password, 1)])), initialPasswordForgetRate(Rate), addToWorld(passwordForgetRate(Service, Rate)), format('memorized password ~w.\n', [Password]).
updateBeliefsHelper(memorizePassword(Service), Result) :- inCurrentWorld(passwordSetupRequired(Service, Password)), removeFromWorld(passwordSetupRequired(Service, Password)), inCurrentWorld(passwordBeliefs(Service, _)), removeFromWorld(passwordBeliefs(Service, _)), addToWorld(passwordBeliefs(Service, [(Password, 1)])), initialPasswordForgetRate(Rate), removeFromWorld(passwordForgetRate(Service, _)), addToWorld(passwordForgetRate(Service, Rate)), format('executing ~w.\n', [memorizePassword(Service)]).
updateBeliefsHelper(memorizePassword(Service), Result) :- not(inCurrentWorld(passwordSetupRequired(Service, _))).


updateBeliefsHelper(writeUsernameOnPostIt(Service), Result) :- inCurrentWorld(usernameSetupRequired(Service, Username)), removeFromWorld(usernameSetupRequired(Service, Username)), addToWorld(usernameBeliefs(Service, [(Username, 0.5)])), addToWorld(wroteUsernameOnPostIt(Service, Username)), format('executing ~w.\n', [writeUsernameOnPostIt(Service)]).
updateBeliefsHelper(writeUsernameOnPostIt(Service), Result) :- not(inCurrentWorld(usernameSetupRequired(Service, _))).

updateBeliefsHelper(writePasswordOnPostIt(Service), Result) :- inCurrentWorld(passwordSetupRequired(Service, Password)), removeFromWorld(passwordSetupRequired(Service, Password)), not(inCurrentWorld(passwordBeliefs(Service, _))), addToWorld(passwordBeliefs(Service, [(Password, 0.5)])), addToWorld(wrotePasswordOnPostIt(Service, Password)), initialPasswordForgetRate(Rate), addToWorld(passwordForgetRate(Service, Rate)), format('executing ~w. \n', [writePasswordOnPostIt(Service)]).
updateBeliefsHelper(writePasswordOnPostIt(Service), Result) :- inCurrentWorld(passwordSetupRequired(Service, Password)), removeFromWorld(passwordSetupRequired(Service, Password)), inCurrentWorld(passwordBeliefs(Service, _)), removeFromWorld(passwordBeliefs(Service, _)), addToWorld(passwordBeliefs(Service, [(Password, 0.5)])), addToWorld(wrotePasswordOnPostIt(Service, Password)), initialPasswordForgetRate(Rate), removeFromWorld(passwordForgetRate(Service, _)), addToWorld(passwordForgetRate(Service, Rate)), format('executing ~w. Setting NEW Password\n', [writePasswordOnPostIt(Service)]).
updateBeliefsHelper(writePasswordOnPostIt(Service), Result) :- not(inCurrentWorld(passwordSetupRequired(Service, _))).

%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%
%%%% signIn %%%%
%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% subgoals, primitive actions, and executables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% %

%%%%%%%% later...
%%%%%%%% we want subgoal: retrieveAccountInformation
%%%%%%%% which can be achieved by goal reqs like...
%%%%%%%%    recallUsername(Service), recallPassword(Service)
%%%%%%%%    readUsernameOffPostIt(Service), readPasswordOffPostIt(Service)
%%%%%%%%    findFileContainingAccountInformation(Service), readUsernameFromFile(Service), readPasswordFromFile(service)

% subgoals, primitive actions, and executables associated with signing in
subGoal(attemptSignIn(Service)).
subGoal(retrieveAndEnterAccountInformation(Service)).
primitiveAction(recallAndEnterUsername(Service, Username)) :- recallUsername(Service, Username), !.
primitiveAction(recallAndEnterPassword(Service, Password)) :- recallPassword(Service, Password), !.
primitiveAction(clickSignInButton(Service, Username, Password)) :- inCurrentWorld(retrievedUsername(Service, Username)), inCurrentWorld(retrievedPassword(Service, Password)), !.
primitiveAction(readAndEnterUsername(Service, Username)) :- readUsernameOffPostIt(Service, Username), !.
primitiveAction(readAndEnterPassword(Service, Password)) :- readPasswordOffPostIt(Service, Password), !.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% goal requirements and repeatables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% signIn goal requirements

goalRequirements(signIn(Service), [attemptSignIn(Service)]) :- format('expanding goal reqs for sign in - cp1.\n'), inCurrentWorld(createdAccount(Service)), not(inCurrentWorld(signedIn(Service, _, _))), format('expanding goal reqs for sign in - cp2.\n'), !.
goalRequirements(signIn(Service), []) :- inCurrentWorld(createdAccount(Service)), inCurrentWorld(signedIn(Service, _, _)), !.

repeatable(attemptSignIn(Service)) :- not(inCurrentWorld(signedIn(Service, _, _))), !.

% To sign in, the agent must retrieve their accountinformation and enter it.
goalRequirements(attemptSignIn(Service), [retrieveAndEnterAccountInformation(Service), clickSignInButton(Service, Username, Password)]).

goalRequirements(retrieveAndEnterAccountInformation(Service), [recallAndEnterUsername(Service, Username), recallAndEnterPassword(Service, Password)]).
goalRequirements(retrieveAndEnterAccountInformation(Service), [readAndEnterUsername(Service, Username), readAndEnterPassword(Service, Password)]).
goalRequirements(retrieveAndEnterAccountInformation(Service), [resetPassword(Service), retrieveAndEnterAccountInformation(Service)]) :- ansi_format([fg(green)], 'retrieveAndEnterAccountInformation(Service) - resetPassword(Service) branch... This is incorrect. Need to change resetPassword so that it does not reset requirements!\n', []), removeFromWorld(retrievedUsername(Service, _)), removeFromWorld(retrievedPassword(Service, _)).

%%%%%%%%%%%%
% executes %
%%%%%%%%%%%%

% there are none right now!

%%%%%%%%%%%%
% utility  %
%%%%%%%%%%%%

recallUsername(Service, Username) :- not(inCurrentWorld(retrievedUsername(Service, Username))), usernameBeliefs(Service, List), maxPairList(List, (Username, Weight)), Weight > 0.5, addToWorld(retrievedUsername(Service, Username)), !.

recallPassword(Service, Password) :- not(inCurrentWorld(retrievedPassword(Service, Password))), passwordBeliefs(Service, List), maxPairList(List, (Password, Weight)), Weight > 0.5, addToWorld(retrievedPassword(Service, Password)), !.

readUsernameOffPostIt(Service, Username) :- not(inCurrentWorld(retrievedUsername(Service, _))), wroteUsernameOnPostIt(Service, Username), addToWorld(retrievedUsername(Service, Username)), !.

readPasswordOffPostIt(Service, Password) :- not(inCurrentWorld(retrievedPassword(Service, _))), wrotePasswordOnPostIt(Service, Password), addToWorld(retrievedPassword(Service, Password)), !.

signInSucceeded(Service, Username, Password) :- addToWorld(signedIn(Service, Username, Password)), removeFromWorld(retrievedUsername(Service, _)), removeFromWorld(retrievedPassword(Service, _)).
signInFailed(Service, Username, Password) :- removeFromWorld(retrievedUsername(Service, _)), removeFromWorld(retrievedPassword(Service, _)).

%%%%%%%%%%%%%%%%%
% updateBeliefs %
%%%%%%%%%%%%%%%%%

updateBeliefsHelper(clickSignInButton(Service, Username, Password), success) :- signInSucceeded(Service, Username, Password), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [clickSignInButton(Service, Username, Password), success]).

updateBeliefsHelper(clickSignInButton(Service, Username, Password), error(Result)) :- signInFailed(Service, Username, Password), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w... this case still needs to be implemented!\n', [clickSignInButton(Service, Username, Password), error(Result)]).

%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%
%%%% signOut %%%%
%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% subgoals, primitive actions, and executables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% %

subGoal(attemptSignOut(Service)).
primitiveAction(clickSignOutButton(Service, Username)) :- inCurrentWorld(signedIn(Service, Username, _)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% goal requirements and repeatables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

goalRequirements(signOut(Service), [attemptSignOut(Service)]) :- inCurrentWorld(createdAccount(Service)), inCurrentWorld(signedIn(Service, _, _)), !.
goalRequirements(signOut(Service), []) :- inCurrentWorld(createdAccount(Service)), not(inCurrentWorld(signedIn(Service, _, _))), !.

goalRequirements(attemptSignOut(Service), [clickSignOutButton(Service, Username)]).


%%%%%%%%%%%%
% executes %
%%%%%%%%%%%%

% no executes!

%%%%%%%%%%%%%%%%%
% updateBeliefs %
%%%%%%%%%%%%%%%%%

updateBeliefsHelper(clickSignOutButton(Service, Username), success) :- removeFromWorld(signedIn(Service, Username, _)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [clickSignOutButton(Service, Username), success]).

updateBeliefsHelper(clickSignOutButton(Service, Username), error(Result)) :- ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w... this case still needs to be implemented!\n', [clickSignOutButton(Service, Username), error(Result)]).

%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%
%%%% resetPassword %%%%
%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% subgoals, primitive actions, and executables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% %

subGoal(attemptResetPassword(Service)).
primitiveAction(navigateToResetPasswordPage(Service)).
subGoal(retrieveAndEnterUsername(Service)).
subGoal(setupForNewPasswordRetrieval(Service)).
primitiveAction(chooseNewPassword(Service)).
primitiveAction(clickResetPasswordButton(Service, Username, Password)) :- inCurrentWorld(desiredPassword(Service, Password)), inCurrentWorld(retrievedUsername(Service, Username)).
subGoal(attemptResetPassword(Service, Password)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% goal requirements and repeatables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

goalRequirements(resetPassword(Service), [attemptResetPassword(Service), setupForAccountRetrieval(Service)]).

goalRequirements(attemptResetPassword(Service), [navigateToResetPasswordPage(Service), retrieveAndEnterUsername(Service), chooseNewPassword(Service), clickResetPasswordButton(Service, Username, Password)]).

goalRequirements(retrieveAndEnterUsername(Service), [recallAndEnterUsername(Service, Username)]).
goalRequirements(retrieveAndEnterUsername(Service), [readAndEnterUsername(Service, Username)]).
goalRequirements(retrieveAndEnterUsername(Service), []) :- ansi_format([fg(green)], 'retrieveAndEnterUsername(Service) - nil branch... This should not happen!\n', []), removeFromWorld(retrievedUsername(Service, _)).

repeatable(attemptResetPassword(Service)) :- inCurrentWorld(passwordProposalResult(Service, _, error(_))).

%%%%%%%%%%%%
% executes %
%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%
% updateBeliefs %
%%%%%%%%%%%%%%%%%

updateBeliefsHelper(navigateToResetPasswordPage(Service), success(passwordRequirements(PR))) :- not(inCurrentWorld(passwordRequirements(Service, _))), addToWorld(passwordRequirements(Service, PR)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [navigateToResetPasswordPage(Service), success(passwordRequirements(PR))]), !.
updateBeliefsHelper(navigateToResetPasswordPage(Service), success(passwordRequirements(PR))) :- inCurrentWorld(passwordRequirements(Service, _)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [navigateToResetPasswordPage(Service), success(passwordRequirements(PR))]), !.
updateBeliefsHelper(navigateToResetPasswordPage(Service), Result) :- ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w/. Should not be here!\n', [navigateToResetPasswordPage(Service), Result]), !.

updateBeliefsHelper(clickResetPasswordButton(Service, Username, Password), success) :- removeFromWorld(desiredPassword(Service, _)), removeFromWorld(passwordRequirements(Service, _)), removeFromWorld(passwordProposalResult(Service, _, _)), removeFromWorld(passwordChosenButNotEntered(Service)), removeFromWorld(retrievedUsername(Service, _)), addToWorld(passwordSetupRequired(Service, Password)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [clickResetPasswordButton(Service, Username, Password), success]).
updateBeliefsHelper(clickResetPasswordButton(Service, Username, Password), Result) :- Result = error(Reason), Reason \= noService, Reason \= noUsername, removeFromWorld(passwordProposalResult(Service, _, _)), removeFromWorld(passwordChosenButNotEntered(Service)), removeFromWorld(retrievedUsername(Service, _)), addToWorld(passwordProposalResult(Service, Password, Result)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [clickResetPasswordButton(Service, Username, Password), Result]).

updateBeliefsHelper(chooseNewPassword(Service), R) :- not(inCurrentWorld(passwordChosenButNotEntered(Service))), not(inCurrentWorld(desiredPassword(Service, _))), not(inCurrentWorld(passwordProposalResult(Service, _, _))), inCurrentWorld(passwordRequirements(Service, Requirements)), choosePasswordHelper(Service, Requirements, '', Password), addToWorld(desiredPassword(Service, Password)), addToWorld(passwordChosenButNotEntered(Service)), format('exec choose new password - branch 1!\n', []), !.

updateBeliefsHelper(chooseNewPassword(Service), R) :- not(inCurrentWorld(passwordChosenButNotEntered(Service))), inCurrentWorld(desiredPassword(Service, PreviousPassword)), inCurrentWorld(passwordProposalResult(Service, _, error(FailedPasswordRequirements))), inCurrentWorld(passwordRequirements(Service, InitialRequirements)), mergeLists(InitialRequirements, FailedPasswordRequirements, Requirements), removeFromWorld(passwordRequirements(Service, InitialRequirements)), addToWorld(passwordRequirements(Service, Requirements)), choosePasswordHelper(Service, Requirements, PreviousPassword, Password), removeFromWorld(desiredPassword(Service, _)), addToWorld(desiredPassword(Service, Password)), addToWorld(passwordChosenButNotEntered(Service)), format('exec choose new password - branch 2!\n', []), !.

updateBeliefsHelper(chooseNewPassword(Service), R) :- format('catch-all choose new password exec!\n', []), !.

%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%
%%%% template %%%%
%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% subgoals, primitive actions, and executables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% %

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% goal requirements and repeatables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%
% executes %
%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%
% updateBeliefs %
%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% more utility content, which must be placed at the end of this file %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% the default updateBeliefs if nothing is specified
updateBeliefs(Action, Result) :- updateUsernameBeliefs(Action, Result), updatePasswordBeliefs(Action, Result), updateBeliefsHelper(Action, Result), !.

updateBeliefs(Action, Result) :- not(updateBeliefsHelper(Action, Result)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w (default call)\n', [Action, Result]), !.

updateUsernameBeliefs(_, _) :- !.

updatePasswordBeliefs(clickSignInButton(Service, Username, Password), success) :- inCurrentWorld(services(Services)), inCurrentWorld(passwordBeliefs(Service, PasswordBeliefs)), removeFromWorld(passwordBeliefs(Service, _)), addToWorld(passwordBeliefs(Service, [(Password, 1)])), removeFromWorld(passwordForgetRate(Service, R)), NewR is R / 2, addToWorld(passwordForgetRate(Service, NewR)), uniquePasswords(UniquePasswords), foreach(member(MemberService, Services), addUniquePasswords(MemberService, UniquePasswords)), delete(Services, Service, ServicesDifferentThanMe), foreach(member(MemberService, ServicesDifferentThanMe), strengthenPassword(MemberService, Password)), foreach(member(MemberService, Services), passwordFatigue(MemberService)), !.
updatePasswordBeliefs(clickSignInButton(Service, Username, Password), error(passwordIncorrect)) :- inCurrentWorld(services(Services)), inCurrentWorld(passwordBeliefs(Service, PasswordBeliefs)), removeFromWorld(passwordBeliefs(Service, _)), delete(PasswordBeliefs, [Password, _], NewPasswordBeliefs), addToWorld(passwordBeliefs(Service, NewPasswordBeliefs)), removeFromWorld(passwordForgetRate(Service, R)), NewR is R * 2, addToWorld(passwordForgetRate(Service, NewR)), uniquePasswords(UniquePasswords), foreach(member(MemberService, Services), addUniquePasswords(MemberService, UniquePasswords)), foreach(member(MemberService, Services), passwordFatigue(MemberService)), !.

updatePasswordBeliefs(Action, Result) :- Action = clickSignInButton(_, _, _), Result \= error(passwordIncorrect), Result \= success, inCurrentWorld(services(Services)), uniquePasswords(UniquePasswords), foreach(member(Service, Services), addUniquePasswords(Service, UniquePasswords)), foreach(member(Service, Services), passwordFatigue(Service)), !.
updatePasswordBeliefs(Action, Result) :- Action \= clickSignInButton(_, _, _), inCurrentWorld(services(Services)), uniquePasswords(UniquePasswords), foreach(member(Service, Services), addUniquePasswords(Service, UniquePasswords)), foreach(member(Service, Services), passwordFatigue(Service)), !.
updatePasswordBeliefs(Action, Result) :- not(inCurrentWorld(services(Services))), !.

strengthenPassword(Service, Password) :- inCurrentWorld(passwordBeliefs(Service, PasswordBeliefs)), inCurrentWorld(passwordForgetRate(Service, Rate)), member((Password, Strength), PasswordBeliefs), removeFromWorld(passwordBeliefs(Service, _)), delete(PasswordBeliefs, (Password, _), PasswordBeliefsModified), NewStrength is min(Strength + Rate, 1), NewPasswordBeliefs = [(Password, NewStrength)|PasswordBeliefsModified], addToWorld(passwordBeliefs(Service, NewPasswordBeliefs)), !.
strengthenPassword(Service, Password) :- not(inCurrentWorld(passwordBeliefs(Service, _))), !.

addUniquePasswords(Service, [Password|Rest]) :- isPassword(Service, Password), addUniquePasswords(Service, Rest), !.
addUniquePasswords(Service, [Password|Rest]) :- not(isPassword(Service, Password)), inCurrentWorld(passwordBeliefs(Service, List)), append([(Password, 0)], List, NewList), removeFromWorld(passwordBeliefs(Service, __)), addToWorld(passwordBeliefs(Service, NewList)), addUniquePasswords(Service, Rest), !.
addUniquePasswords(Service, [Password|Rest]) :- not(isPassword(Service, Password)), not(inCurrentWorld(passwordBeliefs(Service, _))), !.
addUniquePasswords(Service, []) :- !.

uniquePasswords(UniquePasswords) :- setof(Password, isPassword(Password), UniquePasswords), format('found the following unique passwords: ~w.\n', [UniquePasswords]), !.
uniquePasswords([]) :- not(setof(Password, isPassword(_, Password), UniquePasswords)), format('no unique passwords found.\n'), !.

isPassword(Password) :- isPassword(_, Password).
isPassword(Service, Password) :- inCurrentWorld(passwordBeliefs(Service, L)), member((Password, _), L).

passwordFatigue(Service) :- inCurrentWorld(passwordBeliefs(Service, List)), inCurrentWorld(passwordForgetRate(Service, Rate)), applyFatigue(List, Rate, NewList), removeFromWorld(passwordBeliefs(Service, List)), addToWorld(passwordBeliefs(Service, NewList)).
passwordFatigue(Service) :- not(inCurrentWorld(passwordBeliefs(Service, _))), !.

applyFatigue([(P,V)|T], Rate, [(P,NewV)|NewT]) :- V < 0.5, NewV is min(V + Rate, 1), applyFatigue(T, Rate, NewT), !.
applyFatigue([(P,V)|T], Rate, [(P,NewV)|NewT]) :- V > 0.5, NewV is max(V - Rate, 0), applyFatigue(T, Rate, NewT), !.
applyFatigue([(P,V)|T], Rate, [(P,V)|NewT]) :- V = 0.5, applyFatigue(T, Rate, NewT), !.
applyFatigue([], _, []).

%passwordFatigue(Service) :- inCurrentWorld(passwordBeliefs(Service, List)), averagePasswordStrength(List, Average), applyFatigue(List, Average, 0.001, NewList), removeFromWorld(passwordBeliefs(Service, List)), addToWorld(passwordBeliefs(Service, NewList)).

%applyFatigue([(P,V)|T], Average, Rate, [(P, NewV)|NewT]) :- V < Average, NewV is V + Rate, applyFatigue(T, Average, NewT).
%applyFatigue([(P,V)|T], Average, Rate, [(P, NewV)|NewT]) :- V > Average, NewV is V - Rate, applyFatigue(T, Average, NewT).
%applyFatigue([(P,V)|T], Average, Rate, [(P, V)|NewT]) :- V = Average,  applyFatigue(T, Average, NewT).
%applyFatigue([], Average, Rate, []).

averageStrength(List, Average) :- length(List, Length), netStrength(List, NetStrength), Average is NetStrength / Length, !.

netStrength([(P,V)|T], NetStrength) :- netStrength(T, NetStrengthR), NetStrength is NetStrengthR + V.
netStrength([], 0).

printUsernameBeliefs :- inCurrentWorld(services(Services)), foreach(member(Service, Services), printUsernameBeliefs(Service)).

printUsernameBeliefs(Service) :- inCurrentWorld(usernameBeliefs(Service, Beliefs)), ansi_format([fg(magenta)], 'Username beliefs for Service ~w: ~w.\n', [Service, Beliefs]).
printUsernameBeliefs(Service) :- not(inCurrentWorld(usernameBeliefs(Service, _))), ansi_format([fg(magenta)], 'No username beliefs exist for service ~w.\n', [Service]).

printPasswordBeliefs :- inCurrentWorld(services(Services)), foreach(member(Service, Services), printPasswordBeliefs(Service)).

printPasswordBeliefs(Service) :- inCurrentWorld(passwordBeliefs(Service, Beliefs)), ansi_format([fg(magenta)], 'Password beliefs for Service ~w: ~w.\n', [Service, Beliefs]).
printPasswordBeliefs(Service) :- not(inCurrentWorld(passwordBeliefs(Service, _))), ansi_format([fg(magenta)], 'No password beliefs exist for service ~w.\n', [Service]).

printForgetRates :- inCurrentWorld(services(Services)), foreach(member(Service, Services), printForgetRates(Service)).

printForgetRates(Service) :- inCurrentWorld(passwordForgetRate(Service, Rate)), ansi_format([fg(magenta)], 'Password forget rate for Service ~w: ~w.\n', [Service, Rate]).
printForgetRates(Service) :- not(inCurrentWorld(passwordForgetRate(Service, _))), ansi_format([fg(magenta)], 'No password forget rate set for service ~w.\n', [Service]).

%%%%%%%
% fin %
%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% I don't believe we're using the following currently
% but expansion of the model may very well make use of it.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%subGoal(performFirstStep(P)).
%subGoal(decidePerformRest(P)).

%goalRequirements(performFirstStep([Action|Rest]), [Action]). %,decide(performFirstStep(Rest))]).
%  :- format('considering ~w in plan ~w\n',[Action,[Action|Rest]]).

%goalRequirements(decidePerformRest([]), [doNothing]).
%goalRequirements(decidePerformRest([H|R]),[decide(performFirstStep(R)),decidePerformRest(R)]).

%addAuxiliaryFacts([]).
%addAuxiliaryFacts([add(Fact)|R]) :- addToWorld(Fact), format('Added concurrent change ~w\n', [Fact]), addAuxiliaryFacts(R).
%addAuxiliaryFacts([del(Fact)|R]) :- removeFromWorld(Fact), addAuxiliaryFacts(R).

% 'decide(A)' is a built-in goal that performs action A if 'ok(A)' is true.

% If system 1 doesn't make a decision about whether an action is ok,
% use envisionment (projection) to see if we prefer the plan.
% WARNING: CURRENTLY ONLY WORKS WHEN THE ACTION IS THE FIRST STEP IN THE PLAN.
%system2Fact(ok(performFirstStep([Action|Rest]))) :-
%format('\ndeciding whether to ~w\n', [Action]),
%incr(envision), initialWorld(I), preferPlan([Action|Rest],Rest,I).

% We don't currently check which patient meds were delivered to, since
% the scenario only deals with one. Since the utility predicate doesn't
% test this we will need to maintain the current patient on focus as the
% goal tree builds up. We count the number of patients delivered too, so if a
% plan delivers/documents any patient it will get extra utility
%utility(W,U) :- bagof(P,rewarded(W,P),B), length(B,L), !, sumActionCost(W,Cost), U is 100 * L - Cost.
%utility(W,U) :- sumActionCost(W,Cost), U is 0 - Cost.

%sumActionCost([],0).
%sumActionCost([performed(A)|R],S) :- !, cost(A,C), sumActionCost(R,O), S is C + O.
%sumActionCost([H|R],S) :- sumActionCost(R,S).

% For now every action costs 5 units.
%cost(_,5).

% Similarly you must have a trigger to avoid a crash.
%trigger(World, _, [World], 0).  % by default, nothing happens when a world enters a particular state.

% This means the agent chooses between alternate outcomes by which has the higher utility score.
% At the moment there is no alternative.
%decisionTheoretic.

% Copied from mailReader.pl
%incr(Fieldname) :- field(Fieldname,N), New is N + 1, retractall(field(Fieldname,_)), assert(field(Fieldname,New)).

%field(envision, 0).