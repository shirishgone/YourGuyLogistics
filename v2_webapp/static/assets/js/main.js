(function(){
	'use strict';
	var LoginCntrl = function ($state,AuthService,UserData,$localStorage,vendorClients){
		this.userLogin = function(){
			var data = {
				username : this.username,
				password : this.password
			};
			AuthService.login(data).then(function (response){
				console.log(response.data);
				$localStorage.token = response.data.auth_token;
				vendorClients.$refresh().then(function (response){
					console.log(response);
				});
			});
		};
	};

	angular.module('login', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('login', {
			url : '/login',
			templateUrl : '/static/modules/login/login.html',
			controllerAs : 'login',
			controller: 'LoginCntrl',
			resolve: {
				vendorClients : "vendorClients"
			}
		});
	}])
	.controller('LoginCntrl', [
		'$state', 
		'AuthService',
		'UserData',
		'$localStorage',
		'vendorClients',
		LoginCntrl
	]);
})();
(function(){
	'use strice';
	var AuthService = function ($http,constants){
		return{
			login : function(userdata) {
				return $http.post(constants.v1baseUrl+'auth/login/',userdata);
			}
		};
	};
	
	angular.module('login')
	.factory('AuthService', [
		'$http',
		'constants', 
		AuthService
	]);
})();
(function(){
	'use strict';

	// Declare all the app level modules which depend on the different filters and services
	angular.module('ygVendorApp', [
		'ui.router',
		'ngStorage',
		'ngResource',
		'base64',
		'login'
	])
	.config(['$urlRouterProvider','$locationProvider',function ($urlRouterProvider,$locationProvider) {
		// For any unmatched url, redirect to /login
  		$urlRouterProvider.otherwise("/login");
  		$locationProvider.html5Mode(true).hashPrefix('!');
	}]);

})();
(function(){
	'use strice';

	var userdata = {
		role : '',
		token : ''
	};

	angular.module('ygVendorApp')
	.constant('UserData', userdata);
})();
(function(){
	'use strice';

	var constants = {
		v1baseUrl: '/api/v1/',
		v2baseUrl: '/api/v2/',
		v3baseUrl: '/api/v3/',
	};

	angular.module('ygVendorApp')
	.constant('constants', constants);
})();
(function(){
	'use strict';
	var Vendor = function ($resource,constants){
		return $resource(constants.v1baseUrl+'vendor/:id',{id:"@id"},{
			profile: {
				method: 'GET'
			}
		});
	};
	
	angular.module('ygVendorApp')
	.factory('Vendor', [
		'$resource',
		'constants', 
		Vendor
	]);
})();
(function(){
	'use strict';
	var errorHandler = function ($q,$localStorage,$location){
		var errorHandler = {
			responseError : function(response){
				if (response.status === 401 || response.status === 403) {
					$localStorage.$reset();
					$location.path('/login');
				}
				return $q.reject(response);
			}
		};
		return errorHandler;
	};
	angular.module('ygVendorApp')
	.factory('errorHandler', [
		'$q',
		'$localStorage',
		'$location', 
		errorHandler
	])
	.config(['$httpProvider',function ($httpProvider) {
		$httpProvider.interceptors.push('errorHandler');
	}]);
})();
(function(){
	'use strict';
	var tokenInjector = function ($localStorage){
		var tokenInjector = {
			request : function(config){
				config.headers = config.headers || {};
				if ($localStorage.token) {
					config.headers.Authorization = 'Token ' + $localStorage.token;
				}
				return config;
			}
		};
		return tokenInjector;
	};
	angular.module('ygVendorApp')
	.factory('tokenInjector', [
		'$localStorage',
		tokenInjector 
	])
	.config(['$httpProvider',function ($httpProvider) {
		$httpProvider.interceptors.push('tokenInjector');
	}]);
})();
(function(){
	'use strict';
	var vendorClients = function ($q,Vendor){
		var vendorClients = {};
		var fetchVendors = function() {
			var deferred = $q.defer();
			Vendor.profile(function (response) {
				deferred.resolve(angular.extend(vendorClients, response, {
					data: "vendor",
					$refresh: fetchVendors

					// $hasRole: function(role) {
					// 	return userProfile.roles.indexOf(role) >= 0;
					// },

					// $hasAnyRole: function(roles) {
					// 	return !!userProfile.roles.filter(function(role) {
					// 		return roles.indexOf(role) >= 0;
					// 	}).length;
					// },

					// $isAnonymous: function() {
					// 	return userProfile.anonymous;
					// },

					// $isAuthenticated: function() {
					// 	return !userProfile.anonymous;
					// }

				}));

			});
			return deferred.promise;
		};
		return fetchVendors();
	};

	angular.module('ygVendorApp')
	.factory('vendorClients', [
		'$q',
		'Vendor', 
		vendorClients
	]);
})();
(function(){
	'use strice';

	var role = function ($base64,$localStorageProvider){
		var userrole ;
		return {
			setUserRole: function (){
				var x = $base64.decode($localStorageProvider.get('token'));
				userrole = x;
			},
			$get : function(){
				return {
					userrole: userrole
				};
			}

		};
	};

	angular.module('ygVendorApp')
	.provider('role', [
		'$base64',
		'$localStorageProvider',
		role
	]);
})();