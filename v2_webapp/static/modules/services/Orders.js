(function(){
	'use strict';
	var Order = function ($resource,constants){
		return {
			getOrders : $resource(constants.v3baseUrl+'order/:id/',{id:"@id"},{
				query :{
					method: 'GET',
					isArray: false
				}
			}),
			assignOrders : $resource(constants.v3baseUrl+'order/assign_orders/', {}, {
				assign : {
					method: 'PUT',
				}
			}),
			updatePickup : $resource(constants.v3baseUrl+'order/:id/picked_up/',{id:"@id"},{
				update : {
					method: 'PUT'
				}
			}),
			updateDelivered : $resource(constants.v3baseUrl+'order/:id/delivered/',{id:"@id"},{
				update : {
					method: 'PUT'
				}
			}),
			updatePickupAttempted : $resource(constants.v3baseUrl+'order/:id/pickup_attempted/',{id:"@id"},{
				update : {
					method: 'PUT'
				}
			}),
			updateDeliveryAttempted : $resource(constants.v3baseUrl+'order/:id/delivery_attempted/',{id:"@id"},{
				update : {
					method: 'PUT'
				}
			}),
			editCODAmount : $resource(constants.v3baseUrl+'order/:id/update_cod/',{id:"@id"},{
				update : {
					method: 'PUT'
				}
			})
		};
	};
	
	angular.module('ygVendorApp')
	.factory('Order', [
		'$resource',
		'constants', 
		Order
	]);
})();