%  -*- Mode: Prolog -*-

% Writing a more 'reactive' or goal-based version of the agent
% worker's task, where instead of lists of actions we have a
% determination of the next action based on the agent's beliefs and
% goal. Feedback from the actions taken may change beliefs.

goalRequirements(doWork, [doEvilWork]) :- check(evil), !.
goalRequirements(doWork, [taskFillCell(Spreadsheet, Row, Column])
  :- check(taskFillCell(Spreadsheet, Row, Column)), not reportedStoringToManager(Spreadsheet, Row, Column), !.
goalRequirements(doWork, [doNothing]).  % default, if no spreadsheet work given.


% Normal work for filling a spreadsheet

goalRequirements(taskFillCell(S,R,C), [callPerson(Manager, finished(taskFillCell(S,R,C)))])
  :- check(myManager(Manager)), check(reportedStoring(S,R,C)), !.

goalRequirements(taskFillCell(S,R,C), [reportAgent(taskFillCell(S,R,C))])
  :- check(correctValueStored(S,R,C)), not check(reportedStoring(S,R,C)), !.

goalRequirements(taskFillCell(S,R,C), [toolsForWorkflow_spreadsheetSetValue(Value, R, C)])
  :- check(cellVal(S,R,C,Value)), check(spreadsheetOpen(S)), not check(correctValueStored(S,R,C)), !.

goalRequirements(taskFillCell(S,R,C), [toolsForWorkflow_spreadsheetSwitchSheet(S)])
  :- check(cellVal(S,R,C,_)), check(spreadsheetApp(SpreadsheetApp)), check(appHasFocus(SpreadsheetApp)), 
     not check(spreadsheetOpen(S)), !.

goalRequirements(taskFillCell(S,R,C), [switchTo(SpreadsheetApp)])
  :- check(cellVal(S,R,C,_)), check(spreadsheetApp(SpreadsheetApp)), not check(appHasFocus(SpreadsheetApp)), !.

goalRequirements(taskFillCell(S,R,C), [


% Switching to a general application

goalRequirements(switchTo(App), [computer_applicationSwitch(App)])
  :- check(appOpen(App)), not check(appHasFocus(App)), !.

goalRequirements(switchTo(App), [computer_applicationOpen(App)])
  :- not check(appOpen(App)), !.



% Delegating to other agents (not modeled yet, see comments near 'delegatable' predicate).
goalRequirements(Task, [delegateTask(Task)])
  :- delegatable(Task),
     check(agentState(tiredness, Tiredness)), check(overWorkedThresh(Overworked)), Tiredness > Overworked, !.

% Not changing the evil part yet.
goalRequirements(doEvilWork, [RequirementList])
	:-	findall((Spreadsheet, Size), taskFillSpreadsheet(Spreadsheet, Size, false), Spreadsheets),
		corruptall(Spreadsheets, RequirementList).

corruptall([(Spreadsheet, Size)|T], RequirementList)
	:-	getOffset(Spreadsheet, Offset),
		corrupt(Spreadsheet, Size, Offset, List1),
		corruptall(T, List2),
		append(List1, List2, RequirementList).

corruptall([], []).

corrupt(_, 0, _, []).

corrupt(Spreadsheet, Row, Offset, RequirementList)
	:-	TaskID is Row+Offset,
		check(finishedTask(TaskID)), !,
		NextRow is Row - 1,
		corrupt(Spreadsheet, NextRow, Offset, RequirementList).

corrupt(Spreadsheet, Row, Offset, RequirementList)
	:-	NextRow is Row - 1,
		corrupt(Spreadsheet, NextRow, Offset, List1),
		SRow is Row + Offset,
		append([changeValue(Spreadsheet, SRow, count, 0)], List1, RequirementList).

goalRequirements(changeValue(Spreadsheet, Row, Col, Value), [toolsForWorkflow_spreadsheetSwitchSheet(Spreadsheet),
							     toolsForWorkflow_spreadsheetSetValue(Value, Row, Col),
							     continueChangeValue]).

goalRequirements(continueChangeValue,	[updateAgentState(frustrated, 0.1),
					 updateAgentState(tiredness, continueChangeValue),
					 updateAgentState(unexpectedness, 0.98)])
	:-	succeeded(toolsForWorkflow_spreadsheetSetValue(_)), !.

goalRequirements(continueChangeValue,	[printMessage('Failed to set value\n')]).




% Delegation
% - no delegation yet - the other agent in this case needs to accept or reject the task
% which implies multiple decision cycles, not modeled in the original version.
%delegatable(taskFillCell(_,_,_)).
