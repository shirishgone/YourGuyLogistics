(function(){
	'use strict';
	angular.module('deliveryguy', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home.dgList', {
			url: "^/deliveryguy/list?date&attendance&search&page",
			templateUrl: "/static/modules/deliveryguy/list/list.html",
			controllerAs : 'dgList',
    		controller: "dgListCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
    						return Access.hasRole(constants.userRole.ADMIN); 
    					}],
    			dgs: ['DeliveryGuy','$stateParams', function (DeliveryGuy,$stateParams){
    						$stateParams.date = ($stateParams.date !== undefined) ? new Date($stateParams.date).toISOString() : new Date().toISOString();
    						$stateParams.attendance = ($stateParams.attendance!== undefined) ? $stateParams.attendance : 'ALL';
    						$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    						return DeliveryGuy.dgPageQuery.query($stateParams).$promise;
    					}],
    		}
		})
		.state('home.dgCreate', {
			url: "^/deliveryguy/create",
			templateUrl: "/static/modules/deliveryguy/create/create.html",
			controllerAs : 'dgCreate',
    		controller: "dgCreateCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
    						return Access.hasRole(constants.userRole.ADMIN); 
    					}],
    		}
		});
		// .state('home.dgDetail', {
		// 	url: "^/deliveryguy/detail",
		// 	templateUrl: "/static/modules/deliveryguy/detail/detail.html",
		// 	controllerAs : 'dgList',
  //   		controller: "dgListCntrl",
		// });
	}]);
})();