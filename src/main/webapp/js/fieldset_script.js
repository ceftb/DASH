function init_fieldset() {
	constructCollapsableFieldsets();
}

///Fieldsets////
	
function constructCollapsableFieldsets() {
	var allFsets = document.getElementsByTagName('fieldset');
	var fset = null;
	for (var i= 0; i<allFsets.length; i++){
		fset = allFsets[i];
		if(fset.getElementsByTagName('div')[0].className == 'hide'){
			fset.getElementsByTagName('div')[0].style.display="none";
		}
		//construct each fieldset with icon +/- and legend text
		constructCollapsableFieldset(fset, 'true');
	}
}

//Creating each fieldset with legend:
function constructCollapsableFieldset(fset, collapsed){
	//+/- ahref:
	var ahrefText = getAHrefForToggle(collapsed);

	//legend:
	var legend = fset.getElementsByTagName('legend')[0];
	if (legend != null){
		legend.innerHTML = ahrefText + legend.innerHTML;
	}else{
		fset.innerHTML = '<legend>' + ahrefText + '</legend>' + fset.innerHTML;
	}
}

function getAHrefForToggle(collapsed){
	var ahrefText = "<a href='#' onclick='toggleFieldset(this.parentNode.parentNode); return false;'>";
	ahrefText = ahrefText + getExpanderItem(collapsed) + "</a>&nbsp;"

	return ahrefText;
}

function toggleFieldset(fset){
	var ahref = fset.getElementsByTagName('a')[0];
	var div = fset.getElementsByTagName('div')[0];
	if (div.style.display != "none"){
		ahref.innerHTML=getExpanderItem('true');
		div.style.display = 'none';
		//hide the entire div
		$("div#runOutputDiv").hide();
		
	}else{
		ahref.innerHTML=getExpanderItem('false');
		div.style.display = 'block';
	}
	return true;
}

function getExpanderItem(collapsed){
	var ecChar;
	if (collapsed =='true')
		ecChar='+';
	else
		ecChar='-';

	return ecChar;
}