//info is a JSON object (new Object())
//for communication with server
function requestController(info, commandName)
{
//  alert('in func');

info["command"] = commandName;
var result="";

$.ajax({
	type: "POST",
	url: "RequestController",
	data: info,
	dataType: "json",
	async: false,  
	success:function(data) {
  		result = data; 
	},
	error: function(err) { alert(err.status); }
});

return result;
}

function saveAgent(){
		$("div#AgentNameDialog").dialog("close");

		var info = new Object();
		//alert($("input#agentName").val());
		$("span#newAgentName").text($("input#agentName").val());
		info["agentName"] = $("input#agentName").val();
		//save agent on server in lib/logic
		var result = requestController(info,'SaveCommand');
		//var json = $.parseJSON(result.responseText);
		//var agent_text = json.agent;
		//var prolog_text = json.prolog;
}

function runAgent(){
		var info = new Object();
		var result = requestController(info,'RunCommand');
		var json = $.parseJSON(result.responseText);
		var run_result = json.run_result;
		//show result from run command
}

function createEmptyTree(){
$("#goalstree").jstree({ 
            "json_data" : {
                "data" : [
                    { 
                        "data" : "goals", 
                        "attr" : { "id" : "goalsid", "type":"Root" },
                        "children" : []
                    },
                ]
            },
            "plugins" : [ "themes", "json_data", "ui", "crrm", "contextmenu" ],
	        'contextmenu' : { 'items' : customMenu }
  }).bind("rename.jstree", function (event, data) {
    if(data.rslt.new_name!=data.rslt.old_name){
		renameNode(data.rslt.obj.attr("id"),data.rslt.new_name);
	}
  }).bind("select_node.jstree", function (event, data) {
	    $(this).jstree("rename");
});
}

function newAgent(){
  $("span#newAgentName").text($("NewAgent").val());

  $("#goalstree").jstree({ 
     "json_data": {
     "ajax": {
            "type": "POST",
            "url": "RequestController?command=NewCommand",
            "dataType": "json",
            "success": function (data) { return data.json_tree; }
     }
     },
     "plugins" : [ "themes", "json_data", "ui", "crrm", "contextmenu" ],
     'contextmenu' : { 'items' : customMenu }
  }).bind("rename.jstree", function (event, data) {
	renameNode(data.rslt.obj.attr("id"),data.rslt.new_name);
  }).bind("select_node.jstree", function (event, data) {
    $(this).jstree("rename");
  });
}

function refreshTree(commandName, nodeId){
	//alert("refresh "+commandName);

  $("#goalstree").jstree({ 
     "json_data": {
     "ajax": {
            "type": "POST",
            "url": "RequestController?command="+commandName+"&nodeId="+nodeId,
            "dataType": "json",
            "success": function (data) { return data.json_tree; }
     }
     },
     "crrm":{
        "input_width_limit":2000
     },
     "plugins" : [ "themes", "json_data", "ui", "crrm", "contextmenu" ],
     'contextmenu' : { 'items' : customMenu }
  }).bind("rename.jstree", function (event, data) {
    if(data.rslt.new_name!=data.rslt.old_name)
		renameNode(data.rslt.obj.attr("id"),data.rslt.new_name);
  }).bind("select_node.jstree", function (event, data) {
    $(this).jstree("rename");
  }).bind("loaded.jstree", function (event, data) {
        $(this).jstree("open_all");
  });
}

function addGoal(node){
		var nodeId = $(node).attr("id");
		refreshTree('AddGoalCommand', nodeId)
}


function removeNode(node){
		var nodeId = $(node).attr("id");
		refreshTree('RemoveNodeCommand', nodeId)
}

function makePrimitive(node){
		var nodeId = $(node).attr("id");
		refreshTree('MakePrimitiveCommand', nodeId)
}

function makeExecutable(node){
		var nodeId = $(node).attr("id");
		refreshTree('MakeExecutableCommand', nodeId)
}

function addUpdateRule(node){
		var nodeId = $(node).attr("id");
		refreshTree('AddUpdateRuleCommand', nodeId)
}

function addConstant(node){
		var nodeId = $(node).attr("id");
		refreshTree('AddConstantCommand', nodeId)
}
function addClause(node){
		var nodeId = $(node).attr("id");
		refreshTree('AddClauseCommand', nodeId)
}

function renameNode(id, newName){
	//alert("rename node");

$("#goalstree").jstree({ 
     "json_data": {
     "ajax": {
            "type": "POST",
            "url": "RequestController?command=RenameCommand&nodeId="+id+"&newName="+newName,
            "dataType": "json",
            "success": function (data) { return data.json_tree; }
     }
     },
     "crrm":{
        "input_width_limit":2000
     },
     "plugins" : [ "themes", "json_data", "ui", "crrm", "contextmenu" ],
     'contextmenu' : { 'items' : customMenu }
}).bind("rename.jstree", function (event, data) {
    if(data.rslt.new_name!=data.rslt.old_name)
		renameNode(data.rslt.obj.attr("id"),data.rslt.new_name);
}).bind("select_node.jstree", function (event, data) {
    $(this).jstree("rename");
}).bind("loaded.jstree", function (event, data) {
        $(this).jstree("open_all");
  });
}


function customMenu(node) {
var items = {

                      addGoalItem: { 
                    label: "Add a goal",
                    action: function (node) {  addGoal(node); return; }
                },

                      addClauseItem: { 
                    label: "Add a clause",
                    action: function (node) {  addClause(node); return;  }
                },
                      addConstantItem: { 
                    label: "Add a constant value",
                    action: function (node) {   addConstant(node); return; }
                },
                      makeExeItem: { 
                    label: "Make executable",
                    action: function (node) {   makeExecutable(node); return; }
                },
                
                      makePrimitiveItem: { 
                    label: "Make primitive",
                    action: function (node) {  makePrimitive(node); return; }
                },
                     addRuleItem: { 
                    label: "Add update rule",
                    action: function (node) {   addUpdateRule(node); return; }
                },
                      addMethodItem: { 
                    label: "Add a method",
                    action: function (node) {   addGoal(node); return; }
                },                
                        renameItem: { 
                    label: "Rename node",
                    action: function (node) {   return {renameItem: this.rename(node) }; }
			},
                        deleteItem: { 
                    label: "Remove node",
                    action: function (node) {  removeNode(node); return; }
                }
};
 //alert($(node).attr("id"));
 //alert($(node).attr("type"));

    if ($(node).attr("type")=="Root") {
        delete items.renameItem;
        delete items.addMethodItem;
        delete items.addRuleItem;
        delete items.makePrimitiveItem;
        delete items.makeExeItem;
        delete items.addConstantItem;
        delete items.addClauseItem;
        delete items.deleteItem;
    }
    else if ($(node).attr("type")=="Goal") {
        delete items.addGoalItem;
        if($(node).attr("primitive")=="true") {
        	delete items.makePrimitiveItem;
        }
        else if($(node).attr("primitive")=="false") {
        	delete items.addRuleItem;
        }
        if($(node).attr("executable")=="true") {
        	delete items.makeExeItem;
        }
        delete items.addConstantItem;
        delete items.addClauseItem;
        delete items.renameItem;
    }
    else if ($(node).attr("type")=="GoalLink") {
        delete items.addGoalItem;
        delete items.addMethodItem;
        delete items.addRuleItem;
        delete items.makePrimitiveItem;
        delete items.makeExeItem;
        delete items.addConstantItem;
        delete items.addClauseItem;
        delete items.renameItem;
    }
    else if ($(node).attr("type")=="OtherNode") {
        delete items.addGoalItem;
        delete items.addMethodItem;
        delete items.addRuleItem;
        delete items.makePrimitiveItem;
        delete items.makeExeItem;
        delete items.addConstantItem;
        delete items.addClauseItem;
        delete items.renameItem;
    }
    else if ($(node).attr("type")=="PrologGoal") {
        delete items.addMethodItem;
        delete items.addGoalItem;
        delete items.addRuleItem;
        delete items.makePrimitiveItem;
        delete items.makeExeItem;
        delete items.renameItem;
    }

    return items;

}
