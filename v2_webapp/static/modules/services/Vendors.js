(function(){
	'use strict';
	var Vendor = function ($resource,constants){
		return $resource(constants.v3baseUrl+'vendor/:id/',{id:"@id"},{
			profile: {
				method: 'GET'
			},
			query :{
				method: 'GET',
				isArray: false,
			}
		});
	};
	
	angular.module('ygVendorApp')
	.factory('Vendor', [
		'$resource',
		'constants', 
		Vendor
	]);
})();