:- dynamic(accountExists/4).
:- dynamic(determineResult/3).
:- dynamic(signedIn/3).
:- dynamic(printWorldState/0).
:- dynamic(numAccountsCreated/1).
:- dynamic(numUsernamesMemorized/1).
:- dynamic(numUsernamesWritten/1).
:- dynamic(numPasswordsMemorized/1).
:- dynamic(numPasswordsWritten/1).
:- dynamic(numPasswordsReset/1).

:- dynamic(servicesCreated/0).
:- dynamic(services/1).
:- dynamic(passwordRequirements/2).
:- dynamic(testServiceStrength/1).

:- dynamic(passwordResetPerformed/2).
:- dynamic(passwordWrittenDown/2).

:- consult('services_util').

%%%%%%%%%%%%%%
% parameters %
%%%%%%%%%%%%%%

targetServicePasswordCompositionStrength(weak). % weak, average, good, or strong

% any one of these may be one less than the true value as the target service is not accounted for in the numbers below
numWeakServices(7).
numAverageServices(8).
numGoodServices(8).
numStrongServices(8).

numServices(N) :- numWeakServices(NW), numAverageServices(NA), numGoodServices(NG), numStrongServices(NS), N is NW + NA + NG + NS + 1, !.

% i do not think this is used anymore...
% direct attack risk associated with service
% attackRisk(Service, User, 0.2) :- passwordWrittenDown(Service, User).
% attackRisk(Service, User, 0.1) :- not(passwordWrittenDown(Service, User)).

reuseAttackRisk(0.25). % probability that an attacker will reuse passwords across all services


rawPasswordStrength(Service, User, 0.1) :- accountExists(Service, _, Password, User), passwordScore(Service, Password, Score), Score =< 2.
rawPasswordStrength(Service, User, 0.2) :- accountExists(Service, _, Password, User), passwordScore(Service, Password, Score), Score > 2, Score =< 4.
rawPasswordStrength(Service, User, 0.3) :- accountExists(Service, _, Password, User), passwordScore(Service, Password, Score), Score > 4, Score =< 8.
rawPasswordStrength(Service, User, 0.4) :- accountExists(Service, _, Password, User), passwordScore(Service, Password, Score), Score > 8, Score =< 16.
rawPasswordStrength(Service, User, 0.5) :- accountExists(Service, _, Password, User), passwordScore(Service, Password, Score), Score > 16.
rawPasswordStrength(Service, User, 1) :- not(accountExists(Service, _, _, User).

serviceVulnerabilityRisk(Service, User, Risk) :- rawPasswordStrength(Service, User, Strength), Risk is (1 - Strength) * 0.2.

stolenPasswordAttackRisk(Service, User, 0.25) :- accountExists(Service, _, _, User), passwordWrittenDown(Service, User).
stolenPasswordAttackRisk(Service, User, 0) :- accountExists(Service, _, _, User), not(passwordWrittenDown(Service, User)).
stolenPasswordAttackRisk(Service, User, 0) :- not(accountExists(Service, _, _, User)).

probabilitySafeFromDirectAttack(Service, User, P) :- accountExists(Service, _, _, User), serviceVulnerabilityRisk(Service, User, SVR), stolenPasswordAttackRisk(Service, User, SPAR), P is (1 - SVR) * (1 - SPAR), !.
probabilitySafeFromDirectAttack(Service, User, 1) :- not(accountExists(Service, _, _, User)), !.

probabilitySafe(Service, User, P) :- probabilitySafeFromDirectAttack(Service, User, PDirect), probabilitySafeFromAllIndirectAttacks(Service, User, PIndirect), P is PDirect * PIndirect, !.

%probabilitySafe(Service, User, P) :- probabilitySafeFromDirectAttack(Service, User, P), !.

probabilitySafeFromAllIndirectAttacks(Service, User, P) :- services(L), probabilitySafeFromAllIndirectAttacksHelper(Service, L, User, P), !.

probabilitySafeFromAllIndirectAttacksHelper(IndirectlyAttackedService, [DirectlyAttackedService | Rest], User, P) :- probabilitySafeFromIndirectAttack(IndirectlyAttackedService, DirectlyAttackedService, User, PThis), probabilitySafeFromAllIndirectAttacksHelper(IndirectlyAttackedService, Rest, User, PRecurse), P is PThis * PRecurse, !.
probabilitySafeFromAllIndirectAttacksHelper(_, [], User, 1) :- !.

probabilitySafeFromIndirectAttack(IndirectlyAttackedService, DirectlyAttackedService, User, P) :- IndirectlyAttackedService \= DirectlyAttackedService, accountExists(IndirectlyAttackedService, Username, Password, User), accountExists(DirectlyAttackedService, Username, Password, User), probabilitySafeFromDirectAttack(DirectlyAttackedService, User, PSafeFromDirectAttack), reuseAttackRisk(RAR), P is 1 - (1 - PSafeFromDirectAttack) * RAR, !.

probabilitySafeFromIndirectAttack(IndirectlyAttackedService, DirectlyAttackedService, User, 1) :- IndirectlyAttackedService \= DirectlyAttackedService, accountExists(IndirectlyAttackedService, Username1, Password1, User), accountExists(DirectlyAttackedService, Username2, Password2, User), Username1 \= Username2, !.

probabilitySafeFromIndirectAttack(IndirectlyAttackedService, DirectlyAttackedService, User, 1) :- IndirectlyAttackedService \= DirectlyAttackedService, accountExists(IndirectlyAttackedService, Username1, Password1, User), accountExists(DirectlyAttackedService, Username2, Password2, User), Password1 \= Password2, !.

probabilitySafeFromIndirectAttack(IndirectlyAttackedService, DirectlyAttackedService, User, 1) :- IndirectlyAttackedService \= DirectlyAttackedService, not(accountExists(IndirectlyAttackedService, _, _, User)), !.
probabilitySafeFromIndirectAttack(IndirectlyAttackedService, DirectlyAttackedService, User, 1) :- IndirectlyAttackedService \= DirectlyAttackedService, not(accountExists(DirectlyAttackedService, _, _, User)), !.

probabilitySafeFromIndirectAttack(IndirectlyAttackedService, DirectlyAttackedService, User, 1) :- IndirectlyAttackedService = DirectlyAttackedService, !.

%%%%%%%%%%%%%%%%%%
% initial values %
% DO NOT CHANGE! %
%%%%%%%%%%%%%%%%%%

numPasswordsReset(0).
numUsernamesMemorized(0).
numPasswordsMemorized(0).
numPasswordsWritten(0).
numAccountsCreated(0).
numUsernamesWritten(0).

%%%%%%%%%%%%%%%%%%
% services logic %
%%%%%%%%%%%%%%%%%%

printWorldState :- ansi_format([fg(blue)], 'printing world state...\n', []), numAccountsCreated(AC), numUsernamesMemorized(UM), numUsernamesWritten(UW), numPasswordsMemorized(PM), numPasswordsWritten(PW), numPasswordsReset(PR), ansi_format([fg(blue)], 'number of accounts created: ~w\nnumber of usernames memorized: ~w\nnumber of usernames written down: ~w\nnumber of passwords memorized: ~w\nnumber of passwords written down: ~w\nnumber of password resets performed: ~w\n', [AC, UM, UW, PM, PW, PR]), printExposureForService1, printAverageExposure, !.

printExposureForService1 :- foreach(id(User), printExposureForService1(User)).

printExposureForService1(User) :- printIfPasswordWrittenDownForService1(User), printIfPasswordResetPerformedForService1(User), probabilitySafe(service1, User, P), ansi_format([fg(green)], 'Password security measure for user ~w at target service ~w: ~w.\n', [User, service1, P]), !.

printAverageExposure :- foreach(id(User), printAverageExposureForUser(User)).

printAverageExposureForUser(User) :- services(Services), computeNetExposureForUser(User, Services, NetExposure), numServices(NumServices), AverageExposure is NetExposure / NumServices, ansi_format([fg(green)], 'Average password security measure for user ~w is ~w.\n', [User, AverageExposure]), !.

computeNetExposureForUser(User, [H | T], NetExposure) :- probabilitySafe(H, User, P), computeNetExposureForUser(User, T, NetExposureRecurse), NetExposure is P + NetExposureRecurse, !.

computeNetExposureForUser(User, [], 0) :- !.

% I do not think this is used anymore...
%directAttackRiskSet([], 0).
%directAttackRiskSet([(Service, User)|T], Risk) :- attackRisk(Service, User, RiskH), directAttackRiskSet(T, RiskR), Risk is RiskH + RiskR, !.

printIfPasswordWrittenDownForService1(User) :- passwordWrittenDown(service1, User), ansi_format([fg(green)], 'User ~w wrote down password for service1.\n', [User]), !.
printIfPasswordWrittenDownForService1(User) :- not(passwordWrittenDown(service1, User)), ansi_format([fg(green)], 'User ~w did NOT write down password for service1.\n', [User]), !.

printIfPasswordResetPerformedForService1(User) :- passwordResetPerformed(service1, User), ansi_format([fg(green)], 'User ~w did reset password for service1.\n', [User]), !.
printIfPasswordResetPerformedForService1(User) :- not(passwordResetPerformed(service1, User)), ansi_format([fg(green)], 'User ~w did NOT reset password for service1.\n', [User]), !.

services(S) :- not(servicesCreated), format('creating services...\n', []), format('services - cp1.\n', []), numServices(NumServices), format('services - cp2.\n', []), createServices(NumServices, S), format('services - cp3.\n', []), assert(services(S)), format('services - cp4.\n', []), asserta(servicesCreated), format('created services: ~w.\n', [S]), !.

createServices(N, [Service|Rest]) :- format('createServices: N = ~w.\n', [N]), N > 1, atom_number(AtomN, N), atom_concat(service, AtomN, Service), NMinus1 is N - 1, setPasswordRequirements(N), createServices(NMinus1, Rest), !.

createServices(1, [service1]) :- setPasswordRequirements(1).

setPasswordRequirements(Service, weak) :- format('setting weak password requirements for ~w.\n', [Service]), MinLength is 1 + random(4), MinLower is random(2), MinUpper is random(2), assert(passwordRequirements(Service, [minLength(MinLength), minLower(MinLower), minUpper(MinUpper), minDigit(0), minSpecial(0), maxLength(64)])).
setPasswordRequirements(Service, average) :- format('setting average password requirements for ~w.\n', [Service]), MinLength is 4 + random(5), MinLower is 1 + random(2), MinUpper is 1 + random(2), MinDigit is random(2), assert(passwordRequirements(Service, [minLength(MinLength), minLower(MinLower), minUpper(MinUpper), minDigit(MinDigit), minSpecial(0), maxLength(64)])).
setPasswordRequirements(Service, good) :- format('setting good password requirements for ~w.\n', [Service]), MinLength is 8 + random(5), MinLower is 1 + random(3), MinUpper is 1 + random(3), MinDigit is 1 + random(2), MinSpecial is random(2), assert(passwordRequirements(Service, [minLength(MinLength), minLower(MinLower), minUpper(MinUpper), minDigit(MinDigit), minSpecial(MinSpecial), maxLength(64)])).
setPasswordRequirements(Service, strong) :- format('setting strong password requirements for ~w.\n', [Service]), MinLength is 12 + random(5), MinLower is 2 + random(3), MinUpper is 2 + random(3), MinDigit is 2 + random(3), MinSpecial is 1 + random(2), assert(passwordRequirements(Service, [minLength(MinLength), minLower(MinLower), minUpper(MinUpper), minDigit(MinDigit), minSpecial(MinSpecial), maxLength(64)])).


setPasswordRequirements(K) :- atom_number(AtomK, K), atom_concat(service, AtomK, ServiceK), numWeakServices(NW), numAverageServices(NA), numGoodServices(NG), numStrongServices(NS), LowerThresold is 1, UpperThreshold is 1 + NW, LowerThresold < K, K =< UpperThreshold, setPasswordRequirements(ServiceK, weak).

setPasswordRequirements(K) :- atom_number(AtomK, K), atom_concat(service, AtomK, ServiceK), numWeakServices(NW), numAverageServices(NA), numGoodServices(NG), numStrongServices(NS), LowerThresold is 1 + NW, UpperThreshold is 1 + NW + NA, LowerThresold < K, K =< UpperThreshold, setPasswordRequirements(ServiceK, average).

setPasswordRequirements(K) :- atom_number(AtomK, K), atom_concat(service, AtomK, ServiceK), numWeakServices(NW), numAverageServices(NA), numGoodServices(NG), numStrongServices(NS), LowerThresold is 1 + NW + NA, UpperThreshold is 1 + NW + NA + NG, LowerThresold < K, K =< UpperThreshold, setPasswordRequirements(ServiceK, good).

setPasswordRequirements(K) :- atom_number(AtomK, K), atom_concat(service, AtomK, ServiceK), numWeakServices(NW), numAverageServices(NA), numGoodServices(NG), numStrongServices(NS), LowerThresold is 1 + NW + NA + NG, UpperThreshold is 1 + NW + NA + NG + NS, LowerThresold < K, K =< UpperThreshold, setPasswordRequirements(ServiceK, strong).

setPasswordRequirements(1) :- targetServicePasswordCompositionStrength(Strength), setPasswordRequirements(service1, Strength), !.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% old randomized approach to creating services %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% weakPasswordCompositionBias(32).
% averagePasswordCompositionBias(32).
% goodPasswordCompositionBias(32).
% strongPasswordCompositionBias(32).

%createServices(N, [Service|Rest]) :- format('createServices: N = ~w.\n', [N]), N > 1, atom_number(AtomN, N), atom_concat(service, AtomN, Service), NMinus1 is N - 1, setPasswordRequirements(Service), createServices(NMinus1, Rest), !.

%createServices(1, [service1]) :- setPasswordRequirements(service1).

%setPasswordRequirements(service1) :- targetServicePasswordCompositionStrength(Strength), setPasswordRequirements(service1, Strength), !.

%setPasswordRequirements(Service) :- Service \= service1, generatePasswordCompositionStrength(Strength), setPasswordRequirements(Service, Strength), !.

%generatePasswordCompositionStrength(Strength) :- weakPasswordCompositionBias(WB), averagePasswordCompositionBias(AB), goodPasswordCompositionBias(GB), strongPasswordCompositionBias(SB), Net is  WB + AB + GB + SB, IntegerRepresentation is 1 + random(Net), mapIntegerToStrength(IntegerRepresentation, WB, AB, GB, SB, Strength), !.

%mapIntegerToStrength(Int, WB, AB, GB, SB, weak) :- Int =< WB, !.
%mapIntegerToStrength(Int, WB, AB, GB, SB, average) :- Int > WB, Int =< WB + AB, !.
%mapIntegerToStrength(Int, WB, AB, GB, SB, good) :- Int >  WB + AB, Int =< WB + AB + GB, !.
%mapIntegerToStrength(Int, WB, AB, GB, SB, strong) :- Int > WB + AB + GB, Int =< WB + AB + GB + SB, !.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

serviceExists(Service) :- services(Services), member(Service, Services).

determineResult(initializeUser, User, services(X)) :- format('User ~w added to simulation.\n', [User]), services(X).

determineResult(navigateToCreateAccountPage(Service), User, error(noService)) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]).
determineResult(navigateToCreateAccountPage(Service), User, success(usernameRequirements(UR), passwordRequirements(PR))) :- serviceExists(Service), usernameNavRequirements(Service, UR), passwordNavRequirements(Service, PR), format('User ~w performed ~w. Result: ~w.\n', [User, navigateToCreateAccountPage(Service), success(usernameRequirements(Service, UR), passwordRequirements(Service, PR))]).

determineResult(navigateToResetPasswordPage(Service), User, error(noService)) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]).
determineResult(navigateToResetPasswordPage(Service), User, success(passwordRequirements(PR))) :- serviceExists(Service), passwordNavRequirements(Service, PR), format('User ~w performed ~w. Result: ~w\n', [User, navigateToResetPasswordPage(Service), success(passwordRequirements(PR))]).


determineResult(enterDesiredUsername(Service, Username), User, error(noService)) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]).
determineResult(enterDesiredUsername(Service, Username), User, Result) :- serviceExists(Service), usernameResponse(Service, Username, Result), format('User ~w performed ~w. Result: ~w.\n', [User, enterDesiredUsername(Service, Username), Result]).

determineResult(enterDesiredPassword(Service, Password), User, error(noService)) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]).
determineResult(enterDesiredPassword(Service, Password), User, Result) :- format('trying to determine result for enterDesiredPassword(~w, ~w): cp 1.\n', [Service,Password]), serviceExists(Service), format('trying to determine result for enterDesiredPassword(~w, ~w): cp 2.\n', [Service,Password]), passwordResponse(Service, Password, Result), format('User ~w performed ~w. Result: ~w.\n', [User, enterDesiredPassword(Service, Password), Result]).


%%% TEST!!!!: determineResult(clickCreateAccountButton(Service, Username, Password), User, error(success, error([minLength(20)]))).
determineResult(clickCreateAccountButton(Service, Username, Password), User, error(noService)) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]), !.
determineResult(clickCreateAccountButton(Service, Username, Password), User, success) :- serviceExists(Service), usernameResponse(Service, Username, UsernameResult), passwordResponse(Service, Password, PasswordResult), UsernameResult = success, PasswordResult = success(PasswordRating), assert(accountExists(Service, Username, Password, User)), retract(numAccountsCreated(X)), Y is X + 1, assert(numAccountsCreated(Y)), format('created account!\n'), !.
determineResult(clickCreateAccountButton(Service, Username, Password), User, error(UsernameResult, PasswordResult)) :- serviceExists(Service), usernameResponse(Service, Username, UsernameResult), passwordResponse(Service, Password, PasswordResult), UsernameResult = error(Reason), !.
determineResult(clickCreateAccountButton(Service, Username, Password), User, error(UsernameResult, PasswordResult)) :- serviceExists(Service), usernameResponse(Service, Username, UsernameResult), passwordResponse(Service, Password, PasswordResult), PasswordResult = error(Reason), !.

determineResult(clickResetPasswordButton(Service, Username, Password), User, error(noService)) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]), !.
determineResult(clickResetPasswordButton(Service, Username, Password), User, error(noUsername(Username))) :- serviceExists(Service), not(accountExists(Service, Username, _, User)), format('could not reset account since account with specified username does not exist!\n'), !.
determineResult(clickResetPasswordButton(Service, Username, Password), User, PasswordResult) :- serviceExists(Service), accountExists(Service, Username, _, User), passwordResponse(Service, Password, PasswordResult), PasswordResult = error(Reason), retract(accountExists(Service, Username, _, User)), assert(accountExists(Service, Username, Password, User)), format('reset password on account! (pw was  inadequate but we accept inadequate passwords during password resets)\n'), !.
determineResult(clickResetPasswordButton(Service, Username, Password), User, success) :- serviceExists(Service), accountExists(Service, Username, _, User), passwordResponse(Service, Password, PasswordResult), PasswordResult = success(PasswordRating), retract(accountExists(Service, Username, _, User)), assert(accountExists(Service, Username, Password, User)), retract(numPasswordsReset(X)), Y is X + 1, assert(numPasswordsReset(Y)), retractall(passwordResetPerformed(Service, User)), assert(passwordResetPerformed(Service, User)), retractall(passwordWrittenDown(Service, User)), format('reset password on account!\n'), !.

determineResult(clickSignInButton(Service, Username, Password), User, Result) :- processSignIn(Service, Username, Password, User, Result), !.

determineResult(clickSignOutButton(Service, Username), User, Result) :- processSignOut(Service, Username, User, Result), !.

determineResult(writeUsernameOnPostIt(Service), User, success) :- retract(numUsernamesWritten(X)), Y is X + 1, assert(numUsernamesWritten(Y)), !.

determineResult(writePasswordOnPostIt(Service), User, success) :- retract(numPasswordsWritten(X)), Y is X + 1, assert(numPasswordsWritten(Y)), retractall(passwordWrittenDown(Service, User)), assert(passwordWrittenDown(Service, User)), !.


determineResult(memorizeUsername(Service), User, success) :- retract(numUsernamesMemorized(X)), Y is X + 1, assert(numUsernamesMemorized(Y)), !.

determineResult(memorizePassword(Service), User, success) :- retract(numPasswordsMemorized(X)), Y is X + 1, assert(numPasswordsMemorized(Y)), !.

usernameResponse(Service, Username, error([isNot(Username)])) :- usernameTaken(Service, Username).
usernameResponse(Service, Username, error([H])) :- not(usernameTaken(Service, Username)), usernameRequirements(Service, Requirements), getUnsatisfiedRequirements(Username, Requirements, [H|T]), !.
usernameResponse(Service, Username, success) :- not(usernameTaken(Service, Username)), usernameRequirements(Service, Requirements), getUnsatisfiedRequirements(Username, Requirements, UnsatisfiedRequirements), UnsatisfiedRequirements = [], !.

% usernameResponse(Service, Username, error(alreadyExists(Username))) :- usernameTaken(Service, Username).
% usernameResponse(Service, Username, error(minLength(8))) :- string_length(Username, Length), Length < 8.
% usernameResponse(Service, Username, error(maxLength(32))) :- string_length(Username, Length), Length > 32.
% usernameResponse(Service, Username, success) :- not(usernameTaken(Service, Username)), string_length(Username, Length), Length >= 8, Length =< 32.

passwordResponse(Service, Password, error([H])) :- format('passwordResponse: error branch - cp 1.\n'), passwordRequirements(Service, Requirements), format('passwordResponse: error branch - cp 2.\n'), getUnsatisfiedRequirements(Password, Requirements, [H|T]), format('passwordResponse: error branch - END.\n'), !.
passwordResponse(Service, Password, success(Strength)) :- format('passwordResponse: success branch - cp 1.\n'), passwordRequirements(Service, Requirements), format('passwordResponse: success branch - cp 2.\n'), getUnsatisfiedRequirements(Password, Requirements, UnsatisfiedRequirements), format('passwordResponse: success branch - cp 3.\n'), UnsatisfiedRequirements = [], format('passwordResponse: success branch - cp 4.\n'), passwordStrength(Service, Password, Strength), format('passwordResponse: success branch - END.\n'), !.

passwordStrength(Service, Password, weak) :- passwordScore(Service, Password, Score), Score < 8.
passwordStrength(Service, Password, fair) :- passwordScore(Service, Password, Score), Score >= 8, Score < 12.
passwordStrength(Service, Password, good) :- passwordScore(Service, Password, Score), Score >= 12, Score < 16.
passwordStrength(Service, Password, strong) :- passwordScore(Service, Password, Score), Score >= 16.

passwordScore(Service, Password, Score) :- atom_length(Password, Score).

processSignIn(Service, Username, Password, User, error(usernameDoesNotExist)) :- not(accountExists(Service, Username, _, _)), !.
processSignIn(Service, Username, Password, User, error(passwordIncorrect)) :- accountExists(Service, Username, TruePassword, _), Password \= TruePassword, !.
processSignIn(Service, Username, Password, User, error(signedInElsewhere)) :- signedIn(Service, Username, _), !.
processSignIn(Service, Username, Password, User, success) :- not(signedIn(Service, Username, _)), assert(signedIn(Service, Username, User)), !.

processSignOut(Service, Username, User, error(usernameDoesNotExist)) :- not(accountExists(Service, Username, _, _)), !.
processSignOut(Service, Username, User, error(notSignedIn)) :- accountExists(Service, Username, _, _), not(signedIn(Service, Username, User)), !.
processSignOut(Service, Username, User, success) :- signedIn(Service, Username, _), retractall(signedIn(Service, Username, _)), !.

usernameNavRequirements(Service, [minLength(4)]).
passwordNavRequirements(Service, [minLength(4)]).

usernameRequirements(Service, [minLength(4), minLower(1), minUpper(1), maxLength(64)]).
%passwordRequirements(aol, [minLength(4), minLower(0), minUpper(0), minDigit(0), minSpecial(0), maxLength(64)]).
%passwordRequirements(hotmail, [minLength(8), minLower(0), minUpper(0), minDigit(0), minSpecial(0), maxLength(64)]).
%passwordRequirements(yahoomail, [minLength(12), minLower(1), minUpper(1), minDigit(0), minSpecial(0), maxLength(64)]).
%passwordRequirements(gmail, [minLength(20), minLower(2), minUpper(2), minDigit(2), minSpecial(2), maxLength(64)]).

%passwordRequirements(Service, [minLength(6), minLower(1), minUpper(1), minDigit(2), minSpecial(1), maxLength(64)]).

% owner refers to the person who created the account...
% although in a real world, we may not know this, we may use it here to identify
% malicious users, password sharing, etc. in the simulation
usernameTaken(Service, Username) :- accountExists(Service, Username, Password, Owner).