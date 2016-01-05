(function(){
	'use strict';
	var Vendor = function ($resource,constants){
		return $resource(constants.v1baseUrl+'vendor/:id',{id:"@id"},{
			profile: {
				method: 'GET'
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