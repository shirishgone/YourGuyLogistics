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