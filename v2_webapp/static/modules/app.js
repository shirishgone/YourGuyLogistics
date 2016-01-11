(function(){
	'use strict';

	// Declare all the app level modules which depend on the different filters and services
	angular.module('ygVendorApp', [
		'ngMaterial',
		'ngMessages',
		'ui.router',
		'ngStorage',
		'ngResource',
		'base64',
		'login',
		'home',
		'order',
		'forbidden'
	])
	.config([
		'$urlRouterProvider',
		'$locationProvider',
		'$resourceProvider',
		'$mdThemingProvider',
		'roleProvider',
		function ($urlRouterProvider,$locationProvider,$resourceProvider,$mdThemingProvider,roleProvider) {
		// For any unmatched url, redirect to /home
  		$urlRouterProvider.otherwise("/home");
  		$locationProvider.html5Mode(true).hashPrefix('!');
  		$resourceProvider.defaults.stripTrailingSlashes = false;
  		roleProvider.$get().$setUserRole();
  		$mdThemingProvider.theme('purpleTheme')
  		.primaryPalette('purple')
        .accentPalette('blue')
        .warnPalette('deep-orange');
        $mdThemingProvider.setDefaultTheme('purpleTheme');
	}]);

})();