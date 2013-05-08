//info is a JSON object (new Object())
function requestController(info, commandName)
{

  alert('in func');

info["command"] = commandName;

var result="";

return $.ajax({
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

//not used
function openAgent(filename){
		alert(filename);
		var info = new Object();
		info["fileName"] = $filename;
		var result = requestController(info,'OpenCommand');
}

function runAgent(){
		//$("div#AgentNameDialog").dialog("close");

		var info = new Object();
		var result = requestController(info,'RunCommand');
		var json = $.parseJSON(result.responseText);
		var run_result = json.run_result;
}

function newAgent(){

		var info = new Object();
		$("span#newAgentName").text($("NewAgent").val());
		var result = requestController(info,'NewCommand');
		//empty tree
		var jsonTree="{\"data\":\"goals\",\"children\":[],\"attr\":{\"type\":\"Goal\",\"primitive\":\"false\"}}";
		var json = $.parseJSON(jsonTree);
		var jsTreeSettings = $("#goalstree").jstree("get_settings");
		jsTreeSettings.json_data.data = json;
		$.jstree._reference("goalstree")._set_settings(jsTreeSettings);
		// Refresh whole tree (-1 means root of tree)
		$.jstree._reference("goalstree").refresh(-1);
}

function addGoal(node){
		var info = new Object();
		var nodeId = $(node).attr("id");
		alert(nodeId);
		info["nodeId"] = nodeId;
		var result = requestController(info,'AddGoalCommand');
		var json = $.parseJSON(result.responseText);
		var jsTreeSettings = $("#goalstree").jstree("get_settings");
		jsTreeSettings.json_data.data = json.json_tree;
		$.jstree._reference("goalstree")._set_settings(jsTreeSettings);
		// Refresh whole tree (-1 means root of tree)
		$.jstree._reference("goalstree").refresh(-1);
}

function removeNode(node){
		var info = new Object();
		var nodeId = $(node).attr("id");
		alert(nodeId);
		info["nodeId"] = nodeId;
		var result = requestController(info,'RemoveNodeCommand');
		var json = $.parseJSON(result.responseText);
		//if I don't clean it the refresh doesn't work properly
		//$("#goalstree").empty();
		var jsTreeSettings = $("#goalstree").jstree("get_settings");
		jsTreeSettings.json_data.data = json.json_tree;
		$.jstree._reference("goalstree")._set_settings(jsTreeSettings);
		// Refresh whole tree (-1 means root of tree)
		$.jstree._reference("goalstree").refresh(-1);
}

function makePrimitive(node){
		var info = new Object();
		var nodeId = $(node).attr("id");
		alert(nodeId);
		info["nodeId"] = nodeId;
		var result = requestController(info,'MakePrimitiveCommand');
		var json = $.parseJSON(result.responseText);
		//if I don't clean it the refresh doesn't work properly
		//$("#goalstree").empty();
		var jsTreeSettings = $("#goalstree").jstree("get_settings");
		jsTreeSettings.json_data.data = json.json_tree;
		$.jstree._reference("goalstree")._set_settings(jsTreeSettings);
		// Refresh whole tree (-1 means root of tree)
		$.jstree._reference("goalstree").refresh(-1);
}

function makeExecutable(node){
		var info = new Object();
		var nodeId = $(node).attr("id");
		alert(nodeId);
		info["nodeId"] = nodeId;
		var result = requestController(info,'MakeExecutableCommand');
		var json = $.parseJSON(result.responseText);
		//if I don't clean it the refresh doesn't work properly
		//$("#goalstree").empty();
		var jsTreeSettings = $("#goalstree").jstree("get_settings");
		jsTreeSettings.json_data.data = json.json_tree;
		$.jstree._reference("goalstree")._set_settings(jsTreeSettings);
		// Refresh whole tree (-1 means root of tree)
		$.jstree._reference("goalstree").refresh(-1);
}

function addUpdateRule(node){
		var info = new Object();
		var nodeId = $(node).attr("id");
		alert(nodeId);
		info["nodeId"] = nodeId;
		var result = requestController(info,'AddUpdateRuleCommand');
		var json = $.parseJSON(result.responseText);
		//if I don't clean it the refresh doesn't work properly
		//$("#goalstree").empty();
		var jsTreeSettings = $("#goalstree").jstree("get_settings");
		jsTreeSettings.json_data.data = json.json_tree;
		$.jstree._reference("goalstree")._set_settings(jsTreeSettings);
		// Refresh whole tree (-1 means root of tree)
		$.jstree._reference("goalstree").refresh(-1);
}

function addConstant(node){
		var info = new Object();
		var nodeId = $(node).attr("id");
		alert(nodeId);
		info["nodeId"] = nodeId;
		var result = requestController(info,'AddConstantCommand');
		var json = $.parseJSON(result.responseText);
		//if I don't clean it the refresh doesn't work properly
		//$("#goalstree").empty();
		var jsTreeSettings = $("#goalstree").jstree("get_settings");
		jsTreeSettings.json_data.data = json.json_tree;
		$.jstree._reference("goalstree")._set_settings(jsTreeSettings);
		// Refresh whole tree (-1 means root of tree)
		$.jstree._reference("goalstree").refresh(-1);
}
function addClause(node){
		var info = new Object();
		var nodeId = $(node).attr("id");
		alert(nodeId);
		info["nodeId"] = nodeId;
		var result = requestController(info,'AddClauseCommand');
		var json = $.parseJSON(result.responseText);
		//if I don't clean it the refresh doesn't work properly
		//$("#goalstree").empty();
		var jsTreeSettings = $("#goalstree").jstree("get_settings");
		jsTreeSettings.json_data.data = json.json_tree;
		$.jstree._reference("goalstree")._set_settings(jsTreeSettings);
		// Refresh whole tree (-1 means root of tree)
		$.jstree._reference("goalstree").refresh(-1);
}

function renameNode(id, newName){
		var info = new Object();
		info["nodeId"] = id;
		info["newName"] = newName;
		var result = requestController(info,'RenameCommand');
		var json = $.parseJSON(result.responseText);
		//if I don't clean it the refresh doesn't work properly
		//$("#goalstree").empty();
		var jsTreeSettings = $("#goalstree").jstree("get_settings");
		jsTreeSettings.json_data.data = json.json_tree;
		$.jstree._reference("goalstree")._set_settings(jsTreeSettings);
		// Refresh whole tree (-1 means root of tree)
		$.jstree._reference("goalstree").refresh(-1);
}

function testF(){
  //alert('test');
}


function customMenu(node) {
  //alert('bubu');
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
    }
    else if ($(node).attr("type")=="GoalLink" || $(node).attr("type")=="OtherType") {
        delete items.addGoalItem;
        delete items.addMethodItem;
        delete items.addRuleItem;
        delete items.makePrimitiveItem;
        delete items.makeExeItem;
        delete items.addConstantItem;
        delete items.addClauseItem;
    }
    else if ($(node).attr("type")=="PrologGoal") {
        delete items.addMethodItem;
        delete items.addGoalItem;
        delete items.addRuleItem;
        delete items.makePrimitiveItem;
        delete items.makeExeItem;
    }

    return items;

}
