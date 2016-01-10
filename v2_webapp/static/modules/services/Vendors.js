(function(){
	'use strict';
	var Vendor = function ($resource,constants){
		return $resource(constants.v1baseUrl+'vendor/:id',{id:"@id"},{
			profile: {
				method: 'GET'
			},
			query :{
				method: 'GET',
				isArray: false,
				transformResponse: function(data){
					var response = angular.fromJson(data);
					if(angular.isArray(response)){
						var object = {};
						object.store_name = 'Operations';
						object.vendors = response;
						return object;
					}
					else{
						return response;
					}
				}
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