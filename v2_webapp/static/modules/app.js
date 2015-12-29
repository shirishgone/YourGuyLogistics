(function(){
	'use strict';

	// Declare all the app level modules which depend on the different filters and services
	angular.module('ygVendorApp', [
		'ui.router'
	])
	.config(['$urlRouterProvider','$locationProvider',function ($urlRouterProvider,$locationProvider) {
		// For any unmatched url, redirect to /login
  		$urlRouterProvider.otherwise("/login");
  		$locationProvider.html5Mode(true).hashPrefix('!');
	}]);

})();