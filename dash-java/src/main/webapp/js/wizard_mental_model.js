
function createEmptyMentalTree(){
$("#mentalmodelstree").jstree({ 
            "json_data" : {
                "data" : [
                    { 
                        "data" : "mental models", 
                        "attr" : { "id" : "mentalid", "type":"Root" },
                        "children" : [{"data" : "trigger", 
                        "attr" : { "id" : "triggerid", "type":"Trigger" },
                        "children" : []},{"data" : "utilities", 
                        "attr" : { "id" : "utilityid", "type":"Utility" },
                        "children" : []}]
                    },
                ]
            },
            "plugins" : [ "themes", "json_data", "ui", "crrm", "contextmenu" ],
	        'contextmenu' : { 'items' : customMenuMental }
  }).bind("rename.jstree", function (event, data) {
    if(data.rslt.new_name!=data.rslt.old_name){
		renameMentalNode(data.rslt.obj.attr("id"),data.rslt.new_name);
	}
  }).bind("select_node.jstree", function (event, data) {
   		var nodeName= data.inst.get_text(data.rslt.obj);
   		if(nodeName!="mental models" && nodeName!="trigger" && nodeName !="utilities")
	    	$(this).jstree("rename");
});
}


function refreshMentalTree(commandName, nodeId){
	//alert("refresh "+commandName);

  $("#mentalmodelstree").jstree({ 
     "json_data": {
     "ajax": {
            "type": "POST",
            "url": "RequestController?command="+commandName+"&nodeId="+nodeId,
            "dataType": "json",
            "success": function (data) { return data.json_mental_tree; }
     }
     },
     "crrm":{
        "input_width_limit":2000
     },
     "plugins" : [ "themes", "json_data", "ui", "crrm", "contextmenu" ],
     'contextmenu' : { 'items' : customMenuMental }
  }).bind("rename.jstree", function (event, data) {
    if(data.rslt.new_name!=data.rslt.old_name)
		renameMentalNode(data.rslt.obj.attr("id"),data.rslt.new_name);
  }).bind("select_node.jstree", function (event, data) {
   		var nodeName= data.inst.get_text(data.rslt.obj);
   		if(nodeName!="mental models" && nodeName!="trigger" && nodeName !="utilities")
	    	$(this).jstree("rename");
  }).bind("loaded.jstree", function (event, data) {
        $(this).jstree("open_all");
  });
}


function addAction(node){
		var nodeId = $(node).attr("id");
		refreshMentalTree('AddActionCommand', nodeId)
}

function addOutcome(node){
		var nodeId = $(node).attr("id");
		refreshMentalTree('AddOutcomeCommand', nodeId)
}

function addModel(node){
		var nodeId = $(node).attr("id");
		refreshMentalTree('AddModelCommand', nodeId)
}

function addOperator(node){
		var nodeId = $(node).attr("id");
		refreshMentalTree('AddOperatorCommand', nodeId)
}

function removeMentalNode(node){
		var nodeId = $(node).attr("id");
		refreshMentalTree('RemoveMentalNodeCommand', nodeId)
}

function renameMentalNode(id, newName){
	//alert("rename node");

$("#mentalmodelstree").jstree({ 
     "json_data": {
     "ajax": {
            "type": "POST",
            "url": "RequestController?command=RenameMentalNodeCommand&nodeId="+id+"&newName="+newName,
            "dataType": "json",
            "success": function (data) { return data.json_mental_tree; }
     }
     },
     "crrm":{
        "input_width_limit":2000
     },
     "plugins" : [ "themes", "json_data", "ui", "crrm", "contextmenu" ],
     'contextmenu' : { 'items' : customMenuMental }
}).bind("rename.jstree", function (event, data) {
    if(data.rslt.new_name!=data.rslt.old_name)
		renameMentalNode(data.rslt.obj.attr("id"),data.rslt.new_name);
}).bind("select_node.jstree", function (event, data) {
   		var nodeName= data.inst.get_text(data.rslt.obj);
   		if(nodeName!="mental models" && nodeName!="trigger" && nodeName !="utilities")
	    	$(this).jstree("rename");
}).bind("loaded.jstree", function (event, data) {
        $(this).jstree("open_all");
  });
}


function customMenuMental(node) {
var items = {

                      addAction: { 
                    label: "Add action",
                    action: function (node) {  addAction(node); return; }
                },

                      addModel: { 
                    label: "Add model",
                    action: function (node) {   addModel(node); return; }
                },
                      addOutcome: { 
                    label: "Add outcome",
                    action: function (node) {   addOutcome(node); return; }
                },
                
                      addOperator: { 
                    label: "Add operator",
                    action: function (node) {  addOperator(node); return; }
                },
                        deleteItem: { 
                    label: "Remove node",
                    action: function (node) {  removeMentalNode(node); return; }
                }
};
 //alert($(node).attr("id"));
 //alert($(node).attr("type"));

    if ($(node).attr("type")=="Root") {
        delete items.addModel;
        delete items.addOperator;
        delete items.deleteItem;
        delete items.addOutcome;
    }
    else if ($(node).attr("type")=="Trigger") {
        delete items.addAction
        delete items.addOutcome;
        delete items.deleteItem;
    }
   else if ($(node).attr("type")=="Action") {
        delete items.addAction
        delete items.addOutcome;
    }
    else if ($(node).attr("type")=="Utility") {
        delete items.addModel;
        delete items.addAction
        delete items.addOperator;
        delete items.deleteItem;
    }
    else if ($(node).attr("type")=="Model") {
        delete items.addModel;
        delete items.addAction
        delete items.addOutcome;
    }
    else if ($(node).attr("type")=="Operator") {
        delete items.addModel;
        delete items.addAction
        delete items.addOperator;
        delete items.addOutcome;
    }
    else if ($(node).attr("type")=="UtilityRule") {
        delete items.addModel;
        delete items.addAction
        delete items.addOperator;
        delete items.addOutcome;
    }

    return items;

}
