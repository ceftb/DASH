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
:-dynamic(storeRegime/2).
:-dynamic(followedLink/1).
:-dynamic(field/2).
:-dynamic(unreported/0).
:-dynamic(system1Fact/2).
:-dynamic(system2Threshold/1).

% This is at the level of receiving the agent-to-agent message
% and registering it as mail
goalRequirements(doWork, [respondToMessage(mail(F,To,S,Te,U,Ty,D,N))]) 
  :- mail(F,To,S,Te,U,Ty,D,N), !.

% This is the agent consciously doing something with each email message
goalRequirements(doWork, [processNextEmail(ID)])
  :- unreadEmail(ID), !.

goalRequirements(doWork, [report, doNothing]).

% Initial version just reads all its email and is done.
goalRequirements(processNextEmail(ID), 
	         [printMessage('reading ~w ~w from ~w\n', [Type, ID, From]),
		  readEmail(ID), decide(followLink(ID))])
  :- believe(ok(read(ID))), !, mailType(ID,Type), from(ID,From).

% Otherwise, do nothing
goalRequirements(processNextEmail(ID),[]).

goalRequirements(decide(Action), [Action])
  :- believe(ok(Action)), !.
goalRequirements(decide(Action), []) :- format('Action ~w not chosen\n', [Action]).

% Regime for making decisions is system1 if user is busy (or currently in system1).
% (Now, system1 is always running, and is used or overridden by system2)
%useRegime(Tasktype,Regime) :- storeRegime(Tasktype, Regime), !.
%useRegime(Tasktype,Regime) :- storeRegime(Tasktype, _), !, fail.
%useRegime(readMail,system1) :-
%  findall([ID], unreadEmail(ID), L), size(L,Size), Size > 5, !, format('using system 1 for email\n'), assert(storeRegime(readMail,system1)).
%useRegime(readMail,system2) :- assert(storeRegime(readMail,system2)), format('using system 2 for email\n'). % true by default, and won't be checked a second time

size([],0).
size([H|T],Size) :- size(T,SmallerSize), Size is SmallerSize + 1.


% General version for belief - see if system 1 has already produced a belief
% (positive or negative) and if not, for an action, do envisionment.
% For strong system 2 we might run system 1 rules anyway.
% Trying -0.1 - 0.1 for strong system 1, and +/-0.5 for strong system 2 (perhaps with random overrides anyway)

system2Threshold(0.5).

believe(Fact) :-
  system1Fact(Fact, Value), system2Threshold(Th), Value > Th, !, incr(sys1Used).
believe(Fact) :-
  system1Fact(Fact, Value), system2Threshold(Th), Value < -Th, !, incr(sys1Used), fail.

% If we engage system 2 on a ok(followLink(ID)) belief, check some things out
% about the url
believe(ok(followLink(ID))) :-
  url(ID,Url), hasNumericIP(Url), !, format('Saw numeric IP: ~w\n', [Url]), incr(numeric), fail.

hasNumericIP(Url) :-
  sub_string(Url, Start, _, _, 'http://'), 
  IPStart is Start + 7,
  sub_string(Url, IPEnd, _, _, '/'), IPEnd > IPStart, !, Length is IPEnd - IPStart,
  sub_string(Url, IPStart, Length, _, Sub),
  string_to_list(Sub,L), noAlphaChars(L).

noAlphaChars([]).
noAlphaChars([C|T]) :- (C < 65 ; (C > 90, C < 97) ; C >122), noAlphaChars(T).

% If sytem 1 doesn't make a decision about whether an action is ok,
% envision and see if we prefer the plan 
believe(ok(Action)) :-
  incr(envision), preferPlan([Action],[],[]).

% Old regime-change approach.

%believeOKToClickLink(ID) :-
%  useRegime(readMail,system1), useServices(Service), recognizeService(Service,ID), !.

%believeOKToClickLink(ID) :-
%  storeRegime(readMail,system1), retract(storeRegime(readMail,system1)), assert(storeRegime(readMail,system2)), format('switched to system 2\n'), fail. % use system2 rules

%believeOKToClickLink(ID) :-
%  useRegime(readMail,system2), format('using system2 rule\n'), !, 
%  retract(storeRegime(readMail,system2)), assert(storeRegime(readMail,system1)),  % go back to system1 next time
%  preferPlan([clickLink(ID)],[],[]).


% 'recognize' a service if the from, subject or text contains a match.
recognizeService([H|T], ID) :- recognizeService1(H, ID).
recognizeService([H|T], ID) :- recognizeService(T,ID).

recognizeService1(Service,ID) :- from(ID,From), sub_string(From, _, _, _, Service).
recognizeService1(Service,ID) :- subject(ID,Subject), sub_string(Subject, _, _, _, Service).
recognizeService1(Service,ID) :- text(ID,Text), sub_string(Text, _, _, _, Service).


% This version stores email within the agent, represented with the
% predicates email(ID), read(ID,Boolean), attachment(ID,A),
% from(ID,P), subject(ID,S), text(ID,T), etc.

unreadEmail(ID)
  :- email(ID), mailRead(ID, false).

goalRequirements(respondToMessage(mail(From,To,Subject,Text,Url,Type,DoNotReply,Name)),
	         [executeAddEmail(From,To,Subject,Text,Url,Type,DoNotReply,Name)]).

% Reading an email just asserts that it is read.
executable(readEmail(_)).
execute(readEmail(ID)) :-
  myRetractall(mailRead(ID,_)), myAssert(mailRead(ID,true)), incr(numberRead).


executable(followLink(_)).
execute(followLink(ID)) :-
  format('Following link on ~w\n', [ID]), myAssert(followedLink(ID)), incr(numberLinksFollowed).

% Add email from a message by asserting predicates for all the fields.
executable(executeAddEmail(_,_,_,_,_,_,_,_)).
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

reportSys1Follow :-
  findall((ID,S),system1Fact(ok(followLink(ID)),S),List), 
  format('system 1 strengths: ~w\n',[List]).

incr(Fieldname) :- field(Fieldname,N), New is N + 1, retractall(field(Fieldname,_)), assert(field(Fieldname,New)).

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

subGoal(processNextEmail(_)).
subGoal(respondToMessage(_)).
subGoal(readEmail(_)).
subGoal(decide(_)).


%% Preferring outcomes - this is not part of the planning code at the moment.
%% Nor does it currently use System 1 to propose operators, outcomes or utilities,
%% but it probably should.

%% Initially just pick one mental model at a time

preferPlan(Plan1, Plan2, Initial) :-
  mentalModel([Model|_]),
  format('comparing ~w and ~w in model ~w\n', [Plan1, Plan2, Model]),
  envisionOutcomes(Plan1, Model, Initial, Outcomes1), 
  envisionOutcomes(Plan2, Model, Initial, Outcomes2), 
  prefer(Outcomes1, Outcomes2).

% The envisioned outcomes are a weighted set of possible outcomes. Each possible outcome
% is a set of fluents that will be true in the world of the outcome and are different from the
% current world.

envisionOutcomes([], _, World, [[1, World]]).  % One outcome from the empty plan, which is the current world.

% Project the first step on the world, and project the rest of the plan on each of the outcomes
envisionOutcomes([Action|RestOfPlan], Model, World, Outcomes) :-
  project(Action,Model,World,NextWorlds), 
  combineProjections(RestOfPlan,Model,NextWorlds,Outcomes).

% How to project an action from a list of sets of adds with weights.
project(Action,Model,World,NextWorlds) :-
  addSets(Action, Model, AddSets), 
  combineAdds(World, AddSets, ActionWorlds),
  triggerWorlds(ActionWorlds, Model, NextWorlds, 1).  % last arg is the max number of steps to model.
% Warning: currently dies for maxSteps > 1.

combineAdds(_, [], []).
combineAdds(World, [[Weight | Adds]|Rest], [[Weight, Next]|RestNext]) :-
  append(World, Adds, Next), combineAdds(World, Rest, RestNext).

% Iterate over the next projected worlds
combineProjections(Plan,_,[],[]).

combineProjections(Plan,Model,[[Weight, World]|T],Outcomes) :-
  envisionOutcomes(Plan,Model,World,FirstUnweightedOutcomes), 
  combineWeights(Weight,FirstUnweightedOutcomes,FirstOutcomes),
  combineProjections(Plan,Model,T,RestOutcomes), 
  append(FirstOutcomes,RestOutcomes,Outcomes).


combineWeights(Weight1, [[Weight2,World]|T], [[Weight,World]|CT]) :- 
  Weight is Weight1 * Weight2, combineWeights(Weight1, T, CT).

combineWeights(_,[],[]).


% Ways to prefer uncertain worlds.

% Decision-theoretic: compute the expected utility of each set of
% possible outcomes, treating the weight as a probability.
prefer(O1, O2) :-
  decisionTheoretic, expectedUtility(O1, U1), expectedUtility(O2, U2), 
  ((U1 > U2, format('Prefer ~w over ~w since ~w > ~w\n', [O1, O2, U1, U2])) ; 
   (format('Prefer ~w over ~w since ~w <= ~w\n', [O2, O1, U1, U2]), fail)).

expectedUtility([],0).
expectedUtility([[Weight,World]|Rest],U) :- 
  utility(World,FirstU), format('Utility of ~w is ~w\n', [World, FirstU]), expectedUtility(Rest,RestU), U is Weight * FirstU + RestU.

%%
%% System 2 domain knowledge
%%

% For now, say it's 50/50 whether we are successfully attacked if we click a link in an email.
% This is to check the mechanics of projection and is independent of the mental model
addSets(followLink(ID), _, [[0.5, followedLink(ID)], [0.5, followedLink(ID), compromised(ID)]]).

% Triggers store beliefs about exogenous acts during projection

% Model n steps forward through triggers, or until the triggers come to a halt
triggerWorlds(Worlds, Model, FinalWorlds, MaxSteps) :- 
  triggerAndCount(Worlds, Model, FinalWorlds, MaxSteps, NewWorldCount),
  format('~w new worlds created in simulation\n', [NewWorldCount]).

% Trigger one step looks for triggers for each world in the set. The fourth
% argument is a count of the number of new worlds created.
triggerAndCount([],_,[],_,0).
triggerAndCount([[Weight,World]|T],Model,Worlds,MaxSteps,NewCount) :-
  triggerNSteps(World,Model,HTrigger,MaxSteps,OneNewCount), 
  triggerAndCount(T,Model,Rest,MaxSteps,RestNewCount),
  distributeWeight(Weight,HTrigger,TriggeredWorlds), 
  append(TriggeredWorlds, Rest, Worlds),
  NewCount is OneNewCount + RestNewCount.

triggerNSteps(World,Model,[World],0,0).  % Stop when there are no more steps

triggerNSteps(World,Model,[World],Steps,0) :- % Also stop when no new world is created
  trigger(World,Model,_,New), New is 0, !.

triggerNSteps(World,Model,TriggerFinal,MaxSteps,FinalCount) :-
  trigger(World,Model,HTrigger,NewCount),
  RemainingSteps is MaxSteps - 1,
  triggerAllNext(Model,HTrigger,TriggerFinal,RemainingSteps,FurtherCount),
  FinalCount is NewCount + FurtherCount.

% Go through the list of all new worlds and look for new new worlds
triggerAllNext(_,[],[],_,0) :- !.
triggerAllNext(Model,[World|Rest],Final,RemainingSteps,NewCount) :-
  triggerNSteps(World,Model,WorldFinal,RemainingSteps,WorldCount),
  triggerAllNext(Model,Rest,RestFinal,RemainingSteps,RestCount),
  append(WorldFinal,RestFinal,Final),
  NewCount is WorldCount + RestCount.
  

distributeWeight(Weight, Worlds, WeightedWorlds) :-
  size(Worlds, Size), NewWeight is Weight / Size, attachWeight(NewWeight,Worlds,WeightedWorlds).

attachWeight(_,[],[]).
attachWeight(Weight,[H|T],[[Weight,H]|R]) :- attachWeight(Weight,T,R).

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
%% ** NOTE: FOR MENTAL MODELS APPROACH, THE MODEL SHOULD AFFECT THE OUTCOMES, NOT UTILITIES
%%    NEED TO RE-WORK
utility(World, -1) :- member(stolen(_),World), !.
utility(World, -1) :- member(deleted(files),World), not(member(backedUp, World)), !.
utility(World, 0.5) :- member(followedLink(_),World), !.
utility(_,0).  % Utility of any world not mentioned above is 0.

%%
%% System 1 rules and facts
%%

% Read anything
if mailType(ID,_) and attention(A) and greater(A,0) then ok(read(ID)) at 1.

%% Following a link
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

% Some facts enter system1 from observation in the email. This is in general how
% facts enter System1 from System2's world.
system1Fact(mailType(ID,Type), 1) :-  mailType(ID,Type).
system1Fact(url(ID,Url), 1) :-  url(ID,Url).
system1Fact(useService(S),1) :- useService(S).
system1Fact(recognizeService(S,ID),1) :- recognizeService1(S,ID).
system1Fact(doNotReply(ID),1) :- doNotReply(ID).
system1Fact(nameAppears(ID,Name),1) :- nameAppears(ID,Name).

% Do this as an auxiliary to the rule matching part
system1Fact(short(String),1) :- string_length(String, Length), Length < 40.

% Sort of a meta-fact that controls the attention level, from 0 (no rules will fire)
% to 10 (all rules will fire).
system1Fact(attention(7),1).

% Reporting on state to display system
state(S) :- 
   field(numberRead, R), field(numberLinksFollowed, F), 
   sformat(S, 'Followed ~w of ~w links', [F,R]).

%%
%% Initial state
%%

% This would be in the bootstrap when there is more than one.
id(10).

myManager(2).

% nextID keeps track of the unique ID number for the next email.
nextID(1).

goal(doWork).
goalWeight(doWork,1) :- started.
goalWeight(waiting,1).

useService('ebay').
useService('eBay').
useService('wamu').
useService('paypal').

% Model used for envisioning. These are based on Wash 10
%mentalModel([hacker(burglar)]). % can be hacker(vandal), hacker(burglar) or hacker(criminal), which means after big fish
mentalModel([virus(mischief)]). % virus can be bad, buggy, mischief or crime.

field(numberRead,0).
field(numberLinksFollowed,0).
field(sys1Used, 0).
field(numeric,0).
field(envision,0).
unreported.

uIPredicates([system2Threshold/1]).

decisionTheoretic.
