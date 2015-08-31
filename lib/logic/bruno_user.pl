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

% These are asserted during the initialization stage and hold the lists of all passwords
:-dynamic(strongPassList/1).
:-dynamic(medPassList/1). 
:-dynamic(weakPassList/1). 

% These are counters for number of succecful and unsuccesful logins - important for MCM memory model
:-dynamic(numSuccesLogins/1).
:-dynamic(numFailedLogins/1).

%maxList from agentGeneral
:-consult('agentGeneral').
:-consult('services_util').

% Utility for following predicates:
%  - read_lines/1
%  - choose/1
%  -  
:-consult('bruno_auth_util').

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Parameters - some are fixed and some are ment to be changed
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Mozer et al. 
initialPasswordForgetRate(0.48). 

% When congnitive burden is over 56 bits, we start to form password Groups (Bonneau 12,14)
passwordReuseTreshold(56). 

% When cognitive burden reaches 60 bits (regardless of grouping), users start to write passwords down - guesstimated
passwordWriteTreshold(60). 

%Reads in the lists of passwords into appropriate - called in initializeUserState
initPassLists :- read_lines('bruno_pass_strong.txt', strongPL), assert(strongPassList(strongPL)),
			 	 read_lines('bruno_pass_med.txt', medPL), assert(medPassList(medPL)),
			 	 read_lines('bruno_pass_weak.txt', weakPL), assert(weakPassList(weakPL)),
			 	 read_lines('bruno_dict.txt', bigDict), assert(bigDictionary(bigDict)).

% Initializes counters for logins. Called only once during initializeUserState
initDynamicVariables :- assert(numSuccesLogins(0)), 
						assert(numFailedLogins(0)).

% This is only used to stop simulation. Remove if termination is not neccessary	
passwordForgetRateStoppingCriterion(0.0005).		 

% Need to find a way of resetting cognitiveBurden when passwords are grouped
cognitiveBurden(B) :- cognitiveUsernameBurden(UB), cognitivePasswordBurden(PB), 
					  B is UB + PB, !.

% Username is the burden of all usernames that one can remember, minus ones he/she has written down
cognitiveUsernameBurden(UB) :- recallableUsernames(UU), cognitiveBurden(UU, UB1), 
							findall(S, inCurrentWorld(createdAccount(S)), ServicesC), length(ServicesC, AccountsCreated), 
								findall(S, inCurrentWorld(wroteUsernameOnPostIt(S, _)), ServicesW), length(ServicesW, UsernamesWrittenDown), 
									UB2 is AccountsCreated - UsernamesWrittenDown, 
									UB is UB1 + UB2, !.

% Note that when passwords are grouped, we set the net strenght of every but 0-th instance to 0
% That is why only one iteration should be calculated
cognitivePasswordBurden(PB) :- recallablePasswords(UP), cognitiveBurden(UP, PB1), 
							   findall(S, inCurrentWorld(createdAccount(S)), ServicesC), length(ServicesC, AccountsCreated), 
							   	findall(S, inCurrentWorld(wrotePasswordOnPostIt(S, _)), ServicesW), length(ServicesW, PasswordsWrittenDown), 
							   		PB2 is AccountsCreated - PasswordsWrittenDown, 
							   		PB is PB1 + PB2, !.


%%%%%%%%%%%%%%%%%%%
% Stop
%%%%%%%%%%%%%%%%%%%

testStoppingCriterion :- inCurrentWorld(services(Services)), passwordForgetRateStoppingCriterion(StopRate), 
						 foreach(member(Service, services)), 
						 forgetRateSmallerThan(Service, StopRate), halt(1), !.

forgetRateSmallerThan(Service, StopRate) :- inCurrentWorld(passwordForgetRate(Service, Rate)), Rate < StopRate, !.						


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Iterations - copy pasted from Vijays model
% ...for testing in isolation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% iterations of loop
run :- kIterations(50).
kIterations(K) :- integer(K), K > 1, oneIteration, KMinusOne is K - 1, kIterations(KMinusOne).
kIterations(1) :- oneIteration.

oneIteration :- format('\n\nchoosing action...\n'), system1, do(X), format('chose action ~w\n', X), updateBeliefs(X, 1), system1.


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% High level subgoals, primitive actions and executables
%%% for most of these, there is a section with helper subgoals
%%% and primitive actions for it 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% Placeholder for actions - used for repetetive actions
goal(doWork).
goalWeight(doWork, 1).

% check for the stopping criteria
goalRequirements(doWork, Requirements) :- testStoppingCriterion,  ansi_format([fg(blue)], 'Testing stopping criteria.\n', []), !.
% check if the requirements are set
goalRequirements(doWork, Requirements) :- requirementsSet(Requirements), !.
% Initialize user (if not already)
goalRequirements(doWork, [initializeUser]) :- not(requirementsSet(X)), not(inCurrentWorld(userInitialized)), 
											  ansi_format([fg(blue)], 'Initializing user.\n', []), !.
% ...and set requirements											
goalRequirements(doWork, Requirements) :- not(requirementsSet(X)), chooseService(Service), determineRequirements(Service, Requirements), assert(requirementsSet(Requirements)), ansi_format([fg(blue)], 
										  'New requirements set: ~w\n', [Requirements]), !.


%%% Create a new account
subGoal(createAccount(Service)) :- serviceExists(Service).
goalRequirements(createAccount(Service), [attemptCreateAccount(Service), setupForAccountRetrieval(Service)]).

determineRequirements(Service, [createAccount(Service), resetRequirements]) :- not(inCurrentWorld(createdAccount(Service))), !.
determineRequirements(Service, [Reqs, resetRequirements]) :- R is random(2), nth0(R, [signIn(Service), signOut(Service)], Reqs), !.


%%% Sign in into service
subGoal(signIn(Service)) :- serviceExists(Service).
% If user has account, but not signed in, sign in
goalRequirements(signIn(Service), [attemptSignIn(Service)]) :- format('Expanding goal reqs for sign in - cp1.\n'), 
															   inCurrentWorld(createdAccount(Service)), not(inCurrentWorld(signedIn(Service, _, _))), 
															   format('Expanding goal reqs for sign in - cp2.\n'), !.
goalRequirements(signIn(Service), []) :- inCurrentWorld(createdAccount(Service)), inCurrentWorld(signedIn(Service, _, _)), !.


%%% Sign out of the service
subGoal(signOut(Service)) :- serviceExists(Service).
% If the account exists and if the account is in the world, we are good to sign out
goalRequirements(signOut(Service), [attemptSignOut(Service)]) :- inCurrentWorld(createdAccount(Service)), inCurrentWorld(signedIn(Service, _, _)), 
																 format('Attempting to sign out.\n'), !.
goalRequirements(signOut(Service), []) :- inCurrentWorld(createdAccount(Service)), not(inCurrentWorld(signedIn(Service, _, _))), !.


%%% Reset password 
subGoal(resetPassword(Service)) :- serviceExists(Service).
goalRequirements(resetPassword(Service), [attemptResetPassword(Service), setupForAccountRetrieval(Service)]).


%%% Sign out of the service
subGoal(signOut(Service)) :- serviceExists(Service).
goalRequirements(signOut(Service), [attemptSignOut(Service)]) :- inCurrentWorld(createdAccount(Service)), inCurrentWorld(signedIn(Service, _, _)), !.
goalRequirements(signOut(Service), []) :- inCurrentWorld(createdAccount(Service)), not(inCurrentWorld(signedIn(Service, _, _))), !.


%%% Reset password - also used for creating groups (changing all passwords to one)
subGoal(resetPassword(Service)) :- serviceExists(Service).
goalRequirements(resetPassword(Service), [attemptResetPassword(Service), setupForAccountRetrieval(Service)]).


%%% The primitiveAction initializeUser is the very first action the agent performs.
% -synchronize the hub with the user
% -initialize password lists
% -initialize dynamic variables
% Returns: list of services available to the user

primitiveAction(initializeUser) :- inCurrentWorld(userInitialized).
primitiveAction(initializeUser) :- not(inCurrentWorld(userInitialized)), initializeUserState.

% Wrapper to initialize user
initializeUserState :- FirstNameIndex is random(5), nth0(FirstNameIndex, [joe, bob, sally, carol, alice], FirstName), addToWorld(firstName(FirstName)),
					   initPassLists,
					   initDynamicVariables, 
					   !.
goalRequirements(signIn(Service), []) :- inCurrentWorld(createdAccount(Service)), inCurrentWorld(signedIn(Service, _, _)), !.

% Update beliefs with the new user
updateBeliefsHelper(initializeUser, R) :- ansi_format([fg(red)], 'Update beliefs called with initializeUser. result: ~w\n', [R]), addToWorld(performed(initializeUser)), addToWorld(R), addToWorld(userInitialized), !.



%%% Reset the task user is working on; called as a last thing before doing a task 
executable(resetRequirements).
execute(resetRequirements) :- retractall(requirementsSet(_)), removeFromWorld(setupApproachUsed(_, _)), 
							  format('Executing ~w.\n', resetRequirements).




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% World Logic 
% - this lets us comunicate with the world logic
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% initialize empty world
initialWorld([]).

% Predicate that allows sending the Fact to the world hub
addToWorld(Fact) :- initialWorld(I), member(Fact, I), !.
addToWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), 
					assert(initialWorld([Fact|I])), assert(Fact).

% Predicate that removes Fact from world (once) if it is already part of the world
% still works if fact is not part of the world
removeFromWorld(Fact) :- initialWorld(I), not(member(Fact, I)), !.
removeFromWorld(Fact) :- initialWorld(I), member(Fact, I), 
						 select(Fact, I, J), 
						 	retract(initialWorld(I)), assert(initialWorld(J)), !.

% Predicate that checks if a fact exists in the world
inCurrentWorld(Fact) :- initialWorld(World), member(Fact, World).

% Predicate to check if an action is performed in the world
performed(Action, World) :- member(performed(Action), World).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Utility content
% - helper functions, print and test statements, etc. 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%/

% Check if the service exists
serviceExists(Service):- inCurrentWorld(services(Services)), member(Service, Services).

% Check if the group exists
groupExsists(Group):- member(Group, Groups).

% Choose a service at random
chooseService(Service) :- inCurrentWorld(services(Services)), length(Services, Length), 
						  ServiceIndex is random(Length), nth0(ServiceIndex, Services, Service).

% Print users state and beliefs
printUserState :- cognitiveBurden(B), passwordWriteTreshold(T), 
				  ansi_format([fg(magenta)], 'Cognitive burden: ~w.\nCognitive Treshold: ~w.\n', [B, T]), 
				  printUsernameBeliefs, printPasswordBeliefs, printForgetRates, !.
printUserState :- !.

printDoneStatements :- foreach(done(A, B), ansi_format([fg(yellow)], '~w.\n', [done(A, B)])).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Here we start sending stuff to the World hub
% Every primitive action is picked up by java program and results are returned
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Runtime SG Utility - createAccount
% - utilities for creating account
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% First we try to sign in 
subGoal(attemptCreateAccount(Service)).
primitiveAction(navigateToCreateAccountPage(Service)).

% Then enter desired username
subGoal(enterDesiredUsernameSG(Service)).
goalRequirements(enterDesiredUsernameSG(Service), [chooseUsername(Service), enterDesiredUsername(Service, Username)]).
goalRequirements(enterDesiredPasswordSG(Service), [choosePassword(Service), enterDesiredPassword(Service, Password)]).

primitiveAction(chooseUsername(Service)).
%%% Checks if username already exists
primitiveAction(enterDesiredUsername(Service, Username)) :- inCurrentWorld(desiredUsername(Service, Username)).

% Enter desired password
subGoal(enterDesiredPasswordSG(Service)).
primitiveAction(choosePassword(Service)).
%%% Check if password is available
primitiveAction(enterDesiredPassword(Service, Password)) :- inCurrentWorld(desiredPassword(Service, Password)).
primitiveAction(clickCreateAccountButton(Service, Username, Password)) :- inCurrentWorld(desiredUsername(Service, Username)), inCurrentWorld(desiredPassword(Service, Password)).

% "Claim" the account
subGoal(setupForAccountRetrieval(Service)).
goalRequirements(setupForAccountRetrieval(Service), Approach) :- format('subgoal: setup for account retrieval - cp1.\n'), not(inCurrentWorld(setupApproachUsed(Service, _))), format('subgoal: setup for account retrieval - cp2.\n'), chooseSetupApproach(Service, Approach), format('subgoal: setup for account retrieval - cp3.\n'), addToWorld(setupApproachUsed(Service, Approach)).
goalRequirements(setupForAccountRetrieval(Service), Approach) :- inCurrentWorld(setupApproachUsed(Service, Approach)).

goalRequirements(attemptCreateAccount(Service), [navigateToCreateAccountPage(Service), enterDesiredUsernameSG(Service), enterDesiredPasswordSG(Service), clickCreateAccountButton(Service, Username, Password)]).

%%% Memorize usernames and passwords
primitiveAction(memorizeUsername(Service)).
primitiveAction(memorizePassword(Service)).		
%%% Tralallalalalla
primitiveAction(writeUsernameOnPostIt(Service)).
primitiveAction(writePasswordOnPostIt(Service)).

% if we only need to do setup for password retrieval
chooseSetupApproach(Service, [memorizePassword(Service)]) :- format('chooseSetupApproach - cp1.\n'), not(inCurrentWorld(usernameSetupRequired(Service, _))), inCurrentWorld(passwordSetupRequired(Service, Password)), format('chooseSetupApproach - cp2.\n'), cognitiveUsernameBurden(UB), cognitiveThreshold(T), cognitiveBurdenForPassword(Password, NewPB), format('chooseSetupApproach - cp3.\n'), X is UB + NewPB, X =< T, format('chosen setup approach: memorizing password.\n').
chooseSetupApproach(Service, [writePasswordOnPostIt(Service)]) :- not(inCurrentWorld(usernameSetupRequired(Service, _))), inCurrentWorld(passwordSetupRequired(Service, Password)), cognitiveUsernameBurden(UB), cognitiveThreshold(T), cognitiveBurdenForPassword(Password, NewPB), X is UB + NewPB, X > T, format('chosen setup approach: writing password to post it note.\n').

% if we need to do setup for username and password retrieval
chooseSetupApproach(Service, [memorizeUsername(Service), memorizePassword(Service)]) :- format('chooseSetupApproach - cp1.\n'), inCurrentWorld(usernameSetupRequired(Service, Username)), inCurrentWorld(passwordSetupRequired(Service, Password)), format('chooseSetupApproach - cp2.\n'), cognitiveThreshold(T), cognitiveBurdenForUsername(Username, NewUB), cognitiveBurdenForPassword(Password, NewPB), format('chooseSetupApproach - cp3.\n'), X is NewUB + NewPB, X =< T, format('chosen setup approach: memorizing username and password.\n').
chooseSetupApproach(Service, [memorizeUsername(Service), writePasswordOnPostIt(Service)]) :- format('chooseSetupApproach - cp1.\n'), inCurrentWorld(usernameSetupRequired(Service, Username)), inCurrentWorld(passwordSetupRequired(Service, Password)), format('chooseSetupApproach - cp2.\n'), cognitiveThreshold(T), cognitiveBurdenForUsername(Username, NewUB), cognitivePasswordBurden(PB), cognitiveBurdenForPassword(Password, NewPB), format('chooseSetupApproach - cp3.\n'), X is NewUB + PB, X =< T, Y is NewUB + NewPB, Y > T, format('chosen setup approach: memorizing username and password.\n').
chooseSetupApproach(Service, [writeUsernameOnPostIt(Service), writePasswordOnPostIt(Service)]) :- inCurrentWorld(usernameSetupRequired(Service, Username)), inCurrentWorld(passwordSetupRequired(Service, Password)), cognitiveBurden(B), cognitiveThreshold(T), cognitiveBurdenForUsername(Username, NewUB), cognitivePasswordBurden(PB), X is NewUB + PB, X > T, format('chosen setup approach: writing username and password to post it notes.\n').

repeatable(attemptCreateAccount(Service)) :- not(inCurrentWorld(createdAccount(Service))).
repeatable(enterDesiredUsernameSG(Service)) :- inCurrentWorld(usernameProposalResult(Service, _, error(_))).
repeatable(enterDesiredPasswordSG(Service)) :- inCurrentWorld(passwordProposalResult(Service, _, error(_))).

% if we only need to do setup for password retrieval
chooseSetupApproach(Service, [memorizePassword(Service)]) :- format('chooseSetupApproach - cp1.\n'), not(inCurrentWorld(usernameSetupRequired(Service, _))), inCurrentWorld(passwordSetupRequired(Service, Password)), format('chooseSetupApproach - cp2.\n'), cognitiveUsernameBurden(UB), cognitiveThreshold(T), cognitiveBurdenForPassword(Password, NewPB), format('chooseSetupApproach - cp3.\n'), X is UB + NewPB, X =< T, format('chosen setup approach: memorizing password.\n').
chooseSetupApproach(Service, [writePasswordOnPostIt(Service)]) :- not(inCurrentWorld(usernameSetupRequired(Service, _))), inCurrentWorld(passwordSetupRequired(Service, Password)), cognitiveUsernameBurden(UB), cognitiveThreshold(T), cognitiveBurdenForPassword(Password, NewPB), X is UB + NewPB, X > T, format('chosen setup approach: writing password to post it note.\n').

% if we need to do setup for username and password retrieval
chooseSetupApproach(Service, [memorizeUsername(Service), memorizePassword(Service)]) :- format('chooseSetupApproach - cp1.\n'), inCurrentWorld(usernameSetupRequired(Service, Username)), inCurrentWorld(passwordSetupRequired(Service, Password)), format('chooseSetupApproach - cp2.\n'), cognitiveThreshold(T), cognitiveBurdenForUsername(Username, NewUB), cognitiveBurdenForPassword(Password, NewPB), format('chooseSetupApproach - cp3.\n'), X is NewUB + NewPB, X =< T, format('chosen setup approach: memorizing username and password.\n').
chooseSetupApproach(Service, [memorizeUsername(Service), writePasswordOnPostIt(Service)]) :- format('chooseSetupApproach - cp1.\n'), inCurrentWorld(usernameSetupRequired(Service, Username)), inCurrentWorld(passwordSetupRequired(Service, Password)), format('chooseSetupApproach - cp2.\n'), cognitiveThreshold(T), cognitiveBurdenForUsername(Username, NewUB), cognitivePasswordBurden(PB), cognitiveBurdenForPassword(Password, NewPB), format('chooseSetupApproach - cp3.\n'), X is NewUB + PB, X =< T, Y is NewUB + NewPB, Y > T, format('chosen setup approach: memorizing username and password.\n').
chooseSetupApproach(Service, [writeUsernameOnPostIt(Service), writePasswordOnPostIt(Service)]) :- inCurrentWorld(usernameSetupRequired(Service, Username)), inCurrentWorld(passwordSetupRequired(Service, Password)), cognitiveBurden(B), cognitiveThreshold(T), cognitiveBurdenForUsername(Username, NewUB), cognitivePasswordBurden(PB), X is NewUB + PB, X > T, format('chosen setup approach: writing username and password to post it notes.\n').

repeatable(attemptCreateAccount(Service)) :- not(inCurrentWorld(createdAccount(Service))).

repeatable(enterDesiredUsernameSG(Service)) :- inCurrentWorld(usernameProposalResult(Service, _, error(_))).

repeatable(enterDesiredPasswordSG(Service)) :- inCurrentWorld(passwordProposalResult(Service, _, error(_))).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Runtime SG Utility - signIn
% -utilities for signing in 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% First try to sign in
subGoal(attemptSignIn(Service)).

goalRequirements(attemptSignIn(Service), [retrieveAndEnterAccountInformation(Service), clickSignInButton(Service, Username, Password)]).


% Remember account information
subGoal(retrieveAndEnterAccountInformation(Service)).
primitiveAction(recallAndEnterUsername(Service, Username)) :- recallUsername(Service, Username), !.
primitiveAction(recallAndEnterPassword(Service, Password)) :- recallPassword(Service, Password), !.
primitiveAction(clickSignInButton(Service, Username, Password)) :- inCurrentWorld(retrievedUsername(Service, Username)), inCurrentWorld(retrievedPassword(Service, Password)), !.
%%% If cant remember read and enter from postIt
primitiveAction(readAndEnterUsername(Service, Username)) :- readUsernameOffPostIt(Service, Username), !.
primitiveAction(readAndEnterPassword(Service, Password)) :- readPasswordOffPostIt(Service, Password), !.

goalRequirements(retrieveAndEnterAccountInformation(Service), [resetPassword(Service), retrieveAndEnterAccountInformation(Service)]) :- format('retrieveAndEnterAccountInformation - branch 1 - cp 1.\n'), inCurrentWorld(resettingPassword(Service)), format('retrieveAndEnterAccountInformation - branch 1 - cp 2.\n').
goalRequirements(retrieveAndEnterAccountInformation(Service), [recallAndEnterUsername(Service, Username), recallAndEnterPassword(Service, Password)]) :- format('retrieveAndEnterAccountInformation - branch 2 - cp 1.\n'), not(inCurrentWorld(resettingPassword(Service))), format('retrieveAndEnterAccountInformation - branch 2 - cp 2.\n').
goalRequirements(retrieveAndEnterAccountInformation(Service), [readAndEnterUsername(Service, Username), readAndEnterPassword(Service, Password)]) :- format('retrieveAndEnterAccountInformation - branch 3 - cp 1.\n'), not(inCurrentWorld(resettingPassword(Service))), format('retrieveAndEnterAccountInformation - branch 3 - cp 2.\n').
goalRequirements(retrieveAndEnterAccountInformation(Service), [recallAndEnterUsername(Service, Username), readAndEnterPassword(Service, Password)]) :- format('retrieveAndEnterAccountInformation - branch 4 - cp 1.\n'), not(inCurrentWorld(resettingPassword(Service))), format('retrieveAndEnterAccountInformation - branch 4 - cp 2.\n').
goalRequirements(retrieveAndEnterAccountInformation(Service), [resetPassword(Service), retrieveAndEnterAccountInformation(Service)]) :- format('retrieveAndEnterAccountInformation - branch 5 - cp 1.\n'), not(inCurrentWorld(resettingPassword(Service))), ansi_format([fg(green)], 'retrieveAndEnterAccountInformation(~w) - resetPassword(~w) branch... This is incorrect. Need to change resetPassword so that it does not reset requirements!\n', [Service, Service]), format('retrieveAndEnterAccountInformation - branch 5 - cp 2.\n'), removeFromWorld(retrievedUsername(Service, _)), format('retrieveAndEnterAccountInformation - branch 5 - cp 3.\n'), removeFromWorld(retrievedPassword(Service, _)), format('retrieveAndEnterAccountInformation - branch 5 - cp 4.\n'), retractall(done(retrieveAndEnterAccountInformation(Service), _)), addToWorld(resettingPassword(Service)), format('retrieveAndEnterAccountInformation - branch 5 - cp 5.\n').

recallUsername(Service, Username) :- format('recallUsername - cp 1.\n'), not(inCurrentWorld(retrievedUsername(Service, _))), format('recallUsername - cp 2.\n'), inCurrentWorld(usernameBeliefs(Service, List)), format('recallUsername - cp 3.\n'), maxPairList(List, (Username, Weight)), format('recallUsername - cp 4.\n'), recallThreshold(RT), Weight > RT, format('recallUsername - cp 5.\n'), addToWorld(retrievedUsername(Service, Username)), format('recallUsername(~w, ~w) completed.\n', [Service, Username]), !.
recallPassword(Service, Password) :- format('recallPassword - cp 1.\n'), not(inCurrentWorld(retrievedPassword(Service, _))), format('recallPassword - cp 2.\n'), inCurrentWorld(passwordBeliefs(Service, List)), format('recallPassword - cp 3.\n'), maxPairList(List, (Password, Weight)), format('recallPassword - cp 4.\n'), recallThreshold(RT), Weight > RT, format('recallPassword - cp 5.\n'), addToWorld(retrievedPassword(Service, Password)), format('recallPassword(~w, ~w) completed.\n', [Service, Password]), !.
readUsernameOffPostIt(Service, Username) :- not(inCurrentWorld(retrievedUsername(Service, _))), inCurrentWorld(wroteUsernameOnPostIt(Service, Username)), addToWorld(retrievedUsername(Service, Username)), !.
readPasswordOffPostIt(Service, Password) :- format('readPasswordOffPostIt - cp 1.\n'), not(inCurrentWorld(retrievedPassword(Service, _))), format('readPasswordOffPostIt - cp 2.\n'), inCurrentWorld(wrotePasswordOnPostIt(Service, Password)), format('readPasswordOffPostIt - cp 3.\n'), addToWorld(retrievedPassword(Service, Password)), format('readPasswordOffPostIt(~w, ~w) completed.\n', [Service, Password]), !.

% What happens if sign in succeds or fails
signInSucceeded(Service, Username, Password) :- addToWorld(signedIn(Service, Username, Password)), removeFromWorld(retrievedUsername(Service, _)), removeFromWorld(retrievedPassword(Service, _)).
signInFailed(Service, Username, Password) :- removeFromWorld(retrievedUsername(Service, _)), removeFromWorld(retrievedPassword(Service, _)).

% Update beliefs with what happens after sign in button is clicked
updateBeliefsHelper(clickSignInButton(Service, Username, Password), success) :- signInSucceeded(Service, Username, Password), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [clickSignInButton(Service, Username, Password), success]).
updateBeliefsHelper(clickSignInButton(Service, Username, Password), error(Result)) :- signInFailed(Service, Username, Password), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w... this case still needs to be implemented!\n', [clickSignInButton(Service, Username, Password), error(Result)]).

% If not signed in, repeat it untill it is signed in
repeatable(attemptSignIn(Service)) :- not(inCurrentWorld(signedIn(Service, _, _))), !.



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Runtime SG Utility - signOut
% -utilities for signing out
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% First we try to sign out
subGoal(attemptSignOut(Service)).
primitiveAction(clickSignOutButton(Service, Username)) :- inCurrentWorld(signedIn(Service, Username, _)).

goalRequirements(attemptSignOut(Service), [clickSignOutButton(Service, Username)]).

updateBeliefsHelper(clickSignOutButton(Service, Username), success) :- removeFromWorld(signedIn(Service, Username, _)), ansi_format([fg(red)], 'Update beliefs called with ~w. result: ~w\n', [clickSignOutButton(Service, Username), success]).
updateBeliefsHelper(clickSignOutButton(Service, Username), error(Result)) :- ansi_format([fg(red)], 'Usernamepdate beliefs called with ~w. result: ~w... this case still needs to be implemented!\n', [clickSignOutButton(Service, Username), error(Result)]).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Runtime SG Utility - resetPassword
% -utilities for reseting the password 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

subGoal(attemptResetPassword(Service)).
primitiveAction(navigateToResetPasswordPage(Service)).
goalRequirements(attemptResetPassword(Service), [navigateToResetPasswordPage(Service), retrieveAndEnterUsername(Service), chooseNewPassword(Service), clickResetPasswordButton(Service, Username, Password)]).

subGoal(retrieveAndEnterUsername(Service)).

goalRequirements(retrieveAndEnterUsername(Service), [recallAndEnterUsername(Service, Username)]).
goalRequirements(retrieveAndEnterUsername(Service), [readAndEnterUsername(Service, Username)]).
goalRequirements(retrieveAndEnterUsername(Service), []) :- ansi_format([fg(green)], 'retrieveAndEnterUsername(Service) - nil branch... This should not happen!\n', []), removeFromWorld(retrievedUsername(Service, _)).

subGoal(setupForNewPasswordRetrieval(Service)).
primitiveAction(chooseNewPassword(Service)).
primitiveAction(clickResetPasswordButton(Service, Username, Password)) :- format('clickResetPasswordButton - cp 1.\n'), inCurrentWorld(desiredPassword(Service, Password)), format('clickResetPasswordButton - cp 2.\n'), inCurrentWorld(retrievedUsername(Service, Username)), format('clickResetPasswordButton - cp 3.\n'), !.
subGoal(attemptResetPassword(Service, Password)).


updateBeliefsHelper(navigateToResetPasswordPage(Service), success(passwordRequirements(PR))) :- not(inCurrentWorld(passwordRequirements(Service, _))), addToWorld(passwordRequirements(Service, PR)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [navigateToResetPasswordPage(Service), success(passwordRequirements(PR))]), !.
updateBeliefsHelper(navigateToResetPasswordPage(Service), success(passwordRequirements(PR))) :- inCurrentWorld(passwordRequirements(Service, _)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [navigateToResetPasswordPage(Service), success(passwordRequirements(PR))]), !.
updateBeliefsHelper(navigateToResetPasswordPage(Service), Result) :- ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w/. Should not be here!\n', [navigateToResetPasswordPage(Service), Result]), !.

updateBeliefsHelper(clickResetPasswordButton(Service, Username, Password), success) :- removeFromWorld(desiredPassword(Service, _)), removeFromWorld(passwordRequirements(Service, _)), removeFromWorld(passwordProposalResult(Service, _, _)), removeFromWorld(passwordChosenButNotEntered(Service)), removeFromWorld(retrievedUsername(Service, _)), addToWorld(passwordSetupRequired(Service, Password)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [clickResetPasswordButton(Service, Username, Password), success]).
updateBeliefsHelper(clickResetPasswordButton(Service, Username, Password), Result) :- Result = error(Reason), Reason \= noService, Reason \= noUsername, removeFromWorld(passwordProposalResult(Service, _, _)), removeFromWorld(passwordChosenButNotEntered(Service)), removeFromWorld(retrievedUsername(Service, _)), addToWorld(passwordProposalResult(Service, Password, Result)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [clickResetPasswordButton(Service, Username, Password), Result]).

updateBeliefsHelper(chooseNewPassword(Service), R) :- format('choose new password - pred 1 - cp1.\n'), not(inCurrentWorld(passwordChosenButNotEntered(Service))), format('choose new password - pred 1 - cp2.\n'), not(inCurrentWorld(desiredPassword(Service, _))), format('choose new password - pred 1 - cp3.\n'), not(inCurrentWorld(passwordProposalResult(Service, _, _))), format('choose new password - pred 1 - cp4.\n'), inCurrentWorld(passwordRequirements(Service, Requirements)), choosePasswordHelper(Service, Requirements, '', Password), addToWorld(desiredPassword(Service, Password)), addToWorld(passwordChosenButNotEntered(Service)), format('choose new password - branch 1 complete!\n', []), !.
updateBeliefsHelper(chooseNewPassword(Service), R) :- format('choose new password - pred 2 - cp1.\n'), not(inCurrentWorld(passwordChosenButNotEntered(Service))), format('choose new password - pred 2 - cp2.\n'), inCurrentWorld(desiredPassword(Service, PreviousPassword)), format('choose new password - pred 2 - cp3.\n'), inCurrentWorld(passwordProposalResult(Service, _, error(FailedPasswordRequirements))), inCurrentWorld(passwordRequirements(Service, InitialRequirements)), mergeLists(InitialRequirements, FailedPasswordRequirements, Requirements), removeFromWorld(passwordRequirements(Service, InitialRequirements)), addToWorld(passwordRequirements(Service, Requirements)), choosePasswordHelper(Service, Requirements, PreviousPassword, Password), removeFromWorld(desiredPassword(Service, _)), addToWorld(desiredPassword(Service, Password)), addToWorld(passwordChosenButNotEntered(Service)), format('choose new password - branch 2 complete!\n', []), !.
updateBeliefsHelper(chooseNewPassword(Service), R) :- format('catch-all choose new password exec!\n', []), !.

repeatable(attemptResetPassword(Service)) :- inCurrentWorld(passwordProposalResult(Service, _, error(_))).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Update Beliefs Helpers
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%Check if password is recallable
recallablePasswords(UniquePasswords) :- setof(Password, isRecallablePassword(Password), RecallablePasswords), format('Found the following recallable passwords: ~w.\n', [RecallablePasswords]), !.
recallablePasswords([]) :- not(setof(Password, isRecallablePassword(_, Password), _)), format('no recallable passwords found.\n'), !.
isRecallablePassword(Password) :- isRecallablePassword(_, Password).
isRecallablePassword(Service, Password) :- inCurrentWorld(passwordBeliefs(Service, L)), member((Password, Strength), L), recallThreshold(RT), Strength > RT.

% Check if password is reusable
isReusable(Password, U, Requirements) :- member(Password, U), satisfiesRequirements(Password, Requirements).

% Adding the fact taht usernames are memorized to the world
% Still a very crude model where whenever username is used correctly for loging on, 
% it sets it to one, and removes all else (effectivly setting them to 0) from username beliefs
updateBeliefsHelper(memorizeUsername(Service), Result) :- inCurrentWorld(usernameSetupRequired(Service, Username)), removeFromWorld(usernameSetupRequired(Service, Username)), addToWorld(usernameBeliefs(Service, [(Username, 1)])), format('memorized username ~w.\n', [Username]).
updateBeliefsHelper(memorizeUsername(Service), Result) :- not(inCurrentWorld(usernameSetupRequired(Service, _))).

% Adding the fact that passwords are recallable in some way to the world
updateBeliefsHelper(memorizePassword(Service), Result) :- inCurrentWorld(passwordSetupRequired(Service, Password)), not(inCurrentWorld(passwordBeliefs(Service, _))), addToWorld(passwordBeliefs(Service, [(Password, 1)])), initialPasswordForgetRate(Rate), addToWorld(passwordForgetRate(Service, Rate)), removeFromWorld(passwordSetupRequired(Service, Password)), removeFromWorld(resettingPassword(Service)), format('memorized password ~w.\n', [Password]).
updateBeliefsHelper(memorizePassword(Service), Result) :- inCurrentWorld(passwordSetupRequired(Service, Password)), inCurrentWorld(passwordBeliefs(Service, _)), removeFromWorld(passwordBeliefs(Service, _)), addToWorld(passwordBeliefs(Service, [(Password, 1)])), initialPasswordForgetRate(Rate), removeFromWorld(passwordForgetRate(Service, _)), addToWorld(passwordForgetRate(Service, Rate)), removeFromWorld(passwordSetupRequired(Service, Password)), removeFromWorld(resettingPassword(Service)), format('executing ~w.\n', [memorizePassword(Service)]).
updateBeliefsHelper(memorizePassword(Service), Result) :- not(inCurrentWorld(passwordSetupRequired(Service, _))).

% Adding the fact that usernames are written down 
updateBeliefsHelper(writeUsernameOnPostIt(Service), Result) :- inCurrentWorld(usernameSetupRequired(Service, Username)), removeFromWorld(usernameSetupRequired(Service, Username)), addToWorld(usernameBeliefs(Service, [(Username, 0.5)])), addToWorld(wroteUsernameOnPostIt(Service, Username)), format('executing ~w.\n', [writeUsernameOnPostIt(Service)]).
updateBeliefsHelper(writeUsernameOnPostIt(Service), Result) :- not(inCurrentWorld(usernameSetupRequired(Service, _))).

% Adding the fact that passwords are writen down
updateBeliefsHelper(writePasswordOnPostIt(Service), Result) :- inCurrentWorld(passwordSetupRequired(Service, Password)), not(inCurrentWorld(passwordBeliefs(Service, _))), addToWorld(passwordBeliefs(Service, [(Password, 0.5)])), addToWorld(wrotePasswordOnPostIt(Service, Password)), initialPasswordForgetRate(Rate), addToWorld(passwordForgetRate(Service, Rate)), removeFromWorld(passwordSetupRequired(Service, Password)), removeFromWorld(resettingPassword(Service)), format('wrote down password ~w. \n', [writePasswordOnPostIt(Service)]).
updateBeliefsHelper(writePasswordOnPostIt(Service), Result) :- inCurrentWorld(passwordSetupRequired(Service, Password)), inCurrentWorld(passwordBeliefs(Service, _)), removeFromWorld(passwordBeliefs(Service, _)), addToWorld(passwordBeliefs(Service, [(Password, 0.5)])), addToWorld(wrotePasswordOnPostIt(Service, Password)), initialPasswordForgetRate(Rate), removeFromWorld(passwordForgetRate(Service, _)), addToWorld(passwordForgetRate(Service, Rate)), removeFromWorld(passwordSetupRequired(Service, Password)), removeFromWorld(resettingPassword(Service)), format('wrote down password ~w. Setting NEW Password\n', [writePasswordOnPostIt(Service)]).
updateBeliefsHelper(writePasswordOnPostIt(Service), Result) :- not(inCurrentWorld(passwordSetupRequired(Service, _))).

% Choosing passwords 
updateBeliefsHelper(choosePassword(Service), R) :- not(inCurrentWorld(passwordChosenButNotEntered(Service))), not(inCurrentWorld(desiredPassword(Service, _))), not(inCurrentWorld(passwordProposalResult(Service, _, _))), inCurrentWorld(passwordRequirements(Service, Requirements)), choosePasswordHelper(Service, Requirements, '', Password), addToWorld(desiredPassword(Service, Password)), addToWorld(passwordChosenButNotEntered(Service)), format('exec password - branch 1!\n', []), !.
updateBeliefsHelper(choosePassword(Service), R) :- not(inCurrentWorld(passwordChosenButNotEntered(Service))), inCurrentWorld(desiredPassword(Service, PreviousPassword)), inCurrentWorld(passwordProposalResult(Service, _, error(FailedPasswordRequirements))), inCurrentWorld(passwordRequirements(Service, InitialRequirements)), mergeLists(InitialRequirements, FailedPasswordRequirements, Requirements), removeFromWorld(passwordRequirements(Service, InitialRequirements)), addToWorld(passwordRequirements(Service, Requirements)), choosePasswordHelper(Service, Requirements, PreviousPassword, Password), removeFromWorld(desiredPassword(Service, _)), addToWorld(desiredPassword(Service, Password)), addToWorld(passwordChosenButNotEntered(Service)), format('exec password - branch 2!\n', []), !.


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Utilities and helpers 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Check if the cognitive burden is ok when choosing passwords
choosePasswordHelper(Service, Requirements, _, Password):- cognitiveThreshold(T), cognitiveBurden(B), passwordReuseTreshold(R), B>R, uniquePasswords(U) \= [], stringsSortedByLength(U, Priority, SortedU), findall(Password, isReusable(Password, U, Requirements), L), head(L, Password), !.

% First, choose one of the easiest passwords one can find. 
choosePasswordHelper(Service, Requirements, _, Password):- weakPassList(WP), choose(WP, Pass), Password is Pass, not(isRecallable(Password)), satisfiesRequirements(Password, Requirements).

% Then, if no weak passwords satisfy requirement
choosePasswordHelper(Service, Requirements, _, Password):- medPassList(MP), choose(MP, Pass), Password is Pass, not(isRecallable(Password)), satisfyRequirements(Password, Requirements). 

% Furthermore, if no medium passwords satisfy requirement, use one from the strong password list. 
choosePasswordHelper(Service, Requirements, _, Password):- strongPassList(SP), choose(SP, Pass), Password is Pass, not(isRecallable(Password)), satisfyRequirements(Password, Requirements). 

% Else reuse one of the existing ones (not a deliberate chocice)
	choosePasswordHelper(Service, Requirements, _, Password):- medPassList(MP), choose(MP, Pass), Password is Pass, satisfyRequirements(Password, Requirements); 
															   weakPassList(WP), choose(WP, Pass), Password is Pass, satisfyRequirements(Password, Requirements);
															   strongPassList(SP), choose(SP, Pass), Password is Pass, satisfyRequirements(Password, Requirements).

% Add password to the reusable list
isReusable(Password, U, Requirements) :- member(Password, U), satisfiesRequirements(Password, Requirements).

% Utility to check if password is unique
addUniquePasswords(Service, [Password|Rest]) :- isPassword(Service, Password), addUniquePasswords(Service, Rest), !.
addUniquePasswords(Service, [Password|Rest]) :- not(isPassword(Service, Password)), inCurrentWorld(passwordBeliefs(Service, List)), append([(Password, 0)], List, NewList), removeFromWorld(passwordBeliefs(Service, __)), addToWorld(passwordBeliefs(Service, NewList)), addUniquePasswords(Service, Rest), !.
addUniquePasswords(Service, [Password|Rest]) :- not(isPassword(Service, Password)), not(inCurrentWorld(passwordBeliefs(Service, _))), !.
addUniquePasswords(Service, []) :- !.

% Are the usernames recallable
recallableUsernames(RecallableUsernames) :- setof(Username, isRecallableUsername(Username), RecallableUsernames), format('found the following recallable usernames: ~w.\n', [RecallableUsernames]), !.
recallableUsernames([]) :- not(setof(Username, isRecallableUsername(_, Username), _)), format('no recallable usernames found.\n'), !.
% and the helper for it


passwordFatigue(Service) :- inCurrentWorld(passwordBeliefs(Service, List)), inCurrentWorld(passwordForgetRate(Service, Rate)), 
							applyFatigue(List, Rate, NewList), removeFromWorld(passwordBeliefs(Service, List)), 
							addToWorld(passwordBeliefs(Service, NewList)).
passwordFatigue(Service) :- not(inCurrentWorld(passwordBeliefs(Service, _))), !.

% Application of fatigue is the same as in the initial model, however, calculation of the forgetting rate is calculated
% according to Mozer et al. Appropriately, these results show the same as Florencio discovered empirically. 
applyFatigue([(P,V)|T], Rate, [(P,NewV)|NewT]) :- numFailedLogins(X), Nsl is max(1, X), %check for 0 division 
												  pow(V, 1/Rate, TempV), % calculate the new value 
												  NewV is max(TempV, 0), % check that it is zero
												  applyFatigue(T, Rate, NewT), !. %recurse
applyFatigue([], _, []).


strengthenPassword(Service, Password) :- inCurrentWorld(passwordBeliefs(Service, PasswordBeliefs)), inCurrentWorld(passwordForgetRate(Service, Rate)), 
										 member((Password, Strength), PasswordBeliefs), 
										 removeFromWorld(passwordBeliefs(Service, _)), 
										 delete(PasswordBeliefs, (Password, _), PasswordBeliefsModified),
										 numSuccesLogins(Nsl), 
										 StrengthenRate = max(log(Nsl/3), Rate + 0,2), 
										 NewStrength is min(StrengthenRate, 1), NewPasswordBeliefs = [(Password, NewStrength)|PasswordBeliefsModified], 
										 addToWorld(passwordBeliefs(Service, NewPasswordBeliefs)), 
										 assert(numSuccesLogins(Nsl+1)), assert(numFailedLogins(0)), !.
strengthenPassword(Service, Password) :- not(inCurrentWorld(passwordrdBeliefs(Service, _))), !.


% Placeholders for asserting the lists and variables
strongPassList([]).
medPassList([]).
weakPassList([]).
numFailedLogins(0).
numSuccesLogins(0).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Default Update Beliefs 
% - has to be placed after all updateBeliefsHelper
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Default update beliefs
updateBeliefs(Action, Result) :- ansi_format([fg(red)], 'update beliefs called with ~w. BEGIN.\n', [Action]), updateUsernameBeliefs(Action, Result), updatePasswordBeliefs(Action, Result), updateBeliefsHelper(Action, Result), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w. END.\n', [Action, Result]), updateUsernameBeliefs(Action, Result), !.
updateBeliefs(Action, Result) :- not(updateBeliefsHelper(Action, Result)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w (default call)\n', [Action, Result]), !.

updateUsernameBeliefs(_, _) :- !.

updatePasswordBeliefs(clickSignInButton(Service, Username, Password), success) :- inCurrentWorld(services(Services)), inCurrentWorld(passwordBeliefs(Service, PasswordBeliefs)), removeFromWorld(passwordBeliefs(Service, _)), addToWorld(passwordBeliefs(Service, [(Password, 1)])), removeFromWorld(passwordForgetRate(Service, R)), NewR is R / 2, addToWorld(passwordForgetRate(Service, NewR)), uniquePasswords(UniquePasswords), foreach(member(MemberService, Services), addUniquePasswords(MemberService, UniquePasswords)), delete(Services, Service, ServicesDifferentThanMe), foreach(member(MemberService, ServicesDifferentThanMe), strengthenPassword(MemberService, Password)), foreach(member(MemberService, Services), passwordFatigue(MemberService)), !.
updatePasswordBeliefs(clickSignInButton(Service, Username, Password), error(passwordIncorrect)) :- inCurrentWorld(services(Services)), inCurrentWorld(passwordBeliefs(Service, PasswordBeliefs)), removeFromWorld(passwordBeliefs(Service, _)), delete(PasswordBeliefs, [Password, _], NewPasswordBeliefs), addToWorld(passwordBeliefs(Service, NewPasswordBeliefs)), removeFromWorld(passwordForgetRate(Service, R)), NewR is R * 2, addToWorld(passwordForgetRate(Service, NewR)), uniquePasswords(UniquePasswords), foreach(member(MemberService, Services), addUniquePasswords(MemberService, UniquePasswords)), foreach(member(MemberService, Services), passwordFatigue(MemberService)), !.

updatePasswordBeliefs(Action, Result) :- Action = clickSignInButton(_, _, _), Result \= error(passwordIncorrect), Result \= success, inCurrentWorld(services(Services)), uniquePasswords(UniquePasswords), foreach(member(Service, Services), addUniquePasswords(Service, UniquePasswords)), foreach(member(Service, Services), passwordFatigue(Service)), !.
updatePasswordBeliefs(Action, Result) :- Action \= clickSignInButton(_, _, _), inCurrentWorld(services(Services)), uniquePasswords(UniquePasswords), foreach(member(Service, Services), addUniquePasswords(Service, UniquePasswords)), foreach(member(Service, Services), passwordFatigue(Service)), !.
updatePasswordBeliefs(Action, Result) :- not(inCurrentWorld(services(Services))), !.



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Various Print statements
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

printUsernameBeliefs :- inCurrentWorld(services(Services)), foreach(member(Service, Services), printUsernameBeliefs(Service)).

printUsernameBeliefs(Service) :- inCurrentWorld(usernameBeliefs(Service, Beliefs)), ansi_format([fg(magenta)], 'Username beliefs for Service ~w: ~w.\n', [Service, Beliefs]).
printUsernameBeliefs(Service) :- not(inCurrentWorld(usernameBeliefs(Service, _))), ansi_format([fg(magenta)], 'No username beliefs exist for service ~w.\n', [Service]).

printPasswordBeliefs :- inCurrentWorld(services(Services)), foreach(member(Service, Services), printPasswordBeliefs(Service)).

printPasswordBeliefs(Service) :- inCurrentWorld(passwordBeliefs(Service, Beliefs)), ansi_format([fg(magenta)], 'Password beliefs for Service ~w: ~w.\n', [Service, Beliefs]).
printPasswordBeliefs(Service) :- not(inCurrentWorld(passwordBeliefs(Service, _))), ansi_format([fg(magenta)], 'No password beliefs exist for service ~w.\n', [Service]).

printForgetRates :- inCurrentWorld(services(Services)), foreach(member(Service, Services), printForgetRates(Service)).

printForgetRates(Service) :- inCurrentWorld(passwordForgetRate(Service, Rate)), ansi_format([fg(magenta)], 'Password forget rate for Service ~w: ~w.\n', [Service, Rate]).
printForgetRates(Service) :- not(inCurrentWorld(passwordForgetRate(Service, _))), ansi_format([fg(magenta)], 'No password forget rate set for service ~w.\n', [Service]).

