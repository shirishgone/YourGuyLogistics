(function(){
	'use strict';
	var orderDgAssign = function($mdMedia,$mdDialog,Notification,$q){
		return {
			openStatusDialog : function(order){
				var deferred = $q.defer();
				var status = {
					pickup: true,
					delivery: true
				};
				if(order){
					if(!order.pickupguy_id){
						Notification.showError('Please assign Pickup guy for the order');
						deferred.reject('no pickup guy');
						return deferred.promise;
					}
					else if(order.pickupguy_id && !order.deliveryguy_id){
						status.delivery = false;
					}
					else if(!order.pickupguy_id && !order.deliveryguy_id){
						Notification.showError('Please assign DG for the order');
						deferred.reject('no dg guy');
						return deferred.promise;
					}
				}
				var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'));
				return $mdDialog.show({
					controller         : ('OrderStatusUpdateCntrl',['$mdDialog','status',OrderStatusUpdateCntrl]),
					controllerAs       : 'statusUpdate',
					templateUrl        : '/static/modules/order/dialogs/status-update.html?nd=' + Date.now(),
					parent             : angular.element(document.body),
					clickOutsideToClose: false,
					fullscreen         : useFullScreen,
					openFrom           : '#options',
					closeTo            : '#options',
					locals             : {
								status : status
					},
				});
			}

		};
	};
	/*
		@OrderStatusUpdateCntrl controller function for the update status for orders dialog
	*/
	function OrderStatusUpdateCntrl($mdDialog,status){
		var self = this;
		self.status = status;
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
		'Notification',
		'$q',
		orderDgAssign
	]);
})();