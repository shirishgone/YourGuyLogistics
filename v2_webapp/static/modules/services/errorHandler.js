(function(){
	'use strict';
	var errorHandler = function ($q,$localStorage,$location){
		var errorHandler = {
			responseError : function(response){
				if (response.status === 401 || response.status === 403) {
					$localStorage.$reset();
					$location.path('/login');
				}
				return $q.reject(response);
			}
		};
		return errorHandler;
	};
	angular.module('ygVendorApp')
	.factory('errorHandler', [
		'$q',
		'$localStorage',
		'$location', 
		errorHandler
	])
	.config(['$httpProvider',function ($httpProvider) {
		$httpProvider.interceptors.push('errorHandler');
	}]);
})();