(function(){
	'use strict';
	var Reports = function($resource,constants){
		return {
			getReport : $resource(constants.v3baseUrl+"dashboard_stats/", {} , {
				stats : {
					method: 'GET'
				}
			})
		};
	};
	angular.module('ygVendorApp')
	.factory('Reports', [
		'$resource', 
		'constants',
		Reports
	]);
})();