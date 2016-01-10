(function(){
	'use strict';
	var LoginCntrl = function ($state,AuthService,$localStorage,vendorClients){
		this.loader = false;
		this.userLogin = function(){
			this.loader = true;
			var self = this;
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
			},function (error){
				self.loader = false;
				self.error_message = error.data.non_field_errors[0];
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
	var homeCntrl = function($state,$mdSidenav,$mdDialog,constants,vendorClients){
		// Redirect to admin or vendor page accorfing to the credentials.
		if(vendorClients.$hasRole(constants.userRole.ADMIN)){
			this.admin = true;
			$state.go('home.opsorder');
		}
		else if(vendorClients.$hasRole(constants.userRole.VENDOR)){
			this.vendor = true;
			$state.go('home.order');
		}
		// Controller logic for common items between vendor and admin.
		var self = this;
		this.store_name = vendorClients.store_name;
		var confirm = $mdDialog.confirm()
		.parent(angular.element(document.querySelector('#body')))
		.clickOutsideToClose(false)
		.title('Are you sure you want to Sign Out?')
		.textContent('After this you will be redirected to login page.')
		.ariaLabel('Sign Out')
		.targetEvent()
		.ok('Sign Out!')
		.cancel('Not Now')
		.openFrom('#logout-button')
		.closeTo('#logout-button');
		this.toggleSideNav = function(){
			$mdSidenav('left').toggle();
		};
		this.logout = function(){
			vendorClients.$clearUserRole();
			vendorClients.$refresh().then(function (vendor){
				$state.go('login');
			});
		};
		this.showLogoutDialog = function(){
			$mdDialog.show(confirm).then(function(){
				self.logout();
			});
		};
	};

	angular.module('home', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home',{
			url: "/home",
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
		'$mdSidenav',
		'$mdDialog',
		'constants',
		'vendorClients',
		homeCntrl
	]);
})();
(function(){
	'use strict';
	var forbiddenCntrl = function($state,constants,vendorClients){

	};

	angular.module('forbidden', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('forbidden',{
			url: "/forbidden",
			templateUrl: "/static/modules/forbidden/forbidden.html",
			controllerAs : 'forbidden',
    		controller: "forbiddenCntrl",
		});
	}])
	.controller('forbiddenCntrl', [
		'$state', 
		forbiddenCntrl
	]);
})();
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
		'$mdThemingProvider',
		'roleProvider',
		function ($urlRouterProvider,$locationProvider,$mdThemingProvider,roleProvider) {
		// For any unmatched url, redirect to /home
  		$urlRouterProvider.otherwise("/home");
  		$locationProvider.html5Mode(true).hashPrefix('!');
  		roleProvider.$get().$setUserRole();
  		$mdThemingProvider.theme('purpleTheme')
  		.primaryPalette('purple')
        .accentPalette('blue')
        .warnPalette('deep-orange');
        $mdThemingProvider.setDefaultTheme('purpleTheme');
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
	var Order = function ($resource,constants){
		return {
			getOrders : $resource(constants.v2baseUrl+'order/:id/',{id:"@id"},{
				query :{
					method: 'GET',
					isArray: false
				}
			})
		};
	};
	
	angular.module('ygVendorApp')
	.factory('Order', [
		'$resource',
		'constants', 
		Order
	]);
})();
(function(){
	'use strict';
	var Vendor = function ($resource,constants){
		return $resource(constants.v1baseUrl+'vendor/:id',{id:"@id"},{
			profile: {
				method: 'GET'
			},
			query :{
				method: 'GET',
				isArray: false,
				transformResponse: function(data){
					var response = angular.fromJson(data);
					if(angular.isArray(response)){
						var object = {};
						object.store_name = 'Operations';
						object.vendors = response;
						return object;
					}
					else{
						return response;
					}
				}
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

	var stateChangeError = function ($rootScope, Access, $state){
		$rootScope.$on("$stateChangeError",function (event, toState, toParams, fromState, fromParams, error){
			console.log(error);
			if (error == Access.UNAUTHORIZED) {
				$state.go("login");
			} else if (error == Access.FORBIDDEN) {
				$state.go("forbidden");
			}
		});
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
	}])
	.run([
		'$rootScope',
		'Access',
		'$state',
		stateChangeError
	]);
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
			$resetUserRole : function(){
				$localStorage.$reset();
				userrole = 'anonymous';
				authenticated = false;
				return {
					userrole : userrole,
					is_authenticated : authenticated
				};
			},
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
			Vendor.query(function (response) {
				deferred.resolve(angular.extend(vendorClients, response, {
					$refresh: fetchVendors,
					$updateuserRole: function(){
						return role.$setUserRole();
					},
					$clearUserRole: function(){
						return role.$resetUserRole();
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
					$clearUserRole: function(){
						return role.$resetUserRole();
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
(function(){
	'use strict';
	var opsOrderCntrl = function ($state,$mdSidenav,vendorClients,orderResource,orders){
		console.log(orders);
		this.orders = orders.data;
		this.total_pages = orders.total_pages;
		this.total_orders = orders.total_orders;
		this.pending_orders_count = orders.pending_orders_count;
		this.unassigned_orders_count = orders.unassigned_orders_count;
		this.toggleFilter = function(){
			$mdSidenav('order-filter').toggle();
		};
	};

	var vendorOrderCntrl = function ($state){
		console.log("vendor");
	};

	angular.module('order', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home.opsorder', {
			url: "^/all-orders",
			templateUrl: "/static/modules/order/opsOrders.html",
			controllerAs : 'opsOrder',
    		controller: "opsOrderCntrl",
    		resolve: {
    			vendorClients : 'vendorClients',
    			orderResource : 'Order',
    			access: ["Access","constants", function (Access,constants) { 
    						return Access.hasRole(constants.userRole.ADMIN); 
    					}],
    			orders: ['Order','$stateParams', function (Order,$stateParams){
    						return Order.getOrders.query($stateParams).$promise;
    					}]
    		}
		})
		.state('home.order', {
			url: "^/orders",
			templateUrl: "/static/modules/order/vendorOrders.html",
			controllerAs : 'order',
    		controller: "vendorOrderCntrl",
    		resolve: {
    			vendorClients : 'vendorClients',
    			access: ["Access","constants", function (Access,constants) { 
    				return Access.hasRole(constants.userRole.VENDOR); 
    			}]
    		}
		});
	}])
	.controller('opsOrderCntrl', [
		'$state',
		'$mdSidenav',
		'vendorClients',
		 'orderResource',
		 'orders',
		opsOrderCntrl
	])
	.controller('vendorOrderCntrl', [
		'$state',
		vendorOrderCntrl
	]);
})();