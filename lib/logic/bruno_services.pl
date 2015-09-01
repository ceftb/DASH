:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(accountExists/4).
:- dynamic(determineResult/3).
:- dynamic(signedIn/3).
:- dynamic(printWorldState/0).
:- dynamic(numAccountsCreated/2).
:- dynamic(numUsernamesMemorized/2).
:- dynamic(numUsernamesWritten/2).
:- dynamic(numPasswordsMemorized/2).
:- dynamic(numPasswordsWritten/2).
:- dynamic(numPasswordsReset/2).

:- dynamic(servicesCreated/0).
:- dynamic(services/1).
:- dynamic(passwordRequirements/2).
:- dynamic(testServiceStrength/1).

:- dynamic(passwordResetPerformed/2).
:- dynamic(passwordWrittenDown/2).

:- consult('services_util').


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Parameters
% - number of available services
% - probabilities of different exposures
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% First account to be created, and does not specifically count in the account number
% Options: weak, average, good, strong
targetServicePasswordCompositionStrength(weak). 

% Whichever is the target is less then the rest. 
numWeakServices(5).
numAverageServices(6).
numGoodServices(6).
numStrongServices(6).

% Final tally of the services
numServices(N) :- numWeakServices(NW), numAverageServices(NA), numGoodServices(NG), numStrongServices(NS), N is NW + NA + NG + NS + 1, !.

% Probability that atacker will reuse passoword accross services
% Florencio (2014) says that 43-51% (depends on a study) users reuse their passwords. 
% One can then make an educated guess that at least 40% of attackers will try that
reuseAttackRisk(0.40).

% Probability that atacker will use passwords written on postit. 
% Still waiting for Sergey to get some numbers, for now it will be 25%
stealAttackRisk(0.25).

% Scalar for determining probability that a password is vulnerable to an attack
% It scales a function of ingerent service weakness and raw password strenght (in this case, based on bit Strength)
inherentRisk(0.2). 


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Assesing the security measure
% - multiple authors propose different number for probabilities
% - used simple measure of password strenght
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Raw Password Strength is scaled version of passwordStrength used for assesing the "security measure of an attack"
% Reused from Vijays model, since it was not of great importance to me 
rawPasswordStrength(Service, User, 0.1) :- accountExists(Service, _, Password, User), 
										   passwordScore(Service, Password, Score), Score =< 6.
rawPasswordStrength(Service, User, 0.2) :- accountExists(Service, _, Password, User), 
										   passwordScore(Service, Password, Score), Score > 6, Score =< 13.
rawPasswordStrength(Service, User, 0.3) :- accountExists(Service, _, Password, User), 
										   passwordScore(Service, Password, Score), Score > 13, Score =< 19.
rawPasswordStrength(Service, User, 0.4) :- accountExists(Service, _, Password, User), 
										   passwordScore(Service, Password, Score), Score > 19, Score =< 23.
rawPasswordStrength(Service, User, 0.5) :- accountExists(Service, _, Password, User), 
										   passwordScore(Service, Password, Score), Score > 23.
rawPasswordStrength(Service, User, 1) :- not(accountExists(Service, _, _, User)).

%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Direct attacks
%%%%%%%%%%%%%%%%%%%%%%%%

% Core Vulnerability of the service, function of inherent weakness and password Strength in bits
serviceVulnerabilityRisk(Service, User, Risk) :- rawPasswordStrength(Service, User, Strength), 
												 inherentRisk(SVRisk), 
												 Risk is (1 - Strength) * SVRisk.

% Probability that the attacker will read the postit if it exists
stolenPasswordAttackRisk(Service, User, SPRisk) :- accountExists(Service, _, _, User), 
												   stealAttackRisk(SPRisk), 
												   passwordWrittenDown(Service, User).
stolenPasswordAttackRisk(Service, User, 0) :- ( accountExists(Service, _, _, User), not(passwordWrittenDown(Service, User)) ); 
											  not(accountExists(Service, _, _, User)).

% Probability that the password is safe from the direct attack vector
probabilitySafeFromDirectAttack(Service, User, P) :- accountExists(Service, _, _, User), 
													 serviceVulnerabilityRisk(Service, User, SVR), 
													 stolenPasswordAttackRisk(Service, User, SPAR), 
													 P is (1 - SVR) * (1 - SPAR), !.
probabilitySafeFromDirectAttack(Service, User, 1) :- not(accountExists(Service, _, _, User)), !.

%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Indirect Attacks
%%%%%%%%%%%%%%%%%%%%%%%%

% General template/placeholder
probabilitySafeFromAllIndirectAttacks(Service, User, P) :- services(L), 
														   probabilitySafeFromAllIndirectAttacksHelper(Service, L, User, P), !.

% Applied probability that attacker will try to reuse the username/password combo accros attacked services 
probabilitySafeFromAllIndirectAttacksHelper(IndirectlyAttackedService, [DirectlyAttackedService | Rest], User, P) :- probabilitySafeFromIndirectAttack(IndirectlyAttackedService, DirectlyAttackedService, User, PThis), 
																													 probabilitySafeFromAllIndirectAttacksHelper(IndirectlyAttackedService, Rest, User, PRecurse), 
																													 P is PThis * PRecurse, !.
probabilitySafeFromAllIndirectAttacksHelper(_, [], User, 1) :- !.
% General case
probabilitySafeFromIndirectAttack(IndirectlyAttackedService, DirectlyAttackedService, User, P) :- IndirectlyAttackedService \= DirectlyAttackedService, 
																								  accountExists(IndirectlyAttackedService, Username, Password, User), 
																								  accountExists(DirectlyAttackedService, Username, Password, User), 
																								  probabilitySafeFromDirectAttack(DirectlyAttackedService, User, PSafeFromDirectAttack), 
																								  reuseAttackRisk(RARisk), P is 1 - (1 - PSafeFromDirectAttack) * RARisk, !.

% Different usernames or different passwords on attacked services
probabilitySafeFromIndirectAttack(IndirectlyAttackedService, DirectlyAttackedService, User, 1) :- IndirectlyAttackedService \= DirectlyAttackedService, 
																								  accountExists(IndirectlyAttackedService, Username1, Password1, User), 
																								  accountExists(DirectlyAttackedService, Username2, Password2, User), 
																								  ( Username1 \= Username2; Password1 \= Password2 ), !.
% If agent does not have an account on either of attacked services 
probabilitySafeFromIndirectAttack(IndirectlyAttackedService, DirectlyAttackedService, User, 1) :- IndirectlyAttackedService \= DirectlyAttackedService, 
																								  not(accountExists(IndirectlyAttackedService, _, _, User)), !.
probabilitySafeFromIndirectAttack(IndirectlyAttackedService, DirectlyAttackedService, User, 1) :- IndirectlyAttackedService \= DirectlyAttackedService, 
																								  not(accountExists(DirectlyAttackedService, _, _, User)), !.
% If they are the same
probabilitySafeFromIndirectAttack(IndirectlyAttackedService, DirectlyAttackedService, User, 1) :- IndirectlyAttackedService = DirectlyAttackedService, !.

probabilitySafe(Service, User, P) :- probabilitySafeFromDirectAttack(Service, User, PDirect), probabilitySafeFromAllIndirectAttacks(Service, User, PIndirect), P is PDirect * PIndirect, !.



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Statistics - printing the values we are interested in
% - blue or default: general messages
% - green: value messages
% - cyan: debugging
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%% Print Statements
%%%%%%%%%%%%%%%%%%%%%%%%%

printWorldState :- ansi_format([fg(blue)], 'Printing world state...\n', []), 
				   foreach(id(User), printUserSecurityStatistics(User)), 
				   printExposureForService1, !.

% Print the statistics at the end
printUserSecurityStatistics(User) :- services(Services), 
									 computeNetExposureForUser(User, Services, NetExposure), 
									 numServices(NumServices), 
									 AverageExposure is NetExposure / NumServices, 
									 numAccountsCreated(User, AC), numPasswordsMemorized(User, PM), numPasswordsWritten(User, PW), numPasswordsReset(User, PR), 
									 ansi_format([fg(green)], 'User ~w: Accounts Created: ~w, Avg PW Security: ~w, PW Memorization Attempts: ~w, PWs Written Down: ~w,PW Resets: ~w.\n', [User, AC, AverageExposure, PM, PW, PR]), !.

printExposureForService1 :- foreach(id(User), 
							printExposureForService1(User)).

printExposureForService1(User) :- printIfPasswordWrittenDownForService1(User), 
								  printIfPasswordResetPerformedForService1(User), 
								  probabilitySafe(service1, User, P), 
								  ansi_format([fg(green)], 'Password security measure for user ~w at target service ~w: ~w.\n', [User, service1, P]), !.

printAverageExposure :- foreach(id(User), printAverageExposureForUser(User)).

printAverageExposureForUser(User) :- services(Services), 
									 computeNetExposureForUser(User, Services, NetExposure), 
									 numServices(NumServices), 
									 AverageExposure is NetExposure / NumServices, 
									 ansi_format([fg(green)], 'Average password security measure for user ~w is ~w.\n', [User, AverageExposure]), !.


printIfPasswordWrittenDownForService1(User) :- passwordWrittenDown(service1, User), 
											   ansi_format([fg(blue)], 'User ~w wrote down password for service1.\n', [User]), !.
printIfPasswordWrittenDownForService1(User) :- not(passwordWrittenDown(service1, User)), 
											   ansi_format([fg(blue)], 'User ~w did NOT write down password for service1.\n', [User]), !.

printIfPasswordResetPerformedForService1(User) :- passwordResetPerformed(service1, User), 
												  ansi_format([fg(blue)], 'User ~w did reset password for service1.\n', [User]), !.
printIfPasswordResetPerformedForService1(User) :- not(passwordResetPerformed(service1, User)), 
												  ansi_format([fg(blue)], 'User ~w did NOT reset password for service1.\n', [User]), !.



%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%% Utility
%%%%%%%%%%%%%%%%%%%%%%%%

computeNetExposureForUser(User, [H | T], NetExposure) :- probabilitySafe(H, User, P), 
														 computeNetExposureForUser(User, T, NetExposureRecurse), 
														 NetExposure is P + NetExposureRecurse, !.

computeNetExposureForUser(User, [], 0) :- !.


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Services Logic
% - handling services datastructures 
% - various info about services
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

services(S) :- not(servicesCreated), format('creating services...\n', []), 
									 format('services - cp1.\n', []), 
									 numServices(NumServices), 
									 format('services - cp2.\n', []), 
									 createServices(NumServices, S), 
									 format('services - cp3.\n', []), 
									 assert(services(S)), 
									 format('services - cp4.\n', []), 
									 asserta(servicesCreated), 
									 format('bruno je idit\n', []), 
									 format('Created following services: ~w.\n', [S]), !.




% Helper that creates N services and name them accordingly as "service[1-n]"
createServices(N, [Service|Rest]) :- format('createServices: N = ~w.\n', [N]), N > 1, atom_number(AtomN, N), atom_concat(service, AtomN, Service), NMinus1 is N - 1, setPasswordRequirements(N), createServices(NMinus1, Rest), !.

createServices(1, [service1]) :- setPasswordRequirements(1).

% True if service exists in the world
serviceExists(Service) :- services(Services),
						  member(Service, Services).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Requirements 
% - requirements for creating passwords
% - requirements for usernames 						  
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Initial requirements for setting up account. Choosen randomly
usernameInitRequirements(Service, [minLength(4)]).
passwordInitRequirements(Service, [minLength(4)]).

% Arbitrary username requirements, potentially used for further expantion
usernameRequirements(Service, [minLength(4), minLower(1)]).

%%% Password Requirements
% - format for the service-requirements pair is: 
% 		Service, [minLength, minLower, minUpper, minDigit, minSpecial, minLength] 
setPasswordRequirements(Service, weak) :- format('Setting weak password requirements for ~w.\n', [Service]), 
										   MinLength is 1 + random(4), 
										   MinLower is random(0), 
										   assert(passwordRequirements(Service, [minLength(MinLength), minLower(MinLower), minUpper(0), minDigit(0), minSpecial(0), maxLength(64)])).
setPasswordRequirements(Service, average) :- format('Setting average password requirements for ~w.\n', [Service]), 
											  MinLength is 4 + random(5), 
											  MinLower is 1 + random(2), 
											  MinUpper is 1 + random(2), 
											  MinDigit is random(2), 
											  assert(passwordRequirements(Service, [minLength(MinLength), minLower(MinLower), minUpper(MinUpper), minDigit(MinDigit), minSpecial(0), maxLength(64)])).
setPasswordRequirements(Service, good) :- format('Setting good password requirements for ~w.\n', [Service]), 
										  MinLength is 8 + random(5), 
										  MinLower is 1 + random(3), 
										  MinUpper is 1 + random(3), 
										  MinDigit is 1 + random(2), 
										  MinSpecial is random(2), 
										  assert(passwordRequirements(Service, [minLength(MinLength), minLower(MinLower), minUpper(MinUpper), minDigit(MinDigit), minSpecial(MinSpecial), maxLength(64)])).
setPasswordRequirements(Service, strong) :- format('Setting strong password requirements for ~w.\n', [Service]), 
											MinLength is 12 + random(5), 
											MinLower is 2 + random(3), 
											MinUpper is 2 + random(3), 
											MinDigit is 2 + random(3), 
											MinSpecial is 1 + random(2), 
											assert(passwordRequirements(Service, [minLength(MinLength), minLower(MinLower), minUpper(MinUpper), minDigit(MinDigit), minSpecial(MinSpecial), maxLength(64)])).

% Picking which service is classified where 
setPasswordRequirements(K) :- atom_number(AtomK, K), 
							  atom_concat(service, AtomK, ServiceK), 
							  numWeakServices(NW), 
							  numAverageServices(NA), 
							  numGoodServices(NG), 
							  numStrongServices(NS), 
							  LowerThresold is 1, 
							  UpperThreshold is 1 + NW, 
							  LowerThresold < K, 
							  K =< UpperThreshold, 
							  setPasswordRequirements(ServiceK, weak).
setPasswordRequirements(K) :- atom_number(AtomK, K), 
							  atom_concat(service, AtomK, ServiceK), 
							  numWeakServices(NW), 
							  numAverageServices(NA), 
							  numGoodServices(NG), 
							  numStrongServices(NS), 
							  LowerThresold is 1 + NW, 
							  UpperThreshold is 1 + NW + NA, 
							  LowerThresold < K, K =< UpperThreshold, 
							  setPasswordRequirements(ServiceK, average).
setPasswordRequirements(K) :- atom_number(AtomK, K), 
							  atom_concat(service, AtomK, ServiceK), 
							  numWeakServices(NW), numAverageServices(NA), 
							  numGoodServices(NG), 
							  numStrongServices(NS), 
							  LowerThresold is 1 + NW + NA, 
							  UpperThreshold is 1 + NW + NA + NG, 
							  LowerThresold < K, 
							  K =< UpperThreshold, 
							  setPasswordRequirements(ServiceK, good).
setPasswordRequirements(K) :- atom_number(AtomK, K), 
							  atom_concat(service, AtomK, ServiceK), 
							  numWeakServices(NW), 
							  numAverageServices(NA), 
							  numGoodServices(NG), 
							  numStrongServices(NS), 
							  LowerThresold is 1 + NW + NA + NG, 
							  UpperThreshold is 1 + NW + NA + NG + NS, 
							  LowerThresold < K, K =< UpperThreshold, 
							  setPasswordRequirements(ServiceK, strong).

% Setting up the first (target) one
setPasswordRequirements(1) :- targetServicePasswordCompositionStrength(Strength), 
							  setPasswordRequirements(service1, Strength), !.


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Determine Results
% - responses to various primitive actions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%% Responses
%%%%%%%%%%%%%%%%%%%%%%%%

%%% This is the first response we should send
% Here, all of the variables are instanteded for the first time
determineResult(initializeUser, User, services(X)) :- format('User ~w added to simulation.\n', [User]), 
													  services(X), 
													  assert(numAccountsCreated(User, 0)),
													  format('test1', []), 
													  assert(numUsernamesMemorized(User, 0)), 
													  format('test2', []), 
													  assert(numUsernamesWritten(User, 0)), 
													  format('test3', []), 
													  assert(numPasswordsMemorized(User, 0)), 
													  format('test4', []), 
													  assert(numPasswordsWritten(User, 0)), 
													  format('test5', []), 
													  assert(numPasswordsReset(User, 0)),
													  format('test6', []), !.



determineResult(navigateToCreateAccountPage(Service), User, error(noService)) :- not(serviceExists(Service)), 
																				format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]).
determineResult(navigateToCreateAccountPage(Service), User, success(usernameRequirements(UR), passwordRequirements(PR))) :- serviceExists(Service), 
																																usernameInitRequirements(Service, UR), 
																																format('Did we get tihs far\n', []),
																																passwordInitRequirements(Service, PR), 
																																format('User ~w performed ~w. Result: ~w.\n', [User, navigateToCreateAccountPage(Service), success(usernameRequirements(Service, UR), passwordRequirements(Service, PR))]).

determineResult(navigateToResetPasswordPage(Service), User, error(noService)) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]).
determineResult(navigateToResetPasswordPage(Service), User, success(passwordRequirements(PR))) :- serviceExists(Service), passwordInitRequirements(Service, PR), format('User ~w performed ~w. Result: ~w\n', [User, navigateToResetPasswordPage(Service), success(passwordRequirements(PR))]).



determineResult(enterDesiredUsername(Service, Username), User, error(noService)) :- not(serviceExists(Service)), format('Initialization failed in process - falut in service ~w \n', [Service]).
determineResult(enterDesiredUserame(Service, Username), User, Result) :- serviceExists(Service), 
																  usernameRespose(Service, Username, Response),
																  format('User ~w preformed ~w Result: ~w\n', [User, enterDesiredUserame(Service, Username), Result]).


%ask Vijay if I am correct in thinking that the user can have only one account in on the service
determineResult(enterDesiredPassword(Service, Password), User, error(noService)) :- not(serviceExists(Service)), 
																			 format('Initialization failed in process - falut in service ~w \n', [Service]). 
determineResult(enterDesiredPassword(Service, Password), User, Result) :- serviceExists(Service), 
																   % Test print statement
																   format('Working on enterPassword(~w, ~w)', [Service, Password]),
																   passwordResponse(Service, Password, Result), 
																   format('User ~w preformed ~w Result: ~w\n', [User, enterDesiredPassword(Service, Password), Result]).


determineResult(clickCreateAccountButton(Service, Username, Password), User, error(noService)) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]), !.
determineResult(clickCreateAccountButton(Service, Username, Password), User, success) :- serviceExists(Service), usernameResponse(Service, Username, UsernameResult), passwordResponse(Service, Password, PasswordResult), UsernameResult = success, PasswordResult = success(PasswordRating), assert(accountExists(Service, Username, Password, User)), retract(numAccountsCreated(User, X)), Y is X + 1, assert(numAccountsCreated(User, Y)), format('created account!\n'), !.
determineResult(clickCreateAccountButton(Service, Username, Password), User, error(UsernameResult, PasswordResult)) :- serviceExists(Service), usernameResponse(Service, Username, UsernameResult), passwordResponse(Service, Password, PasswordResult), UsernameResult = error(Reason), !.
determineResult(clickCreateAccountButton(Service, Username, Password), User, error(UsernameResult, PasswordResult)) :- serviceExists(Service), usernameResponse(Service, Username, UsernameResult), passwordResponse(Service, Password, PasswordResult), PasswordResult = error(Reason), !.


determineResult(clickSignInButton(Service, Username, Password), User, Result) :- processSignIn(Service, Username, Password, User, Result), !.

determineResult(clickSignOutButton(Service, Username), User, Result) :- processSignOut(Service, Username, User, Result), !.
																							
determineResult(memorizeUsername(Service), User, success) :- retract(numUsernamesMemorized(User, X)), 
															 Y is X+1, 
															 assert(numUsernamesMemorized(User, Y)), !.   
determineResult(memorizePassword(Service), User, success) :- retract(numPasswordsMemorized(User, X)), 
															 Y is X+1, 
															 assert(numPasswordsMemorized(User, Y)), !.

determineResult(writeUsernameOnPostit(Service), User, success) :- retract(numUsernamesWritten(User, X)), 
															 	  Y is X+1, 
																  assert(numUsernamesWritten(User, Y)), !.
determineResult(writeUsernameOnPostit(Service), User, success) :- retract(numPasswordsWritten(User, X)), 
															 	  Y is X+1, 
															 	  assert(numPasswordsWritten(User, Y)), !.


determineResult(clickResetPasswordButton(Service, Username, Password), User, error(noService)) :- not(serviceExists(Service)), 
																								  format('Initialization failed in process - falut in service ~w, which does not exist.\n', [Service]), !.
determineResult(clickResetPasswordButton(Service, Username, Password), User, error(noUsername(Username))) :- serviceExists(Service), 
																											 not(accountExists(Service, Username, _, User)), 
																											 format('Could not reset account: username is unknown\n'), !.
determineResult(clickResetPasswordButton(Service, Username, Password), User, PasswordResult) :- serviceExists(Service), 
																								accountExists(Service, Username, _, User), 
																								passwordResponse(Service, Password, PasswordResult), 
																								PasswordResult = error(Reason), 
																								retract(accountExists(Service, Username, _, User)), 
																								assert(accountExists(Service, Username, Password, User)), 
																								format('Reset password on account! (pw was  inadequate but we accept inadequate passwords during password resets)\n'), !.
determineResult(clickResetPasswordButton(Service, Username, Password), User, success) :- serviceExists(Service), 
																						 accountExists(Service, Username, _, User), 
																						 passwordResponse(Service, Password, PasswordResult), 
																						 PasswordResult = success(PasswordRating), 
																						 retract(accountExists(Service, Username, _, User)), 
																						 assert(accountExists(Service, Username, Password, User)), 
																						 retract(numPasswordsReset(User, X)), Y is X + 1, 
																						 assert(numPasswordsReset(User, Y)), 
																						 retractall(passwordResetPerformed(Service, User)), 
																						 assert(passwordResetPerformed(Service, User)), 
																						 retractall(passwordWrittenDown(Service, User)), 
																						 format('Account password successfully reset\n'), !.



%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%% Utility
%%%%%%%%%%%%%%%%%%%%%%%%



% Username response - used to determine result for enterUsername
% Returns Succes if satisfies requirements, error otherwise
usernameResponse(Service, Username, error([isNot(Username)])) :- usernameTaken(Service, Username).
usernameResponse(Service, Username, error([H])) :- not(usernameTaken(Service, Username)), 
												   usernameRequirements(Service, Requirements),
												   getUnsatisfiedRequirements(Username, Requirements, [H|T]), !.											
usernameRespose(Service, Username, success) :- not(usernameTaken(Service, Requirements)), 
											   usernameRequirements(Service, Requirements),
											   getUnsatisfiedRequirements(Username, Requirements, UnsatisfiedRequirements),
											   UnsatisfiedRequirements = [], !.												   


% Password Response - used to determine result for enterPassword
% Returns success with password Strength if satisfies requirements, error otherwise
passwordResponse(Service, Password, error([H])) :- passwordRequirements(Service, Requirements),
												   getUnsatisfiedRequirements(Password, Requirements, [H|T]),
												   format('Checking password requirements: UnsatisfiedRequirements found \n', []), !.
passwordResponse(Service, Password, success(Strength)) :- passwordRequirements(Service, Requirements),
												   		  getUnsatisfiedRequirements(Password, Requirements, UR),
												   		  UR = [], 
												   		  passwordStrength(Service, Password, Strength),
												   		  %Debugging messages
												   		  ansi_format([fg(cyan)], 'Password ~w satisfies requirements. Strength: ~w \n', [Password, Strength]), !. 

% Determines Strength of a human generated password in bits
passwordStrength(Service, Password, weak) :- passwordScore(Service, Password, Score), Score < 13.
passwordStrength(Service, Password, fair) :- passwordScore(Service, Password, Score), Score >= 13, Score < 19.
passwordStrength(Service, Password, good) :- passwordScore(Service, Password, Score), Score >= 19, Score < 23.
passwordStrength(Service, Password, strong) :- passwordScore(Service, Password, Score), Score >= 23.
		
% Calculate scores based on http://goo.gl/PxV3nK									   
passwordScore(Service, Password, Score) :- atom_length(Password, L),
										   ( (L =< 8, X is L-1, Y is 2*X, Tally is 4+Y);
										   	 (L > 8, L =< 20, X is L-8, Y is X*1.5, Tally is X+18);
										   	 (L > 20, X is L-20, Tally is 32+X)
										   ),	 
										   Score is Tally + random(6), !.

%%% Helpers for processing signing in
% Returns success and asserts signIn flag if not sign in and account exists, error otherwise
processSignIn(Service, Username, Password, User, error(usernameDoesNotExist)) :- not(accountExists(Service, Username, _, _)), !.
processSignIn(Service, Username, Password, User, error(passwordIncorrect)) :- accountExists(Service, Username, TruePassword, _), 
																			  Password \= TruePassword, !.
processSignIn(Service, Username, Password, User, error(signedInElsewhere)) :- signedIn(Service, Username, _), !.
processSignIn(Service, Username, Password, User, success) :- not(signedIn(Service, Username, _)), 
															 assert(signedIn(Service, Username, User)), !.

%%% Helpers for processing sighning out
% Returns success and retracts signed in flag if signed in into service, error otherwise
processSignOut(Service, Username, User, error(usernameDoesNotExist)) :- not(accountExists(Service, Username, _, _)), !.
processSignOut(Service, Username, User, error(notSignedIn)) :- accountExists(Service, Username, _, _), not(signedIn(Service, Username, User)), !.
processSignOut(Service, Username, User, success) :- signedIn(Service, Username, _), retractall(signedIn(Service, Username, _)), !.



% Helper clause that returns true if account with that username already exists
usernameTaken(Service, Username) :- accountExists(Service, Username, Password, Owner).


% write passwordRequirements
% write getUnsatisfiedRequirements
% write accountExists