(function(){
	'use strict';
	var LoginCntrl = function ($state,AuthService,UserData,$localStorage,role){
		this.userLogin = function(){
			var data = {
				username : this.username,
				password : this.password
			};
			AuthService.login(data).then(function (response){
				console.log(response.data);
				$localStorage.$reset();
				$localStorage.token = response.data.auth_token;
				console.log(role.userrole);
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
			controller: 'LoginCntrl'
		});
	}])
	.controller('LoginCntrl', [
		'$state', 
		'AuthService',
		'UserData',
		'$localStorage',
		'role',
		LoginCntrl
	]);
})();
(function(){
	'use strice';

	angular.module('login')
	.factory('AuthService', ['$http','constants', function ($http,constants){
		return{
			login : function(userdata) {
				return $http.post(constants.v1baseUrl+'auth/login/',userdata);
			}
		};
	}]);
})();
(function(){
	'use strict';

	// Declare all the app level modules which depend on the different filters and services
	angular.module('ygVendorApp', [
		'ui.router',
		'ngStorage',
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
	angular.module('ygVendorApp')
	.factory('errorHandler', ['$q','$localStorage','$location', function ($q,$localStorage,$location){
		var errorHandler = {
			responseError : function(response){
				if (response.status === 401 || response.status === 403) {
					$localStorage.$reset();
					$location.path('/login');
				}
				console.log(response);
				return $q.reject(response);
			}
		};
		return errorHandler;
	}])
	.config(['$httpProvider',function ($httpProvider) {
		$httpProvider.interceptors.push('errorHandler');
	}]);
})();
(function(){
	'use strict';
	angular.module('ygVendorApp')
	.factory('tokenInjector', ['$localStorage', function ($localStorage){
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
	}])
	.config(['$httpProvider',function ($httpProvider) {
		$httpProvider.interceptors.push('tokenInjector');
	}]);
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