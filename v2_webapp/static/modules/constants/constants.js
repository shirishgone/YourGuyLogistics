(function(){
	'use strice';

	var constants = {
		v1baseUrl: '/api/v1/',
		v2baseUrl: '/api/v2/',
		v3baseUrl: '/api/v3/',
		userRole: {
			ADMIN : 'operations',
			VENDOR : 'vendor'
		}
	};

	var prodConstants = {
		v1baseUrl: 'http://yourguy.herokuapp.com/api/v1/',
		v2baseUrl: 'http://yourguy.herokuapp.com//api/v2/',
		v3baseUrl: 'http://yourguy.herokuapp.com//api/v3/',
		userRole: {
			ADMIN : 'operations',
			VENDOR : 'vendor'
		}
	};
	var testConstants = {
		v1baseUrl: 'https://yourguytestserver.herokuapp.com/api/v1/',
		v2baseUrl: 'https://yourguytestserver.herokuapp.com/api/v2/',
		v3baseUrl: 'https://yourguytestserver.herokuapp.com/api/v3/',
		userRole: {
			ADMIN : 'operations',
			VENDOR : 'vendor'
		}
	};

	angular.module('ygVendorApp')
	.constant('constants', prodConstants);
})();