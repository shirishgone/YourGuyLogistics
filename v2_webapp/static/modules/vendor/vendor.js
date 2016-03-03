(function(){
	'use strict';
	angular.module('vendor', [])
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.vendorList',{
			url: "^/vendor/list?date&search&page",
			templateUrl: "/static/modules/vendor/list/list.html",
			controllerAs : 'vendorList',
    		controller: "vendorListCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER,constants.userRole.ACCOUNTS,constants.userRole.HR];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    			vendors: ['Vendor','$stateParams', function (Vendor,$stateParams){
    						$stateParams.date = ($stateParams.date !== undefined) ? new Date($stateParams.date).toISOString() : new Date().toISOString();
    						$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    						return Vendor.query($stateParams).$promise;
    					}]
    		}
		});
	}]);
})();