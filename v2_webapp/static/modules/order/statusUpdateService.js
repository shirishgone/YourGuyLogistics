(function(){
	'use strict';
	var orderDgAssign = function($mdMedia,$mdDialog){
		return {
			openStatusDialog : function(){
				var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'));
				return $mdDialog.show({
					controller         : ('OrderStatusUpdateCntrl',['$mdDialog',OrderStatusUpdateCntrl]),
					controllerAs       : 'statusUpdate',
					templateUrl        : '/static/modules/order/dialogs/status-update.html?nd=' + Date.now(),
					parent             : angular.element(document.body),
					clickOutsideToClose: false,
					fullscreen         : useFullScreen,
					openFrom           : '#options',
					closeTo            : '#options',
				});
			}

		};
	};
	/*
		@OrderStatusUpdateCntrl controller function for the update status for orders dialog
	*/
	function OrderStatusUpdateCntrl($mdDialog){
		var self = this;
		this.status_object = {
			data : {}
		};

		this.cancel = function() {
			$mdDialog.cancel();
		};
		this.answer = function(answer){
			$mdDialog.hide(answer);
		};
	}

	angular.module('order')
	.factory('OrderStatusUpdate', [
		'$mdMedia',
		'$mdDialog',
		orderDgAssign
	]);
})();