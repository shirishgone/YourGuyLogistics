(function(){
	'use strict';
	var Profile = function ($resource,constants){
		return $resource(constants.v3baseUrl+'profile/',{},{
			profile: {
				method: 'GET',
				transformResponse: function(data,headers){
					var response = angular.fromJson(data);
					if(response.payload){
						response.payload.data.is_authenticated = response.success;
						return response.payload.data;
					}
					else{
						return response;
					}
				}
			}
		});
	};
	
	angular.module('ygVendorApp')
	.factory('Profile', [
		'$resource',
		'constants', 
		Profile
	]);
})();