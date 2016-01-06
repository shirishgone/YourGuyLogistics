(function(){
	'use strict';
	var LoginCntrl = function ($state,AuthService,$localStorage,vendorClients){
		this.userLogin = function(){
			var data = {
				username : this.username,
				password : this.password
			};
			AuthService.login(data).then(function (response){
				$localStorage.token = response.data.auth_token;
				vendorClients.$refresh().then(function (vendor){
					vendor.$updateuserRole();
					$state.go('home');
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
				vendorClients : "vendorClients",
				access : ["Access",function (Access){
					return Access.isAnonymous();
				}]
			}
		});
	}])
	.controller('LoginCntrl', [
		'$state', 
		'AuthService',
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
		userRole: {
			ADMIN : 'operations',
			VENDOR : 'vendor'
		}
	};

	angular.module('ygVendorApp')
	.constant('constants', constants);
})();
(function(){
	'use strict';
	var Access = function($q,vendorClients){
		var Access = {
			OK: 200,
			UNAUTHORIZED: 401,
    		FORBIDDEN: 403,

    		hasRole : function(role){
    			var deferred = $q.defer();
    			vendorClients.then(function (vendorClients){
    				if(vendorClients.$hasRole(role)){
    					deferred.resolve(Access.OK);
    				}
    				else if(vendorClients.$isAnonymous()){
    					deferred.reject(Access.UNAUTHORIZED);
    				}
    				else{
    					deferred.reject(Access.FORBIDDEN);
    				}
    			});
    			return deferred.promise;
    		},
    		isAuthenticated : function(){
    			var deferred = $q.defer();
    			vendorClients.then(function (vendorClients){
    				if(vendorClients.$isAuthenticated()){
    					deferred.resolve(Access.Ok);
    				}
    				else{
    					deferred.reject(Access.UNAUTHORIZED);
    				}
    			});
    			return deferred.promise;
    		},
    		isAnonymous : function(){
    			var deferred = $q.defer();
    			vendorClients.then(function (vendorClients){
    				if(vendorClients.$isAnonymous()){
    					deferred.resolve(Access.OK);
    				}
    				else{
    					deferred.reject(Access.FORBIDDEN);
    				}
    			});
    			return deferred.promise;
    		}
		};
        return Access;
	};

	angular.module('ygVendorApp').
	factory('Access', [
		'$q',
		'vendorClients',
		Access
	]);
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
				var defer = $q.defer();
				if (response.status === 401 || response.status === 403) {
					$localStorage.$reset();
					$location.path('/login');
				}
				defer.reject(response);
				return defer.promise;

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
	'use strice';

	var role = function ($base64,$localStorage){
		var role = {
			userrole : 'anonymous',
			authenticated : false,
			$setUserRole : function(){
				if($localStorage.token){
					var x = $base64.decode($localStorage.token).split(':');
					userrole = x[1];
					authenticated = true;
				}
				else{
					userrole = 'anonymous';
					authenticated = false;
				}
			},
			$getUserRole : function(){
				return {
					userrole : userrole,
					is_authenticated : authenticated
				};
			}
		};
		return role;
	};

	angular.module('ygVendorApp')
	.factory('role', [
		'$base64',
		'$localStorage',
		role
	]);
})();
(function(){
	'use strict';
	var vendorClients = function ($q,role,Vendor){
		var vendorClients = {};
		var fetchVendors = function() {
			var deferred = $q.defer();
			Vendor.profile(function (response) {
				deferred.resolve(angular.extend(vendorClients, response, {
					$refresh: fetchVendors,
					$updateuserRole: function(){
						return role.$setUserRole();
					},

					$hasRole: function(roleValue) {
						return role.$getUserRole().userrole == roleValue;
					},

					$isAuthenticated: function() {
						return role.$getUserRole().is_authenticated;
					},
					$isAnonymous: function() {
						return !role.$getUserRole().is_authenticated;
					}
				}));

			}, function (error){
				deferred.resolve(angular.extend(vendorClients ,{
					$refresh : fetchVendors,
					$updateuserRole: function(){
						return role.$setUserRole();
					},
					$hasRole : function (roleValue){
						return role,$getUserRole().userrole == roleValue;
					},
					$isAuthenticated: function() {
						return role.$getUserRole().is_authenticated;
					},
					$isAnonymous: function() {
						return !role.$getUserRole().is_authenticated;
					}
				}));
			});
			return deferred.promise;
		};
		return fetchVendors();
	};

	angular.module('ygVendorApp')
	.factory('vendorClients', [
		'$q',
		'role',
		'Vendor', 
		vendorClients
	]);
})();