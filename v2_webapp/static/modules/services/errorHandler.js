(function(){
	'use strict';
	var errorHandler = function ($q,$localStorage,$location,$rootScope){
		var errorHandler = {
			responseError : function(response){
				if(response.data.error){
					$rootScope.errorMessage = response.data.error.message;
				}
				var defer = $q.defer();
				if (response.status === 401 || response.status === 403) {
					$localStorage.$reset();
					$location.path('/login');
				}
				else if(response.status === 500){
					$rootScope.errorMessage = 'Something Went Wrong';
				}
				$rootScope.$broadcast('errorOccured');
				defer.reject(response);
				return defer.promise;

			}
		};
		return errorHandler;
	};

	var stateChangeHandler = function ($rootScope, Access, $state,$document,constants){
		$rootScope.$on("$stateChangeError",function (event, toState, toParams, fromState, fromParams, error){
			console.log(error);
			angular.element($document[0].getElementsByClassName('request-loader')).addClass('request-loader-hidden');
			if (error == Access.UNAUTHORIZED) {
				$state.go("login");
			} else if (error == Access.FORBIDDEN) {
				$state.go("forbidden");
			}
		});
		$rootScope.$on("$stateChangeStart",function (event, toState, toParams, fromState, fromParams){
			angular.element($document[0].getElementsByClassName('request-loader')).removeClass('request-loader-hidden');
			if (toState.redirectTo) {
				event.preventDefault();
				$state.go(toState.redirectTo, toParams);
			}
			else if(toState.name === 'home') {
				Access.hasAnyRole([constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER])
				.then(function(response){
					$state.go('home.opsorder');
				},function(error){
					Access.hasRole(constants.userRole.HR)
					.then(function(response){
						$state.go('home.dgList');
					},function(error){
						Access.hasRole(constants.userRole.ACCOUNTS)
						.then(function(response){
							$state.go('home.cod.deposit');
						},function(error){
							Access.hasRole(constants.userRole.VENDOR)
							.then(function(response){
								$state.go('forbidden');
							},function(error){
								$state.go('forbidden');
							});
						});
					});
				});
			}
		});
		$rootScope.$on("$stateChangeSuccess",function (event, toState, toParams, fromState, fromParams){
			if(toState.name != fromState.name){
				$rootScope.previousState = {
					state : fromState.name,
					params : fromParams
				};
			}
			angular.element($document[0].getElementsByClassName('request-loader')).addClass('request-loader-hidden');
		});
	};

	angular.module('ygVendorApp')
	.factory('errorHandler', [
		'$q',
		'$localStorage',
		'$location',
		'$rootScope', 
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
		'constants',
		stateChangeHandler
	]);
})();