(function(){
	'use strict';
	var codTransferCntrl = function($state,$stateParams){
		console.log('transfer');
	};

	angular.module('Cod')
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.cod.transfer',{
			url: "^/cod/transfer",
			templateUrl: "/static/modules/cod/transfer/transfer.html",
			controllerAs : 'transfer',
    		controller: "codTransferCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.ACCOUNTS];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    		}
		});
	}])
	.controller('codTransferCntrl', [
		'$state',
		'$stateParams',
		codTransferCntrl
	]);
})();