:- dynamic(accountExists/4).
:- dynamic(determineResult/3).
:- dynamic(signedIn/3).

:- consult('services_util').

services([gmail, hotmail, yahoomail]).

serviceExists(Service) :- services(Services), member(Service, Services).

determineResult(initializeUser, User, services(X)) :- format('User ~w added to simulation.\n', [User]), services(X).

determineResult(navigateToCreateAccountPage(Service), User, error(noService)) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]).
determineResult(navigateToCreateAccountPage(Service), User, success(usernameRequirements(UR), passwordRequirements(PR))) :- serviceExists(Service), usernameNavRequirements(Service, UR), passwordNavRequirements(Service, PR), format('User ~w performed ~w. Result: ~w', [User, navigateToCreateAccountPage(Service), success(usernameRequirements(Service, UR), passwordRequirements(Service, PR))]).

determineResult(navigateToResetPasswordPage(Service), User, error(noService)) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]).
determineResult(navigateToResetPasswordPage(Service), User, success(passwordRequirements(PR))) :- serviceExists(Service), passwordNavRequirements(Service, PR), format('User ~w performed ~w. Result: ~w', [User, navigateToResetPasswordPage(Service), success(passwordRequirements(PR))]).


determineResult(enterDesiredUsername(Service, Username), User, error(noService)) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]).
determineResult(enterDesiredUsername(Service, Username), User, Result) :- serviceExists(Service), usernameResponse(Service, Username, Result), format('User ~w performed ~w. Result: ~w.\n', [User, enterDesiredUsername(Service, Username), Result]).

determineResult(enterDesiredPassword(Service, Password), User, error(noService)) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]).
determineResult(enterDesiredPassword(Service, Password), User, Result) :- serviceExists(Service), passwordResponse(Service, Password, Result), format('User ~w performed ~w. Result: ~w.\n', [User, enterDesiredPassword(Service, Password), Result]).


%%% TEST!!!!: determineResult(clickCreateAccountButton(Service, Username, Password), User, error(success, error([minLength(20)]))).
determineResult(clickCreateAccountButton(Service, Username, Password), User, error(noService)) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]), !.
determineResult(clickCreateAccountButton(Service, Username, Password), User, success) :- serviceExists(Service), usernameResponse(Service, Username, UsernameResult), passwordResponse(Service, Password, PasswordResult), UsernameResult = success, PasswordResult = success(PasswordRating), assert(accountExists(Service, Username, Password, User)), format('created account!\n'), !.
determineResult(clickCreateAccountButton(Service, Username, Password), User, error(UsernameResult, PasswordResult)) :- serviceExists(Service), usernameResponse(Service, Username, UsernameResult), passwordResponse(Service, Password, PasswordResult), UsernameResult = error(Reason), !.
determineResult(clickCreateAccountButton(Service, Username, Password), User, error(UsernameResult, PasswordResult)) :- serviceExists(Service), usernameResponse(Service, Username, UsernameResult), passwordResponse(Service, Password, PasswordResult), PasswordResult = error(Reason), !.

determineResult(clickResetPasswordButton(Service, Username, Password), User, error(noService)) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]), !.
determineResult(clickResetPasswordButton(Service, Username, Password), User, error(noUsername(Username))) :- serviceExists(Service), not(accountExists(Service, Username, _, User)), format('could not reset account since account with specified username does not exist!\n'), !.
determineResult(clickResetPasswordButton(Service, Username, Password), User, PasswordResult) :- serviceExists(Service), accountExists(Service, Username, _, User), passwordResponse(Service, Password, PasswordResult), PasswordResult = error(Reason), retract(accountExists(Service, Username, _, User)), assert(accountExists(Service, Username, Password, User)), format('reset password on account!\n'), !.
determineResult(clickResetPasswordButton(Service, Username, Password), User, success) :- serviceExists(Service), accountExists(Service, Username, _, User), passwordResponse(Service, Password, PasswordResult), PasswordResult = success(PasswordRating), retract(accountExists(Service, Username, _, User)), assert(accountExists(Service, Username, Password, User)), format('reset password on account!\n'), !.

determineResult(clickSignInButton(Service, Username, Password), User, Result) :- processSignIn(Service, Username, Password, User, Result), !.

determineResult(clickSignOutButton(Service, Username), User, Result) :- processSignOut(Service, Username, User, Result), !.

usernameResponse(Service, Username, error([isNot(Username)])) :- usernameTaken(Service, Username).
usernameResponse(Service, Username, error([H])) :- not(usernameTaken(Service, Username)), usernameRequirements(Service, Requirements), getUnsatisfiedRequirements(Username, Requirements, [H|T]), !.
usernameResponse(Service, Username, success) :- not(usernameTaken(Service, Username)), usernameRequirements(Service, Requirements), getUnsatisfiedRequirements(Username, Requirements, UnsatisfiedRequirements), UnsatisfiedRequirements = [], !.

% usernameResponse(Service, Username, error(alreadyExists(Username))) :- usernameTaken(Service, Username).
% usernameResponse(Service, Username, error(minLength(8))) :- string_length(Username, Length), Length < 8.
% usernameResponse(Service, Username, error(maxLength(32))) :- string_length(Username, Length), Length > 32.
% usernameResponse(Service, Username, success) :- not(usernameTaken(Service, Username)), string_length(Username, Length), Length >= 8, Length =< 32.

passwordResponse(Service, Password, error([H])) :- passwordRequirements(Service, Requirements), getUnsatisfiedRequirements(Password, Requirements, [H|T]), !.
passwordResponse(Service, Password, success(Strength)) :- passwordRequirements(Service, Requirements), getUnsatisfiedRequirements(Password, Requirements, UnsatisfiedRequirements), UnsatisfiedRequirements = [], passwordStrength(Service, Password, Strength), !.

passwordStrength(Service, Password, weak) :- passwordScore(Service, Password, Score), Score < 8.
passwordStrength(Service, Password, fair) :- passwordScore(Service, Password, Score), Score >= 8, Score < 10.
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

usernameNavRequirements(Service, [minLength(6)]).
passwordNavRequirements(Service, [minLength(6)]).

usernameRequirements(Service, [minLength(6), minLower(1), minUpper(1), maxLength(64)]).
passwordRequirements(Service, [minLength(6), minLower(1), minUpper(1), minDigit(2), minSpecial(1), maxLength(64)]).

% owner refers to the person who created the account...
% although in a real world, we may not know this, we may use it here to identify
% malicious users, password sharing, etc. in the simulation
usernameTaken(Service, Username) :- accountExists(Service, Username, Password, Owner).