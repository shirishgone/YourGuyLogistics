(function(){
	'use strict';
	var orderFilter = function(){
		var orderfilter = {
			filter : {
				date : null,
				vendor : null,
				dg : null,
				cod : false,
				status : [],
				time : null,
				search : null
			},
			setFilter : function (object){
				object.date = orderfilter.date;
				object.vendor = orderfilter.vendor;
				object.dg = orderfilter.dg;
				object.cod = orderfilter.cod;
				object.status = orderfilter.status;
				object.time = orderfilter.time;
				object.search = orderfilter.search;
			},
			getFilter : function (){
				return orderfilter.filter;
			}

		};
		return orderFilter;
	};

	angular.module('order')
	.factory('orderFilter', [
		orderFilter

	]);

})();