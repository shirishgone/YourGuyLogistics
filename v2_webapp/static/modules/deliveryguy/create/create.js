(function(){
	'use strict';
	var dgCreateCntrl = function ($mdSidenav,$stateParams,dgConstants){
		console.log(dgConstants);
		var self = this;
		self.shift_timings = dgConstants.shift_timings;
		self.transportation_mode = dgConstants.transportation_mode;
	};

	angular.module('deliveryguy')
	.controller('dgCreateCntrl', [
		'$mdSidenav', 
		'$stateParams',
		'dgConstants',
		dgCreateCntrl
	]);
})();