:- dynamic(accountExists/4).
:- dynamic(determineResult/3).
:- dynamic(signedIn/3).

%%%%%%%%% REMOVE THIS! %%%%%%%%%%%%
%%%%%%%%%% JUST A TEST %%%%%%%%%%%%
accountExists(Service, test_un, a, a).

services([gmail, hotmail]).

serviceExists(Service) :- services(Services), member(Service, Services).

determineResult(initializeUser, User, services(X)) :- format('User ~w added to simulation.\n', [User]), services(X).

determineResult(enterDesiredUsername(Service, Username), User, noService) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]).
determineResult(enterDesiredUsername(Service, Username), User, Result) :- serviceExists(Service), usernameResponse(Service, Username, Result), format('User ~w performed ~w. Result: ~w.\n', [User, enterDesiredUsername(Service, Username), Result]).

determineResult(enterDesiredPassword(Service, Password), User, noService) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]).
determineResult(enterDesiredPassword(Service, Password), User, Result) :- serviceExists(Service), passwordResponse(Service, Password, Result), format('User ~w performed ~w. Result: ~w.\n', [User, enterDesiredPassword(Service, Password), Result]).

determineResult(clickCreateAccountButton(Service, Username, Password), User, noService) :- not(serviceExists(Service)), format('This should never happen! User tried to access service ~w, which does not exist.\n', [Service]), !.
determineResult(clickCreateAccountButton(Service, Username, Password), User, accept) :- serviceExists(Service), usernameResponse(Service, Username, UsernameResult), passwordResponse(Service, Password, PasswordResult), UsernameResult = accept, PasswordResult = accept(PasswordRating), assert(accountExists(Service, Username, Password, User)), format('created account!\n'), !.
determineResult(clickCreateAccountButton(Service, Username, Password), User, reject(UsernameResult, PasswordResult)) :- serviceExists(Service), usernameResponse(Service, Username, UsernameResult), passwordResponse(Service, Password, PasswordResult), UsernameResult = reject(Reason), !.
determineResult(clickCreateAccountButton(Service, Username, Password), User, reject(UsernameResult, PasswordResult)) :- serviceExists(Service), usernameResponse(Service, Username, UsernameResult), passwordResponse(Service, Password, PasswordResult), PasswordResult = reject(Reason), !.

determineResult(clickSignInButton(Service, Username, Password), User, Result) :- processSignIn(Service, Username, Password, User, Result), !.

determineResult(clickSignOutButton(Service, Username), User, Result) :- processSignOut(Service, Username, User, Result), !.

usernameResponse(Service, Username, reject(alreadyTaken)) :- usernameTaken(Service, Username).
usernameResponse(Service, Username, reject(tooShort)) :- string_length(Username, Length), Length < 8.
usernameResponse(Service, Username, reject(tooLong)) :- string_length(Username, Length), Length > 32.
usernameResponse(Service, Username, accept) :- not(usernameTaken(Service, Username)), string_length(Username, Length), Length >= 8, Length =< 32.

passwordResponse(Service, Password, reject(tooShort)) :- string_length(Password, Length), Length < 8.
passwordResponse(Service, Password, reject(tooLong)) :- string_length(Password, Length), Length > 64.
passwordResponse(Service, Password, accept(weak)) :- string_length(Password, Length), Length >= 8, Length < 10.
passwordResponse(Service, Password, accept(fair)) :- string_length(Password, Length), Length >= 10, Length < 12.
passwordResponse(Service, Password, accept(good)) :- string_length(Password, Length), Length >= 12, Length < 16.
passwordResponse(Service, Password, accept(strong)) :- string_length(Password, Length), Length >= 16, Length < 64.

processSignIn(Service, Username, Password, User, reject(usernameDoesNotExist)) :- not(accountExists(Service, Username, _, _)), !.
processSignIn(Service, Username, Password, User, reject(passwordIncorrect)) :- accountExists(Service, Username, TruePassword, _), Password \= TruePassword, !.
processSignIn(Service, Username, Password, User, reject(signedInElsewhere)) :- signedIn(Service, Username, _), !.
processSignIn(Service, Username, Password, User, accept) :- not(signedIn(Service, Username, _)), assert(signedIn(Service, Username, User)), !.

processSignOut(Service, Username, User, reject(usernameDoesNotExist)) :- not(accountExists(Service, Username, _, _)), !.
processSignOut(Service, Username, User, reject(notSignedIn)) :- accountExists(Service, Username, _, _), not(signedIn(Service, Username, User)), !.
processSignOut(Service, Username, User, accept) :- signedIn(Service, Username, _), retractall(signedIn(Service, Username, _)), !.


% owner refers to the person who created the account...
% although in a real world, we may not know this, we may use it here to identify
% malicious users, password sharing, etc. in the simulation
usernameTaken(Service, Username) :- accountExists(Service, Username, Password, Owner).