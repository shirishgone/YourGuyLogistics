(function(){
	'use strict';
	var DeliverGuy = function ($resource,constants){
		return {
			dgListQuery : $resource(constants.v1baseUrl+'deliveryguy/:id',{id:"@id"},{
				query :{
					method: 'GET',
					isArray: true
				}
			}),
			dgPageQuery : $resource(constants.v3baseUrl+'deliveryguy/:id/',{id:"@id"},{
				query :{
					method: 'GET',
					isArray: false
				}
			})
		};
	};
	
	angular.module('ygVendorApp')
	.factory('DeliveryGuy', [
		'$resource',
		'constants', 
		DeliverGuy
	]);
})();