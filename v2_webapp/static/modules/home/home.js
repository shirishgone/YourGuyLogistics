(function(){
	'use strict';
	var homeCntrl = function($state,constants,vendorClients){
		console.log(vendorClients.$hasRole(constants.userRole.VENDOR));
		// if(vendorClients.$hasRole(constants.userRole.ADMIN)){

		// }
	};

	angular.module('home', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home',{
			url: "/home",
			// abstract: true,
			templateUrl: "/static/modules/home/home.html",
			controllerAs : 'home',
    		controller: "homeCntrl",
    		resolve: {
    			vendorClients : 'vendorClients',
    			access: ["Access",function (Access){ 
    				return Access.isAuthenticated(); 
    			}]
    		}
		});
	}])
	.controller('homeCntrl', [
		'$state', 
		'constants',
		'vendorClients',
		homeCntrl
	]);
})();