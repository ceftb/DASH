% -*- Mode: Prolog -*-

% Simple mail processing agent whose goal is to have all the unread
% mail responded to. It receives a reward for getting work done for
% its boss, which requires opening attachments in emails from the boss
% and from colleagues. It receives a negative reward from opening
% attachments in Phishing email.

:- style_check(-singleton).
:- style_check(-discontiguous).

:-dynamic(mail/8).
:-dynamic(nextID/1).
:-dynamic(mailRead/2).
:-dynamic(email/1).
:-dynamic(url/2).
:-dynamic(from/2).
:-dynamic(subject/2).
:-dynamic(text/2).
:-dynamic(doNotReply/1).
:-dynamic(nameAppears/2).
:-dynamic(mailType/2).
:-dynamic(followedLink/1).
:-dynamic(field/2).
:-dynamic(unreported/0).
:-dynamic(fatigue/1).

% The goalRequirements predicate provides the task break-down for reactive planning.

% This is at the level of receiving the agent-to-agent message
% and registering it as mail
goalRequirements(doMail, [respondToMessage(mail(F,To,S,Te,U,Ty,D,N))]) 
  :- mail(F,To,S,Te,U,Ty,D,N), !.

goalRequirements(respondToMessage(mail(From,To,Subject,Text,Url,Type,DoNotReply,Name)),
	         [executeAddEmail(From,To,Subject,Text,Url,Type,DoNotReply,Name)]).

% This is the agent consciously doing something with each email message
goalRequirements(doMail, [processNextEmail(ID)])
  :- email(ID), mailRead(ID, false), !.

goalRequirements(doMail, [report, doNothing]).

% The 'decide(A)' subgoal picks the action if 'ok(A)' is true, otherwise picks doNothing.
goalRequirements(processNextEmail(ID), 
	         [printMessage('reading ~w ~w from ~w\n', [Type, ID, From]),
		  readEmail(ID), decide(followLink(ID))])
  :- system2Fact(ok(read(ID))), !, mailType(ID,Type), from(ID,From).

% Otherwise, do nothing
goalRequirements(processNextEmail(ID),[]).

subGoal(processNextEmail(_)).
subGoal(respondToMessage(_)).

% Goals need weights so the highest-weight goal can be picked
goal(doMail).
goalWeight(doMail,1) :- started.
goalWeight(waiting,1).

% Writing this in for the demo without graphic
started.

% General version for belief - see if system 1 has already produced a
% belief (positive or negative) that passes threshold and if not, for
% an action, do envisionment. This is coded in system2.pl

fatigue(0.5).

system2Threshold(T) :- fatigue(G), T is 1 - G.  % Need to switch to TLX-style exponential

% Old rule:
% Suspicious of a url that has "www-".
% I need system 2 to combine various pieces of evidence even when it is not doing projections of mental models.
%system2Fact(ok(followLink(ID))) :-
%  url(ID,Url), sub_string(Url, _, _, _, 'www-'), !, format('S2: Odd url: ~w\n', [Url]), fail.


% If system 1 doesn't make a decision about whether an action is ok,
% envision and see if we prefer the plan 
% This should really be in system2.pl, but I left it here to 
system2Fact(ok(Action)) :- incr(envision), preferPlan([Action],[],[]).

% At the bottom of the subgoal tree are 'executable' actions that are
% performed internally or 'primitive' actions that are performed by
% the java 'body'.

% Reading an email just asserts that it is read.
executable(readEmail(_)).
execute(readEmail(ID)) :-
  myRetractall(mailRead(ID,_)), myAssert(mailRead(ID,true)), incr(numberRead).

executable(followLink(_)).
execute(followLink(ID)) :-
  format('Following link on ~w\n', [ID]), myAssert(followedLink(ID)), incr(numberLinksFollowed).

% Add email from a message by asserting predicates for all the fields.

% This version stores email in the agent's prolog space, represented with the
% predicates email(ID), read(ID,Boolean), attachment(ID,A),
% from(ID,P), subject(ID,S), text(ID,T), etc.

executable(executeAddEmail(_,_,_,_,_,_,_,_)).  % Don't crash on old syntax, but do nothing
execute(executeAddEmail(From,To,Subject,Text,Url,Type,DoNotReply,Name))
  :- nextID(ID), myAssert(email(ID)), myAssert(from(ID,From)),
     myAssert(mailRead(ID,false)),
     myAssert(subject(ID,Subject)), myAssert(text(ID,Text)),
     myAssert(url(ID,Url)),
     myAssert(mailType(ID,Type)),
     handleDoNotReply(ID,DoNotReply),
     handleName(ID,Name),
     myRetract(nextID(ID)), NextID is ID + 1,
	myAssert(nextID(NextID)),
     myRetract(mail(From,To,Subject,Text,Url,Type,DoNotReply,Name)).

% Should be one of these
handleDoNotReply(ID,1) :- myAssert(doNotReply(ID)).
handleDoNotReply(ID,0).

handleName(ID,none) :- !.
handleName(ID,Name) :- myAssert(nameAppears(ID,Name)).

%%
%% System 2 domain knowledge
%%

% This hard-coded system 2 rule for following a link models a rule
% that the cognitive agent follows explicitly (as opposed to a system 1 rule).

% If we engage system 2 on a ok(followLink(ID)) belief, check some things out
% about the url
system2Fact(ok(followLink(ID))) :-
  url(ID,Url), hasNumericIP(Url), !, format('S2: numeric IP: ~w\n', [Url]), incr(numeric), fail.

hasNumericIP(Url) :-
  sub_string(Url, Start, _, _, 'http://'), 
  IPStart is Start + 7,
  sub_string(Url, IPEnd, _, _, '/'), IPEnd > IPStart, !, Length is IPEnd - IPStart,
  sub_string(Url, IPStart, Length, _, Sub),
  string_to_list(Sub,L), noAlphaChars(L).

noAlphaChars([]).
noAlphaChars([C|T]) :- (C < 65 ; (C > 90, C < 97) ; C >122), noAlphaChars(T).


% Model used for envisioning. These are based on Wash 10
%mentalModel([hacker(burglar)]). % can be hacker(vandal), hacker(burglar) or hacker(criminal), which means after big fish
mentalModel([virus(mischief)]). % virus can be bad, buggy, mischief or crime.

%% addSets and trigger predicates define how to do forward projection on mental models.
%% The 'utility' predicate defines how to score final projected worlds.

% For now, say it's 50/50 whether we are successfully attacked if we click a link in an email.
% This holds for all current mental models.
addSets(followLink(ID), _, _, [[0.5, followedLink(ID)], [0.5, followedLink(ID), compromised(ID)]]).

% If the hacker is a burglar, he may take ID information
% Will generalize this once I have a handle on it.

% A burglar (or crime-related virus) may steal identity data
trigger(World, hacker(burglar), [World, [stolen(id)|World]], 1) :-
  member(compromised(_), World), !.
trigger(World, virus(crime), [World, [stolen(id)|World]], 1) :-
  member(compromised(_), World), !.

% A vandal (or mischievous virus) may delete files. But (see below)
% backing up makes this not too bad.
trigger(World, hacker(vandal), [World, [deleted(files)|World]], 1) :-
  member(compromised(_), World), not(member(backedup(files),World)), not(member(deleted(files),World)), !.
trigger(World, virus(mischief), [World, [deleted(files)|World]], 1) :-
  member(compromised(_), World), not(member(backedup(files),World)), not(member(deleted(files),World)), !.


trigger(World, _, [World], 0).  % by default, nothing happens
  

% Utility of various worlds under various models. I will assume one model at a time here.
utility(World, -1) :- member(stolen(_),World), !.
utility(World, -2) :- member(deleted(files),World), not(member(backedUp, World)), !.
utility(World, 0.5) :- member(followedLink(_),World), !.
utility(_,0).  % Utility of any world not covered above is 0.


%%
%% System 1 rules and facts
%% 
%%

% Read anything unless asleep (attention <= 0)
if mailType(ID,_) and attention(A) and greater(A,0) then ok(read(ID)) at 1.

% For now, accept all ham in system 1, as a proxy for recognizing the sender
if mailType(ID,ham) then ok(followLink(ID)) at 1.

% By default don't click on a link unless some of the other rules add weight
if url(ID,_) and attention(A) and greater(A,5) then ok(followLink(ID)) at -0.5.

% Also accept mail that seems to be from services I use
if attention(A) and greater(A,3) and useService(Service) and recognizeService(Service, ID) then ok(followLink(ID)) at 0.8.

% The length of the url is a cue (Onarlioglu 11)
if url(ID,Url) and short(Url) and attention(A) and greater(A,4) then ok(followLink(ID)) at 0.4.

% Seeing 'do not reply to this message' is a negative (Jakobsson 08)
if doNotReply(ID) and attention(A) and greater(A,6) then ok(followLink(ID)) at -0.6.

% If there's a name (i.e. it's signed) then that's more likely to be ok (Jakobsson 08)
if nameAppears(ID,_) and attention(A) and greater(A,5) then ok(followLink(ID)) at 0.4.

% If there are other positive words, then increase the positive word score
if goodWord(Word) and hasString(ID, Word) and attention(A) and greater(A,4) then ok(followLink(ID)) at 0.5.

% Some facts enter system1 from observation in the email. This is in general how
% facts enter System1 from observation or inference.
system1Fact(mailType(ID,Type), 1) :-  mailType(ID,Type).
system1Fact(url(ID,Url), 1) :-  url(ID,Url).
system1Fact(useService(S),1) :- useService(S).
system1Fact(recognizeService(S,ID),1) :- hasString(ID,S).
system1Fact(doNotReply(ID),1) :- doNotReply(ID).
system1Fact(nameAppears(ID,Name),1) :- nameAppears(ID,Name).
system1Fact(hasString(ID,String),1) :- hasString(ID,String).
system1Fact(goodWord(Word),1) :- member(Word,['friend','picture','flickr','party']).

% An auxiliary to the rule matching part
system1Fact(short(String),1) :- string_length(String, Length), Length < 40.

% Sort of a meta-fact that controls the attention level, from 0 (no rules will fire)
% to 10 (all rules will fire).
system1Fact(attention(7),1).

% Support for recognition
hasString(ID,String) :- from(ID,From), sub_string(From, _, _, _, String).
hasString(ID,String) :- subject(ID,Subject), sub_string(Subject, _, _, _, String).
hasString(ID,String) :- text(ID,Text), sub_string(Text, _, _, _, String).

% Reporting on state to display system
state(S) :- 
   field(numberRead, R), field(numberLinksFollowed, F), 
   sformat(S, 'Followed ~w of ~w links', [F,R]).

% The other information that will be seen in the UI
uIPredicates([slider(fatigue,1,0,1),mentalModel/1]).  % slider terms are pred, arity, min, max

%%
%% Initial state
%%

% This would be in the bootstrap when there is more than one.
id(10).

myManager(2).

% nextID keeps track of the unique ID number for the next email.
nextID(1).

useService('ebay').
useService('eBay').
useService('wamu').
useService('paypal').

field(numberRead,0).
field(numberLinksFollowed,0).
field(sys1Used, 0).
field(numeric,0).
field(envision,0).
unreported.

% This means the agent chooses between alternate outcomes by which has the higher utility score.
% At the moment there is no alternative.
decisionTheoretic.

% This prints out a summary at the end of going through the emails.
executable(report).
execute(report)
  :- unreported, field(numberRead, NumEmails), NumEmails > 0, !, field(numberLinksFollowed,NumLinks), 
     findall(ID,firedRule(if mailType(ID,ham) then ok(followLink(ID)) at _), R), size(R,S),
     findall(service(Service,N),(useService(Service),findall(ID,firedRule(if useService(Service) and recognizeService(Service, ID) then ok(followLink(ID)) at _), L), size(L,N)),R2),
     format('Read ~w emails and followed ~w links\nHam: ~w, services: ~w\n', [NumEmails, NumLinks, S, R2]),
     field(sys1Used,S1), field(numeric,Numeric), field(envision,Env), system2Threshold(Th),
     format('At threshold ~w: S1 used ~w, S2 num ~w, S2 envision ~w\n', [Th, S1, Numeric, Env]),
     reportSys1Follow,
     % Summarize url lengths up to 50.
     %summarizeUrlLengths(L), format('Url lengths: ~w\n', [L]),
     retractall(unreported).
execute(report).

size([],0).
size([H|T],Size) :- size(T,SmallerSize), Size is SmallerSize + 1.

reportSys1Follow :-
  findall((ID,S),system1Fact(ok(followLink(ID)),S),List), 
  format('system 1 strengths: ~w\n',[List]).

incr(Fieldname) :- field(Fieldname,N), New is N + 1, retractall(field(Fieldname,_)), assert(field(Fieldname,New)).

% Still part of the reporting code
:-dynamic(bucket/2).
summarizeUrlLengths(L) :-
  findall((ID,L), (url(ID,U),string_length(U,L)), List),
  initializeBuckets(190), fillBuckets(List), write('filled'), nl, summarizeBuckets(190, L).

initializeBuckets(-1).
initializeBuckets(N) :- retractall(bucket(N,_)), assert(bucket(N,0)), M is N - 1, initializeBuckets(M).

fillBuckets([]).
fillBuckets([(ID,L)|T]) :- 
  bucket(L,C), !, retract(bucket(L,C)), N is C + 1, assert(bucket(L,N)), fillBuckets(T).
fillBuckets([(ID,L)|T]) :- url(ID,U), fillBuckets(T).

summarizeBuckets(-1,[]).
summarizeBuckets(N,[(N,C)|T]) :- bucket(N,C), C > 0, !, M is N - 1, summarizeBuckets(M,T).
summarizeBuckets(N,T) :- M is N - 1, summarizeBuckets(M,T). % remove zero-count entries

% Don't pay attention to the world for now, except email.
updateBeliefs(_,_).

