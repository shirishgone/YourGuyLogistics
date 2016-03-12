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
		'deliveryguy',
    'vendor',
    'reports',
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
  		$mdThemingProvider.definePalette('ygBlue', {
  			'50'  : 'EEFDFD',
  			'100' : 'E9F5F5',
  			'200' : 'C8EEF8',
  			'300' : '89DAF1',
  			'400' : '6DD2ED',
  			'500' : '52C9EA',
  			'600' : '37C0E7',
  			'700' : '1CB8E3',
  			'800' : '18A2CB',
  			'900' : '158CAD',
  			'A100': 'C4EEF9',
  			'A200': '78D7EF',
  			'A400': '1FC0E7',
  			'A700': '31AEF7',
		    'contrastDefaultColor': 'light',    // whether, by default, text (contrast)
		                                        // on this palette should be dark or light
		    'contrastDarkColors': ['50', '100', //hues which contrast should be 'dark' by default
		    '200', '300', '400', 'A100'],
		    'contrastLightColors': undefined    // could also specify this if default was 'dark'
		});
		$mdThemingProvider.definePalette('ygOrange', {
  			'50'  : 'FFF9F1',
  			'100' : 'FF7CEC',
  			'200' : 'FFEED6',
  			'300' : 'FDD9A6',
  			'400' : 'FDCD88',
  			'500' : 'FCC06A',
  			'600' : 'FBB34C',
  			'700' : 'FBA72E',
  			'800' : 'FA9A10',
  			'900' : 'E78A05',
  			'A100': 'FFF6CF',
  			'A200': 'FFF0C7',
  			'A400': 'FDD393',
  			'A700': 'FBB134',
		    'contrastDefaultColor': 'dark',    // whether, by default, text (contrast)
		                                        // on this palette should be dark or light
		    'contrastDarkColors': ['50', '100', //hues which contrast should be 'dark' by default
		    '200', '300', '400', 'A100'],
		    'contrastLightColors': undefined    // could also specify this if default was 'dark'
		});
  		$mdThemingProvider.theme('ygBlueTheme')
  		.primaryPalette('ygBlue' , {
  			'default' : '700',
        'hue-1': '100', // use shade 100 for the <code>md-hue-1</code> class
        'hue-2': '600', // use shade 600 for the <code>md-hue-2</code> class
        'hue-3': 'A100'
  		})
      .accentPalette('ygOrange',{
        'default' : '500'
      })
      .warnPalette('red');
      $mdThemingProvider.setDefaultTheme('ygBlueTheme');
	}]);

})();