(function(){
	'use strict';
	angular.module('ygVendorApp')
	.factory('errorHandler', ['$q','$localStorage','$location', function ($q,$localStorage,$location){
		var errorHandler = {
			responseError : function(response){
				if (response.status === 401 || response.status === 403) {
					$localStorage.$reset();
					$location.path('/login');
				}
				console.log(response);
				return $q.reject(response);
			}
		};
		return errorHandler;
	}])
	.config(['$httpProvider',function ($httpProvider) {
		$httpProvider.interceptors.push('errorHandler');
	}]);
})();