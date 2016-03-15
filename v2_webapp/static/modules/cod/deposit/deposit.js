(function(){
	'use strict';
	var codDepositCntrl = function($state,$stateParams,deposits){
		console.log(deposits);
		var self = this;
		self.deposits = deposits.payload.data;
	};

	angular.module('Cod')
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.cod.deposit',{
			url: "^/cod/deposits",
			templateUrl: "/static/modules/cod/deposit/deposit.html",
			controllerAs : 'deposit',
    		controller: "codDepositCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
					var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.ACCOUNTS];
					return Access.hasAnyRole(allowed_user); 
    			}],
    			deposits : ['COD',function(COD){
    				return COD.getDeposits.get().$promise;
    			}],
    		}
		});
	}])
	.controller('codDepositCntrl', [
		'$state',
		'$stateParams',
		'deposits',
		codDepositCntrl
	]);
})();