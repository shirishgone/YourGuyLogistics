(function(){
	'use strict';
	var COD = function($resource,constants){
		return {
			getDeposits : $resource(constants.v3baseUrl+'cod/bank_deposits_list/'),
			verifyDeposits : $resource(constants.v3baseUrl+'cod/verify_bank_deposit/',{},{
				update :{
					method: 'PUT'
				},
			}),
			getVerifiedDeposits : $resource(constants.v3baseUrl+'cod/verified_bank_deposits_list/'),
			tranferToClient : $resource(constants.v3baseUrl+'cod/transfer_to_client/',{},{
				send :{
					method: 'POST'
				},
			}),
			transactionHistory: $resource(constants.v3baseUrl+'cod/vendor_transaction_history/')
		};
	};
	angular.module('ygVendorApp')
	.factory('COD', [
		'$resource',
		'constants', 
		COD
	]);

})();