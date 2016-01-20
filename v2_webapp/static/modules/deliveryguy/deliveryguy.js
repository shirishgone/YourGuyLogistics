(function(){
	'use strict';
	angular.module('deliveryguy', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home.dgList', {
			url: "^/deliveryguy/list?date&search&page",
			templateUrl: "/static/modules/deliveryguy/list/list.html",
			controllerAs : 'dgList',
    		controller: "dgListCntrl",
    		resolve : {
    			dgs: ['DeliverGuy','$stateParams', function (DeliverGuy,$stateParams){
    						$stateParams.date = ($stateParams.date !== undefined) ? new Date($stateParams.date).toISOString() : new Date().toISOString();
    						$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    						return DeliverGuy.dgPageQuery.query($stateParams).$promise;
    					}],
    		}
		});
		// .state('home.dgCreate', {
		// 	url: "^/deliveryguy/create",
		// 	templateUrl: "/static/modules/deliveryguy/create/create.html",
		// 	controllerAs : 'dgList',
  //   		controller: "dgListCntrl",
		// })
		// .state('home.dgDetail', {
		// 	url: "^/deliveryguy/detail",
		// 	templateUrl: "/static/modules/deliveryguy/detail/detail.html",
		// 	controllerAs : 'dgList',
  //   		controller: "dgListCntrl",
		// });
	}]);
})();