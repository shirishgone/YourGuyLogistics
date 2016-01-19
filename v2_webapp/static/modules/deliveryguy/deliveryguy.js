(function(){
	'use strict';
	angular.module('deliveryguy', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home.dgList', {
			url: "^/deliveryguy/list?date&page",
			templateUrl: "/static/modules/deliveryguy/list/list.html",
			controllerAs : 'dgList',
    		controller: "dgListCntrl",
		})
		.state('home.dgCreate', {
			url: "^/deliveryguy/create",
			templateUrl: "/static/modules/deliveryguy/create/create.html",
			controllerAs : 'dgList',
    		controller: "dgListCntrl",
		})
		.state('home.dgDetail', {
			url: "^/deliveryguy/detail",
			templateUrl: "/static/modules/deliveryguy/detail/detail.html",
			controllerAs : 'dgList',
    		controller: "dgListCntrl",
		});
	}]);
})();