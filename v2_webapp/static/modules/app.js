(function(){
	'use strict';

	// Declare all the app level modules which depend on the different filters and services
	angular.module('ygVendorApp', [
		'ui.router',
		'ngStorage',
		'ngResource',
		'base64',
		'login',
		'home'
	])
	.config(['$urlRouterProvider','$locationProvider','roleProvider',function ($urlRouterProvider,$locationProvider,roleProvider) {
		// For any unmatched url, redirect to /login
  		$urlRouterProvider.otherwise("/home");
  		$locationProvider.html5Mode(true).hashPrefix('!');
  		roleProvider.$get().$setUserRole();
	}]);

})();