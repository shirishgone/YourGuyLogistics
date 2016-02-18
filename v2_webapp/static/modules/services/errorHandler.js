(function(){
	'use strict';
	var errorHandler = function ($q,$localStorage,$location){
		var errorHandler = {
			responseError : function(response){
				var defer = $q.defer();
				if (response.status === 401 || response.status === 403) {
					$localStorage.$reset();
					$location.path('/login');
				}
				defer.reject(response);
				return defer.promise;

			}
		};
		return errorHandler;
	};

	var stateChangeHandler = function ($rootScope, Access, $state,$document){
		$rootScope.$on("$stateChangeError",function (event, toState, toParams, fromState, fromParams, error){
			angular.element($document[0].getElementsByClassName('request-loader')).addClass('request-loader-hidden');
			if (error == Access.UNAUTHORIZED) {
				$state.go("login");
			} else if (error == Access.FORBIDDEN) {
				$state.go("forbidden");
			}
		});
		$rootScope.$on("$stateChangeStart",function (event, toState, toParams, fromState, fromParams){
			angular.element($document[0].getElementsByClassName('request-loader')).removeClass('request-loader-hidden');
		});
		$rootScope.$on("$stateChangeSuccess",function (event, toState, toParams, fromState, fromParams){
			$rootScope.previousState = {
				state : fromState.name,
				params : fromParams
			};
			console.log($rootScope.previousState);
			angular.element($document[0].getElementsByClassName('request-loader')).addClass('request-loader-hidden');
		});
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
	}])
	.run([
		'$rootScope',
		'Access',
		'$state',
		'$document',
		stateChangeHandler
	]);
})();