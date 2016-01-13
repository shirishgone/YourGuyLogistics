(function(){
	'use strict';
	var orderSelection = function(){
		var orderselection = {
			selectedItemArray : [],
			toggle : function (item){
				var idx = orderselection.selectedItemArray.indexOf(item);
        		if (idx > -1) orderselection.selectedItemArray.splice(idx, 1);
        		else orderselection.selectedItemArray.push(item);
			},
			exists : function (item) {
        		return orderselection.selectedItemArray.indexOf(item) > -1;

      		},
			addItem : function(item){
				item.selected = true;
				orderselection.selectedItemArray.push(item);
			},
			removeItem : function (item){
				var index = selectedItemArray.indexOf(item);
				if(index > -1) {
					item.selected = false;
					orderselection.selectedItemArray.splice(index,1);
					return true;
				}
				else{
					return false;
				}
			},
			isSelected : function(){
				if(orderselection.selectedItemArray.length > 0){
					return true;
				}
				else {
					return false;
				}
			},
			clearAll : function (){
				orderselection.selectedItemArray = [];
				return orderselection.selectedItemArray;
			},
			slectedItemLength : function (){
				return orderselection.selectedItemArray.length;
			}
		};
		return orderselection;
	};

	angular.module('order')
	.factory('orderSelection', [
		orderSelection
	]);

})();