(function(){
	'use strict';
	var orderDgAssign = function($mdMedia,$mdDialog,DeliveryGuy){
		return {
			openDgDialog : function(){
				var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'));
				return $mdDialog.show({
					controller         : ('AssignDgCntrl',['$mdDialog','DeliveryGuy',AssignDgCntrl]),
					controllerAs       : 'assignDG',
					templateUrl        : '/static/modules/order/dialogs/assign-dg.html?nd=' + Date.now(),
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
		@AssignDgCntrl controller function for the assign delivery guy dialog
	*/
	function AssignDgCntrl($mdDialog,DeliveryGuy){
		var self = this;
		this.assignment_data = {
			pickup: {
				dg_id: null,
				assignment_type: 'pickup'
			},
			delivery: {
				dg_id: null,
				assignment_type: 'delivery'
			}
		};

		this.cancel = function() {
			$mdDialog.cancel();
		};
		this.answer = function(answer) {
			$mdDialog.hide(answer);
		};
		this.dgSearchTextChange = function(text){
			var search = {
				search : text
			};
			return DeliveryGuy.dgPageQuery.query(search).$promise.then(function (response){
				return response.payload.data.data;
			});
		};
		this.pickupDgChange = function(dg){
			if(dg){
				self.assignment_data.pickup.dg_id = dg.id;
			}
			else{
				self.assignment_data.pickup.dg_id = undefined;
			}
		};
		this.deliveryDgChange = function(dg){
			if(dg){
				self.assignment_data.delivery.dg_id = dg.id;
			}
			else{
				self.assignment_data.delivery.dg_id = undefined;
			}
		};
	}

	angular.module('order')
	.factory('orderDgAssign', [
		'$mdMedia',
		'$mdDialog',
		'DeliveryGuy',
		orderDgAssign
	]);
})();