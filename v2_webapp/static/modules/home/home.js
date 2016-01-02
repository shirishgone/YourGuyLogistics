(function(){
	'use strict';

	angular.module('home', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home',{
			url: "/home",
			templateUrl: "/static/webapp/partials/home.html",
    		controller: "homeCntrl",
		});
	}])
	.controller('homeCntrl', ['', function(){
		
	}]);
})();