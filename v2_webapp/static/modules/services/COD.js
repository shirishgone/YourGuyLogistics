(function(){
	'use strict';
	var COD = function($resource,constants){
		return {
			getDeposits : $resource(constants.v3baseUrl+'cod/bank_deposits_list/')
		};
	};
	angular.module('ygVendorApp')
	.factory('COD', [
		'$resource',
		'constants', 
		COD
	]);

})();