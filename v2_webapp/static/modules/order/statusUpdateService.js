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
		this.pickup = {
			isPickup: true,
			data : {
				pickup_attempted : false,
				delivery_remarks : null
			}
		};
		this.delivery = {
			isPickup: false ,
			data : {
				delivered_at : null,
				delivery_attempted : false,
				delivery_remarks: null,
				cod_collected_amount: null
			}
		};

		this.cancel = function() {
			$mdDialog.cancel();
		};
		this.updatePickupAttempted = function(answer){
			answer.data.pickup_attempted = true;
			$mdDialog.hide(answer);
		};
		this.updatePickup = function(answer){
			answer.data.pickup_attempted = false;
			$mdDialog.hide(answer);
		};
		this.updateDeliveryAttempted = function(answer){
			answer.data.delivery_attempted = true;
			$mdDialog.hide(answer);
		};
		this.updateDelivery = function(answer){
			answer.data.delivery_attempted = false;
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