(function(){
	'use strict';
	var orderDetailCntrl = function($state,$stateParams,order,DeliveryGuy,orderDgAssign,OrderStatusUpdate,PreviousState){
		var self = this;
		self.order = order.payload.data;
		/*
			function to redirect back to the previous page or parent page.
		*/
		self.goBack = function(){
			if(PreviousState.isAvailable()){
				PreviousState.redirectToPrevious();
			}
			else{
				$state.go('home.opsorder');
			}
		};
	};

	angular.module('order')
	.controller('orderDetailCntrl', [
		'$state',
		'$stateParams',
		'order',
		'DeliveryGuy',
		'orderDgAssign',
		'OrderStatusUpdate',
		'PreviousState',
		orderDetailCntrl
	]);

})();