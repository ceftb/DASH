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
		//this is parsed json
  		result = data; 
	},
	error: function (request, status, error) {
		alert("error "+status + "  " + error);
        alert(request.responseText);
    }
	
});

//this is parsed json
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
		var addNL = result.run_result.replace(/@@@/g, "\n");
		//show result from run command
		//$("span#runOutputSpan").text(addNL);
		$("textarea#runText").text(addNL);
		$("div#runOutputDiv").show();
		
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
   		var nodeName= data.inst.get_text(data.rslt.obj);
   		if(nodeName!="goals")
	    	$(this).jstree("rename");
  });

  $("#mentalmodelstree").jstree({ 
     "json_data": {
     "ajax": {
            "type": "POST",
            "url": "RequestController?command=NewMentalCommand",
            "dataType": "json",
            "success": function (data) { return data.json_mental_tree; }
     }
     },
     "plugins" : [ "themes", "json_data", "ui", "crrm", "contextmenu" ],
     'contextmenu' : { 'items' : customMenuMental }
  }).bind("rename.jstree", function (event, data) {
	renameMentalNode(data.rslt.obj.attr("id"),data.rslt.new_name);
  }).bind("select_node.jstree", function (event, data) {
   		var nodeName= data.inst.get_text(data.rslt.obj);
   		if(nodeName!="mental models" && nodeName!="trigger" && nodeName !="utilities")
	    	$(this).jstree("rename");
  });
}

