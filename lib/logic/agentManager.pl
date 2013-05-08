% -*- Mode: Prolog -*-

%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%--------------------------LIST OF GOAL REQUIREMENTS----------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%

goalRequirements(initialize, [getOnComputer(ID)])
	:-compID(ID).

% Goal = Do Work 
goalRequirements(doWork, [doNothing])
	:- checkPCChance(CPC),
	   delegateTaskChance(DTC),
	   Sum is CPC + DTC, 
	   Sum == 0 , 
	   !.

% Goal = Do Work 
goalRequirements(doWork, [checkPC(Error)])
	:- N is random(100)/100,
	   checkPCChance(CPC),
	   N < CPC,
	   !,
	   print('Check the PC for an Error'),
	   error(Error).

goalRequirements(doWork, [delegateTasks])
	:- remainingSubTasks(RST),
	   tasks(MTQ),
	   MTQ > 0,
	   RST = 0,
	   !.

goalRequirements(doWork, [doNothing]).

% Needs to be rewritten
goalRequirements(respondToMessage(Message), [])
	:- %spreadSheetSize(Size),
  	   swritef(M, 'MessageReceived %s', [Message]),
	   print(M),
	   % Test this out
   	   string_length('(TaskFillSpreadsheet', Length),
           sub_string(M, 0, Length, _, '(TaskFillSpreadsheet'),
	   !,
	   %Assert Message that there is a spreadSheet to be filled
	   addJobToStack.

	   
goalRequirements(respondToMessage(finishedTask(_)), [])
	:- spreadSheetSize(_),
	   !,
	   remainingSubTasks(RST),
	   RST = RST-1.

goalRequirements(respondToMessage(M), [])
	:- format('Unrecognized message: ~w \n', [M]).
	  
           
goalRequirements(delegateTasks, ReqList)
	:- % Remove Remaining Sub Tasks
	   findall((Name) ,taskFillSpreadsheet(Name, _, _), List),
	   delegateSpreadsheets(List, ReqList).

% Note - the other spreadsheets should presumably make the list.
delegateSpreadsheets([SpreadSheetName|_], [callPerson(WorkerID, taskFillCell(SpreadSheetName, CurrentTaskToAssign, count))])
	:- currentWorker(WorkerID),
           taskFillSpreadsheet(SpreadSheetName, _, CurrentTaskToAssign).
	   
delegateSpreadsheets([], []).


%---------------
%  Effects, in terms of updated beliefs
%---------------

% Currently doesn't bother to check whether the call succeeded.
updateBeliefs(callPerson(Agent,taskFillCell(SpreadSheet, Task, _)), ReturnValue)
  :- % Cycle agent, reduce tasks to perform and current task to assign
     nextWorker(Agent,Next),
     myRetract(currentWorker(Agent)),
     myAssert(currentWorker(Next)),
     tasks(T),
     NewT is T - 1,
     myRetract(tasks(T)),
     myAssert(tasks(NewT)),
     taskFillSpreadsheet(SpreadSheet, Size, Task),
     myRetract(taskFillSpreadsheet(SpreadSheet, Size, Task)),
     NewTask is Task - 1,
     myAssert(taskFillSpreadsheet(SpreadSheet, Size, NewTask)),
%     format('Asserted new worker ~w , current task ~w , tasks left ~w , sheet ~w \n', 
%	[Next, NewTask, NewT, SpreadSheet]),
     !.

nextWorker(Agent,1) :- workers(Agent), !.
nextWorker(Agent,Next) :- Next is Agent + 1.

updateBeliefs(_,_).
	    
	   
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%-----------------------------LIST OF Executables-------------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%

executable(updateAgentState(_, _)).
execute(updateAgentState(_, _)).

executable(reportAgentState).
execute(reportAgentState)
	:- tiredness(Tiredness), 
	   format('And I am now tired at level ~w\n', [Tiredness]), 
	   unexpectedness(Unexpectedness),
	   format('Unexpectedness was ~w\n', [Unexpectedness]).

%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%------------------------------LIST OF Subgoals---------------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%

subGoal(doOrdinaryWork).
subGoal(checkPC(_)).
subGoal(delegateTasks).
subGoal(delegateSpreadsheets(_)).
subGoal(openBrowser).
subGoal(respondToError(_, _)).

:-dynamic(checkPCChance/1).
:-dynamic(delegateTaskChance/1).
:-dynamic(remainingSubTasks/1).
:-dynamic(tasks/1).
:-dynamic(spreadSheetSize/1).
:-dynamic(taskFillSpreadsheet/3).
:-dynamic(currentWorker/1).
