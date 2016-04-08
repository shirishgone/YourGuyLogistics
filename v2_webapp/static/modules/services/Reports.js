(function(){
	'use strict';
	var Reports = function($resource,constants){
		return {
			getReport : $resource(constants.v3baseUrl+"dashboard_stats/", {} , {
				stats : {
					method: 'GET'
				}
			}),
			reportsExcel : $resource(constants.v3baseUrl+"excel_download/")

		};
	};
	angular.module('ygVendorApp')
	.factory('Reports', [
		'$resource', 
		'constants',
		Reports
	]);
})();