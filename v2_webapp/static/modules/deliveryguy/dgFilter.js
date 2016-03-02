(function(){
	'use strict';
	/*
		filter to convert a time string to specific format for displaying it in dropdown. 
		For eg: 09:00:00 with beconverted to a format to 09:00 AM, 
		which can be shown in dropdowns or any place for ease of user.
	*/
	var timeAsDate = function($filter){
		return function(input){
			if(input) {
				var time = input.split(':');
				return moment().hour(time[0]).minute(time[1]).format('hh:mm A');
			}
			else {
				return false;
			}
			
		};
	};
	angular.module('deliveryguy')
	.filter('timeAsDate',[
		'$filter',
		timeAsDate
	]);
})();