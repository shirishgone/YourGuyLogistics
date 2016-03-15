(function(){
	'use strict';
	var codHistoryCntrl = function($state,$stateParams){
		console.log('history');
	};

	angular.module('Cod')
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.cod.history',{
			url: "^/cod/history",
			templateUrl: "/static/modules/cod/history/history.html",
			controllerAs : 'history',
    		controller: "codHistoryCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.ACCOUNTS];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    		}
		});
	}])
	.controller('codHistoryCntrl', [
		'$state',
		'$stateParams',
		codHistoryCntrl
	]);
})();