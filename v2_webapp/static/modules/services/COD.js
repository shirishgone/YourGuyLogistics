(function(){
	'use strict';
	var COD = function($resource,constants){
		return {
			getDeposits : $resource(constants.v3baseUrl+'cod/bank_deposits_list/'),
			verifyDeposits : $resource(constants.v3baseUrl+'cod/verify_bank_deposit/',{},{
				update :{
					method: 'PUT'
				},
			})
		};
	};
	angular.module('ygVendorApp')
	.factory('COD', [
		'$resource',
		'constants', 
		COD
	]);

})();