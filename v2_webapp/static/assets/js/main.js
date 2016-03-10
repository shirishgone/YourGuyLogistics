(function(){
	'use strict';
	var LoginCntrl = function ($state,AuthService,UserProfile,$localStorage,constants){
		this.loader = false;
		this.userLogin = function(){
			this.loader = true;
			var self = this;
			var data = {
				username : this.username,
				password : this.password
			};
			AuthService.login(data).then(function (response){
				$localStorage.token = response.data.payload.data.auth_token;
				UserProfile.$refresh().then(function (user){
					if(user.role === constants.userRole.OPS_MANAGER || user.role === constants.userRole.OPS){
						$state.go('home.opsorder');
					}
					else if(user.role === constants.userRole.VENDOR){
						$state.go('home.order');
					}
					else if(user.role === constants.userRole.HR){
						$state.go('home.dgList');
					}
				});
			},function (error){
				self.loader = false;
				self.error_message = error.data.error.message;
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
				UserProfile : "UserProfile",
				access : ["Access",function (Access){
					return Access.isAnonymous();
				}]
			}
		});
	}])
	.controller('LoginCntrl', [
		'$state', 
		'AuthService',
		'UserProfile',
		'$localStorage',
		'constants',
		LoginCntrl
	]);
})();
(function(){
	'use strice';
	var AuthService = function ($http,constants){
		return{
			login : function(userdata) {
				return $http.post(constants.v3baseUrl+'login/',userdata);
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
	var homeCntrl = function($rootScope,$state,$mdSidenav,$mdDialog,$mdToast,constants,UserProfile){
		// Show tabs page accorfing to the credentials.
		var self = this;
		this.tabs =  constants.permissible_tabs[UserProfile.$getUserRole()];
		this.user_name = UserProfile.$getUsername();
		/*
			confirm: an object to specify all the parameters for logout confirmation dialog box.
		*/
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
		/*
			toggle the side navigation bar which shows different tabs available.
			this funvtion is used be every child page to toggl to sidebar.
		*/
		this.toggleSideNav = function(){
			$mdSidenav('left').toggle();
		};
		/*
			@logout: function to logut the user and redirect to login page.
		*/
		this.logout = function(){
			UserProfile.$clearUserRole();
			UserProfile.$refresh().then(function (vendor){
				$state.go('login');
			});
		};
		/*
			@showLogoutDialog: function to show the confirmation dialog box when logout button is clicked.
		*/
		this.showLogoutDialog = function(){
			$mdDialog.show(confirm).then(function(){
				self.logout();
			});
		};
		$rootScope.$on('errorOccured', function(){
			if($rootScope.errorMessage){
				$mdToast.show({
					controller: 'ErrorToastCntrl',
					controllerAs : 'errorToast',
					templateUrl: '/static/modules/home/error-toast-template.html',
					hideDelay: 6000,
					position: 'top right'
				});
			}
		});
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
    			access: ["Access",function (Access){ 
    				return Access.isAuthenticated(); 
    			}],
    			UserProfile : 'UserProfile',
    		}
		});
	}])
	.controller('homeCntrl', [
		'$rootScope',
		'$state',
		'$mdSidenav',
		'$mdDialog',
		'$mdToast',
		'constants',
		'UserProfile',
		homeCntrl
	])
	.controller('ErrorToastCntrl', [
		'$mdToast',
		'$rootScope', 
		function($mdToast,$rootScope){
			this.msg = $rootScope.errorMessage;

			this.closeToast = function() {
				$mdToast.hide();
			};
		}
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
		'deliveryguy',
    'vendor',
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
	'use strict';
	var permissible_tabs = {
		operations : {
			order:true,
			dg:true,
			vendor: true,
			reports: true,
			COD: false,
			customer: false,
			products: false,
			feedback: true,
			tutorial: false,
			notification : true
		},
		vendor: {
			order:true,
			dg:false,
			vendor: false,
			reports: true,
			COD: false,
			customer: true,
			products: true,
			feedback: true,
			tutorial: true,
			notification : false
		},
		hr:{
			order:false,
			dg:true,
			vendor: true,
			reports: false,
			COD: false,
			customer: false,
			products: false,
			feedback: false,
			tutorial: false,
			notification : false
		},
		operations_manager:{
			order:true,
			dg:true,
			vendor: true,
			reports: true,
			COD: false,
			customer: false,
			products: false,
			feedback: true,
			tutorial: false,
			notification : true
		},
		accounts: {
			order:true,
			dg:true,
			vendor: true,
			reports: true,
			COD: true,
			customer: false,
			products: false,
			feedback: false,
			tutorial: false,
			notification : false
		},
		sales : {
			order:true,
			dg:true,
			vendor: true,
			reports: true,
			COD: false,
			customer: false,
			products: false,
			feedback: true,
			tutorial: false,
			notification : false
		},
		sales_manager : {
			order:true,
			dg:true,
			vendor: true,
			reports: true,
			COD: false,
			customer: false,
			products: false,
			feedback: true,
			tutorial: false,
			notification : true
		},
	};
	var STATUS_OBJECT = [
    	{status:'Intransit',value:'INTRANSIT'},
    	{status:'Queued',value:'QUEUED',selected:false},
    	{status:'Delivered',value:'DELIVERED',selected:false},
    	{status:'Order Placed',value:'ORDER_PLACED',selected:false},
    	{status:'Pickup Attempted',value:'PICKUPATTEMPTED',selected:false},
    	{status:'Deliver Attempted',value:'DELIVERYATTEMPTED',selected:false},
    	{status:'Cancelled',value:'CANCELLED',selected:false},
    	{status:'Rejected',value:'REJECTED',selected:false},
  	];
  	var dg_checkin_status = [
  		{status:'All',value:'ALL'},
  		{status:'Checked-In',value:'ONLY_CHECKEDIN'},
  		{status:'Not Checked-In',value:'NOT_CHECKEDIN'},
  		{status:'CheckedIn & CheckedOut',value:'CHECKEDIN_AND_CHECKEDOUT'},
  	];
  	var time_data = [
	  	{
	  		value : "00 AM - 06 AM ",
	  		time: {
	  			start_time: 1,
	  			end_time:6
	  		}
	  	},
	  	{
	  		value : "06 AM - 12 PM",
	  		time: {
	  			start_time: 6,
	  			end_time:12
	  		}
	  	},
	  	{
	  		value : "12 PM - 06 PM",
	  		time: {
	  			start_time: 12,
	  			end_time:18
	  		}
	  	},
	  	{
	  		value : "06 PM - 12 AM",
	  		time: {
	  			start_time: 18,
	  			end_time:23
	  		}
	  	}
  	];

	var constants = {
		v1baseUrl : '/api/v1/',
		v2baseUrl : '/api/v2/',
		v3baseUrl : '/api/v3/',
		userRole  : { 
			OPS           : 'operations', 
			VENDOR        : 'vendor',
			HR            : 'hr',
			OPS_MANAGER   : 'operations_manager',
			ACCOUNTS      : 'accounts',
			SALES         : 'sales',
			SALES_MANAGER : 'sales_manager'
		},
		status    : STATUS_OBJECT,
		time      :time_data,
		dg_status : dg_checkin_status,
		permissible_tabs: permissible_tabs
	};
	var prodConstants = {
		v1baseUrl : 'http://yourguy.herokuapp.com/api/v1/',
		v2baseUrl : 'http://yourguy.herokuapp.com/api/v2/',
		v3baseUrl : 'http://yourguy.herokuapp.com/api/v3/',
		userRole  : { 
			OPS           : 'operations', 
			VENDOR        : 'vendor',
			HR            : 'hr',
			OPS_MANAGER   : 'operations_manager',
			ACCOUNTS      : 'accounts',
			SALES         : 'sales',
			SALES_MANAGER : 'sales_manager'
		},
		status    : STATUS_OBJECT,
		time      : time_data,
		dg_status : dg_checkin_status,
		permissible_tabs : permissible_tabs
	};
	var testConstants = {
		v1baseUrl : 'https://yourguytestserver.herokuapp.com/api/v1/',
		v2baseUrl : 'https://yourguytestserver.herokuapp.com/api/v2/',
		v3baseUrl : 'https://yourguytestserver.herokuapp.com/api/v3/',
		userRole  : { 
			OPS           : 'operations', 
			VENDOR        : 'vendor',
			HR            : 'hr',
			OPS_MANAGER   : 'operations_manager',
			ACCOUNTS      : 'accounts',
			SALES         : 'sales',
			SALES_MANAGER : 'sales_manager'
		},
		status    : STATUS_OBJECT,
		time      : time_data,
		dg_status : dg_checkin_status,
		permissible_tabs: permissible_tabs
	};

	angular.module('ygVendorApp')
	.constant('constants', constants);
})();
(function(){
	'use strict';
	var Access = function($q,UserProfile){
		var Access = {
			OK: 200,
			UNAUTHORIZED: 401,
    		FORBIDDEN: 403,

    		hasRole : function(role){
    			var deferred = $q.defer();
    			UserProfile.then(function (UserProfile){
    				if(UserProfile.$hasRole(role)){
    					deferred.resolve(Access.OK);
    				}
    				else if(UserProfile.$isAnonymous()){
    					deferred.reject(Access.UNAUTHORIZED);
    				}
    				else{
    					deferred.reject(Access.FORBIDDEN);
    				}
    			});
    			return deferred.promise;
    		},
            hasAnyRole: function(roles) {
                var deferred = $q.defer();
                UserProfile.then(function(userProfile) {
                    if (userProfile.$hasAnyRole(roles)) {
                        deferred.resolve(Access.OK);
                    } else if (userProfile.$isAnonymous()) {
                        deferred.reject(Access.UNAUTHORIZED);
                    } else {
                        deferred.reject(Access.FORBIDDEN);
                    }
                });
              return deferred.promise;
            },
    		isAuthenticated : function(){
    			var deferred = $q.defer();
    			UserProfile.then(function (UserProfile){
    				if(UserProfile.$isAuthenticated()){
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
    			UserProfile.then(function (UserProfile){
    				if(UserProfile.$isAnonymous()){
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
		'UserProfile',
		Access
	]);
})();
(function(){
	'use strict';
	var DeliverGuy = function ($resource,constants){
		return {
			dg : $resource(constants.v3baseUrl+'deliveryguy/:id/',{id:"@id"},{
				query :{
					method: 'GET',
					isArray: true
				},
				$update : {
					url : constants.v3baseUrl+'deliveryguy/:id'+'/edit_dg_details/',
					method: 'PUT'
				},
				attendance : {
					url : constants.v3baseUrl+'deliveryguy/:id'+'/attendance/',
					method : 'PUT'
				},
				associated_dgs : {
					url : constants.v3baseUrl+'deliveryguy/:id'+'/tl_associated_dgs/',
					method : 'GET'
				},
				promoteToTL : {
					url : constants.v3baseUrl+'deliveryguy/:id'+'/promote_to_teamlead/',
					method : 'PUT'
				}
			}),
			dgPageQuery : $resource(constants.v3baseUrl+'deliveryguy/:id/',{id:"@id"},{
				query :{
					method: 'GET',
					isArray: false
				}
			}),
			dgTeamLeadQuery : $resource(constants.v3baseUrl+'deliveryguy/teamleads/', {}, {
				query : {
					method : 'GET',
					isArray : false
				}
			}),
			dgOpsManagerQuery : $resource(constants.v3baseUrl+'deliveryguy/ops_executives/', {}, {
				query : {
					method : 'GET',
					isArray : false
				}
			}),
			dgServicablePincodes : $resource(constants.v3baseUrl+'servicible_pincodes/', {}, {
				query : {
					method : 'GET',
					isArray : false
				}
			}),
			dgsAttendance : $resource(constants.v3baseUrl+'deliveryguy/download_attendance/', {}, {
				query : {
					method : 'GET',
					isArray : false
				}
			})
		};
	};
	
	angular.module('ygVendorApp')
	.factory('DeliveryGuy', [
		'$resource',
		'constants', 
		DeliverGuy
	]);
})();
(function(){
	'use strict';
	var Order = function ($resource,constants){
		return {
			getOrders : $resource(constants.v3baseUrl+'order/:id/',{id:"@id"},{
				query :{
					method: 'GET',
					isArray: false
				}
			}),
			assignOrders : $resource(constants.v3baseUrl+'order/assign_orders/', {}, {
				assign : {
					method: 'PUT',
				}
			}),
			updatePickup : $resource(constants.v3baseUrl+'order/:id/picked_up/',{id:"@id"},{
				update : {
					method: 'PUT'
				}
			}),
			updateDelivered : $resource(constants.v3baseUrl+'order/:id/delivered/',{id:"@id"},{
				update : {
					method: 'PUT'
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
	var Profile = function ($resource,constants){
		return $resource(constants.v3baseUrl+'profile/',{},{
			profile: {
				method: 'GET',
				transformResponse: function(data,headers){
					var response = angular.fromJson(data);
					if(response.payload){
						response.payload.data.is_authenticated = response.success;
						return response.payload.data;
					}
					else{
						return response;
					}
				}
			}
		});
	};
	
	angular.module('ygVendorApp')
	.factory('Profile', [
		'$resource',
		'constants', 
		Profile
	]);
})();
(function(){
	'use strict';
	var Vendor = function ($resource,constants){
		return $resource(constants.v3baseUrl+'vendor/:id/',{id:"@id"},{
			profile: {
				method: 'GET'
			},
			query :{
				method: 'GET',
				isArray: false,
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
// (function(){
// 	'use strict';
// 	var DgList = function ($q,DeliverGuy){
// 		var deliveryguy = {};
// 		var fetchdg = function() {
// 			var deferred = $q.defer();
// 			DeliverGuy.dgListQuery.query(function (response) {
// 				deferred.resolve(angular.extend(deliveryguy, {
// 					dgs : response,
// 					$refresh: fetchdg,
// 				}));

// 			}, function (error){
// 				deferred.reject(angular.extend(deliveryguy , error ,{
// 					$refresh : fetchdg,
// 				}));
// 			});
// 			return deferred.promise;
// 		};
// 		return fetchdg();
// 	};

// 	angular.module('ygVendorApp')
// 	.factory('DgList', [
// 		'$q',
// 		'DeliverGuy', 
// 		DgList
// 	]);
// })();
(function(){
	'use strict';
	var errorHandler = function ($q,$localStorage,$location,$rootScope){
		var errorHandler = {
			responseError : function(response){
				if(response.data.error){
					$rootScope.errorMessage = response.data.error.message;
				}
				var defer = $q.defer();
				if (response.status === 401 || response.status === 403) {
					$localStorage.$reset();
					$location.path('/login');
				}
				else if(response.status === 500){
					$rootScope.errorMessage = 'Something Went Wrong';
				}
				$rootScope.$broadcast('errorOccured');
				defer.reject(response);
				return defer.promise;

			}
		};
		return errorHandler;
	};

	var stateChangeHandler = function ($rootScope, Access, $state,$document){
		$rootScope.$on("$stateChangeError",function (event, toState, toParams, fromState, fromParams, error){
			angular.element($document[0].getElementsByClassName('request-loader')).addClass('request-loader-hidden');
			if (error == Access.UNAUTHORIZED) {
				$state.go("login");
			} else if (error == Access.FORBIDDEN) {
				$state.go("forbidden");
			}
		});
		$rootScope.$on("$stateChangeStart",function (event, toState, toParams, fromState, fromParams){
			angular.element($document[0].getElementsByClassName('request-loader')).removeClass('request-loader-hidden');
		});
		$rootScope.$on("$stateChangeSuccess",function (event, toState, toParams, fromState, fromParams){
			$rootScope.previousState = {
				state : fromState.name,
				params : fromParams
			};
			angular.element($document[0].getElementsByClassName('request-loader')).addClass('request-loader-hidden');
		});
	};

	angular.module('ygVendorApp')
	.factory('errorHandler', [
		'$q',
		'$localStorage',
		'$location',
		'$rootScope', 
		errorHandler
	])
	.config(['$httpProvider',function ($httpProvider) {
		$httpProvider.interceptors.push('errorHandler');
	}])
	.run([
		'$rootScope',
		'Access',
		'$state',
		'$document',
		stateChangeHandler
	]);
})();
(function(){
	'use strict';
	/*
		A service to handle and move to the previous state with all the url parameters,
		this fucntion uses the rootscope previousState object and redirects from the current page 
		to the previous page, and if the page is reloaded or the previous state is empty it returns 
		a boolean data to do validation check and handle the edge case.
	*/
	var PreviousState = function($rootScope,$state){
		return {
			isAvailable : function(){
				if(!$rootScope.previousState.state || $rootScope.previousState.state === ''){
					return false;
				}
				else{
					return true;
				}
			},
			redirectToPrevious : function(){
				$state.go($rootScope.previousState.state,$rootScope.previousState.params);
				return;
			}
		};
	};

	angular.module('ygVendorApp')
	.factory('PreviousState', [
		'$rootScope',
		'$state',
		PreviousState
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
	'use strict';
	var UserProfile = function ($q,role,Profile){
		var userProfile = {};
		var fetchUserProfile = function() {
			var deferred = $q.defer();
			Profile.profile(function (response) {
				if (userProfile.hasOwnProperty('role')) {
					delete userProfile.role;
				}
				if (userProfile.hasOwnProperty('name')) {
					delete userProfile.name;
				}
				if (userProfile.hasOwnProperty('is_authenticated')) {
					delete userProfile.is_authenticated;
				}
				deferred.resolve(angular.extend(userProfile, response, {
					$refresh: fetchUserProfile,
					$getUsername: function(){
						return userProfile.name;
					},
					$getUserRole: function(){
						return userProfile.role;
					},
					$clearUserRole: function(){
						return role.$resetUserRole();
					},
					$hasRole: function(roleValue) {
						return userProfile.role === roleValue;
					},
					$hasAnyRole: function(roles) {
						return roles.indexOf(userProfile.role) >= 0;
					},
					$isAuthenticated: function() {
						return userProfile.is_authenticated;
					},
					$isAnonymous: function() {
						return !userProfile.is_authenticated;
					}
				}));

			}, function (error){
				userProfile = {};
				deferred.resolve(angular.extend(userProfile ,{
					$refresh : fetchUserProfile,
					$clearUserRole: function(){
						return role.$resetUserRole();
					},
					$hasRole : function (roleValue){
						return userProfile.role == roleValue;
					},
					$hasAnyRole: function(roles) {
						return roles.indexOf(userProfile.role) >= 0;
					},
					$isAuthenticated: function() {
						return userProfile.is_authenticated;
					},
					$isAnonymous: function() {
						return !userProfile.is_authenticated;
					}
				}));
			});
			return deferred.promise;
		};
		return fetchUserProfile();
	};

	angular.module('ygVendorApp')
	.factory('UserProfile', [
		'$q',
		'role',
		'Profile', 
		UserProfile
	]);
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
			$setUserRole : function(role){
				if(role){
					userrole = role;
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
	var ydExcelDownload = function(){
		// Runs during compile
		return {
			// name: '',
			// priority: 1,
			// terminal: true,
			// controller: function($scope, $element, $attrs, $transclude) {},
			// require: 'ngModel', // Array = multiple requires, ? = optional, ^ = check parent elements
			
			// template: '',
			// templateUrl: '',
			// replace: true,
			// transclude: true,
			// compile: function(tElement, tAttrs, function transclude(function(scope, cloneLinkingFn){ return function linking(scope, elm, attrs){}})),
			scope: {
				workbookData : '=',

			}, // {} = isolate, true = child, false/undefined = no change
			restrict: 'AE', // E = Element, A = Attribute, C = Class, M = Comment
			link: function($scope, iElm, iAttrs, controller) {
				// alasql.fn.toUpperCasse = function(name){
				// 	name = name.toUpperCasse();
				// 	name = name.replace(/[^a-zA-Z0-9]/g,' ');
				// };
				var download = function(){
					alasql('SELECT * INTO XLSX("orders.xlsx",{headers:true}) FROM ?',[$scope.workbookData]);
				};
				iElm.bind('click',download);
			}
		};
	};
	angular.module('ygVendorApp')
	.directive('ydExcelDownload', 
		ydExcelDownload
	);

})();
(function(){
	'use strict';
	angular.module('ygVendorApp')
	.directive('ydPagination', [function(){
		// Runs during compile
		return {
			// name: '',
			// priority: 1,
			// terminal: true,
			// template: '',
			// templateUrl: '',
			// replace: true,
			// transclude: true,
			// compile: function(tElement, tAttrs, function transclude(function(scope, cloneLinkingFn){ return function linking(scope, elm, attrs){}})),
			// controller: function($scope, $element, $attrs, $transclude) {},
			// require: 'ngModel', // Array = multiple requires, ? = optional, ^ = check parent elements
			/*
				scope {
					@total      : total data count to show as total data.
					@totalPage  : total number of pages the present.
					@params     : all the params that needs to be sent, like page, date etc. it should be a object with madatory page property.
					@listLength : total count of current data list.
					@paginate   : object which contains two function to paginate to next and previous page.
					@pending    : optional! number of pending data which aren't executed yet.
					@unassigned : optional! number of unassigned data which aren't assagined yet.
					@getData    : a function of parent controller to reload the data as params changes. 
				}
			*/
			scope: {
				total       : '@',
				totalPage   : '@',
				params      : '=',
				listLength  : '@',
				paginate    : '=',
				pending     : '@?',
				unassigned  : '@?',
				getData     : '&',
			}, // {} = isolate, true = child, false/undefined = no change
			restrict: 'AE', // E = Element, A = Attribute, C = Class, M = Comment
			link: function($scope, iElm, iAttrs, controller) {
				$scope.orderFrom = ( ( ( $scope.params.page -1 ) * 50 ) + 1 );
				$scope.orderTo  = ($scope.orderFrom-1) + parseInt($scope.listLength);
				$scope.pageRange = function (){
					return new Array(parseInt($scope.totalPage));
				};
			},
			template : [
				'<div class="ydPagination" layout="row" layout-align="start center">',
					'<div class="stats" layout="row">',
						'<p ng-if="pending"> <span class="pending-text">Pending: </span><span class="pending">{{pending}}</span> </p>',
						'<p ng-if="unassigned"><span class="unassigned-text">Unassigned: </span><span class="unassigned">{{unassigned}}</span> </p>',
						'<p>Total: {{total}} </p>',
					'</div>',
					'<span flex></span>',
					'<div class="pagination" layout="row" layout-align="start center">',
						'<p>Page:</p>',
						'<md-input-container class="md-accent">',
							// '<label class="hide-gt-xs">Page</label>',
							'<md-select class="md-warn" ng-model="params.page" ng-change="getData()" aria-label="page select">',
								'<md-option class="md-accent" ng-repeat="page in pageRange() track by $index" value="{{$index + 1}}">{{$index + 1}}</md-option>',
							'</md-select>',
						'</md-input-container>',
					'</div>',
					'<div class="pagination hide-xs" layout="row" layout-align="start center">',
						'<p>{{orderFrom}} -- {{orderTo}} of {{total}}</p>',
					'</div>',
					'<div class="page-navigation">',
						'<md-button ng-disabled="params.page == 1" ng-click="paginate.previouspage();" class="md-icon-button md-primary" aria-label="Menu Icon">',
								'<md-icon>arrow_backward</md-icon>',
						'</md-button>',
						'<md-button ng-disabled="params.page == totalPage" ng-click="paginate.nextpage();" class="md-icon-button md-primary" aria-label="Menu Icon">',
								'<md-icon>arrow_forward</md-icon>',
						'</md-button>',
					'</div>',
				'</div>',
			].join('')
		};
	}]);
})();
(function(){
	'use strict';
	var vendorOrderCntrl = function ($state){
		console.log("vendor");
	};

	angular.module('order', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home.opsorder', {
			url: "^/all-orders?date&vendor_id&dg_username&order_status&page&start_time&end_time&is_cod&search&delivery_ids&pincodes&is_retail",
			templateUrl: "/static/modules/order/list/list.html",
			controllerAs : 'opsOrder',
    		controller: "opsOrderCntrl",
    		resolve: {
    			DeliveryGuy : 'DeliveryGuy',
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    			orders: ['Order','$stateParams', function (Order,$stateParams){
    						$stateParams.date = ($stateParams.date !== undefined) ? new Date($stateParams.date).toISOString() : new Date().toISOString();
    						$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
						    $stateParams.is_cod = ($stateParams.is_cod == 'true')? Boolean($stateParams.is_cod): null;
						    $stateParams.is_retail = ($stateParams.is_retail == 'true')? Boolean($stateParams.is_retail): null;

						    if(Array.isArray($stateParams.order_status)){
    							$stateParams.order_status = ($stateParams.order_status.length > 0) ? $stateParams.order_status.toString(): null;
    						}
    						
    						if(Array.isArray($stateParams.pincodes)){
    							$stateParams.pincodes = ($stateParams.pincodes.length > 0) ? $stateParams.pincodes.toString(): null;
    						}
    						return Order.getOrders.query($stateParams).$promise;
    					}],
    			Pincodes: ['DeliveryGuy',function(DeliveryGuy){
    						return DeliveryGuy.dgServicablePincodes.query().$promise;
    					}]
    		}
		})
		.state('home.order', {
			url: "^/orders",
			templateUrl: "/static/modules/order/vendorOrders.html",
			controllerAs : 'order',
    		controller: "vendorOrderCntrl",
    		resolve: {
    			access: ["Access","constants", function (Access,constants) { 
    				return Access.hasRole(constants.userRole.VENDOR); 
    			}]
    		}
		});
	}])
	.controller('vendorOrderCntrl', [
		'$state',
		vendorOrderCntrl
	]);
})();
(function(){
	'use strict';
	var orderDgAssign = function($mdMedia,$mdDialog,DeliveryGuy){
		return {
			openDgDialog : function(){
				var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'));
				return $mdDialog.show({
					controller         : ('AssignDgCntrl',['$mdDialog','DeliveryGuy',AssignDgCntrl]),
					controllerAs       : 'assignDG',
					templateUrl        : '/static/modules/order/dialogs/assign-dg.html?nd=' + Date.now(),
					parent             : angular.element(document.body),
					clickOutsideToClose: false,
					fullscreen         : useFullScreen,
					openFrom           : '#options',
					closeTo            : '#options',
				});
			}

		};
	};
	/*
		@AssignDgCntrl controller function for the assign delivery guy dialog
	*/
	function AssignDgCntrl($mdDialog,DeliveryGuy){
		var self = this;
		this.assignment_data = {
			pickup: {
				dg_id: null,
				assignment_type: 'pickup'
			},
			delivery: {
				dg_id: null,
				assignment_type: 'delivery'
			}
		};

		this.cancel = function() {
			$mdDialog.cancel();
		};
		this.answer = function(answer) {
			$mdDialog.hide(answer);
		};
		this.dgSearchTextChange = function(text){
			var search = {
				search : text
			};
			return DeliveryGuy.dgPageQuery.query(search).$promise.then(function (response){
				return response.payload.data.data;
			});
		};
		this.pickupDgChange = function(dg){
			if(dg){
				self.assignment_data.pickup.dg_id = dg.id;
			}
			else{
				self.assignment_data.pickup.dg_id = undefined;
			}
		};
		this.deliveryDgChange = function(dg){
			if(dg){
				self.assignment_data.delivery.dg_id = dg.id;
			}
			else{
				self.assignment_data.delivery.dg_id = undefined;
			}
		};
	}

	angular.module('order')
	.factory('orderDgAssign', [
		'$mdMedia',
		'$mdDialog',
		'DeliveryGuy',
		orderDgAssign
	]);
})();
(function(){
	'use strict';
	var orderFilter = function(){
		var orderfilter = {
			filter : {
				date : null,
				vendor : null,
				dg : null,
				cod : false,
				status : [],
				time : null,
				search : null
			},
			setFilter : function (object){
				object.date = orderfilter.date;
				object.vendor = orderfilter.vendor;
				object.dg = orderfilter.dg;
				object.cod = orderfilter.cod;
				object.status = orderfilter.status;
				object.time = orderfilter.time;
				object.search = orderfilter.search;
			},
			getFilter : function (){
				return orderfilter.filter;
			}

		};
		return orderFilter;
	};

	angular.module('order')
	.factory('orderFilter', [
		orderFilter

	]);

})();
(function(){
	'use strict';
	var orderSelection = function(){
		var orderselection = {
			selectedItemArray : [],
			toggle : function (item){
				var idx = orderselection.selectedItemArray.indexOf(item);
        		if (idx > -1) orderselection.selectedItemArray.splice(idx, 1);
        		else orderselection.selectedItemArray.push(item);
			},
			exists : function (item) {
        		return orderselection.selectedItemArray.indexOf(item) > -1;

      		},
			addItem : function(item){
				item.selected = true;
				orderselection.selectedItemArray.push(item);
			},
			removeItem : function (item){
				var index = selectedItemArray.indexOf(item);
				if(index > -1) {
					item.selected = false;
					orderselection.selectedItemArray.splice(index,1);
					return true;
				}
				else{
					return false;
				}
			},
			isSelected : function(){
				if(orderselection.selectedItemArray.length > 0){
					return true;
				}
				else {
					return false;
				}
			},
			clearAll : function (){
				orderselection.selectedItemArray = [];
				return orderselection.selectedItemArray;
			},
			slectedItemLength : function (){
				return orderselection.selectedItemArray.length;
			},
			getAllItemsIds : function(){
				var array = [];
				orderselection.selectedItemArray.forEach(function(order){
					array.push(order.id);
				});
				return array;
			}
		};
		return orderselection;
	};

	angular.module('order')
	.factory('orderSelection', [
		orderSelection
	]);

})();
(function(){
	'use strict';
	var orderDgAssign = function($mdMedia,$mdDialog){
		return {
			openStatusDialog : function(){
				var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'));
				return $mdDialog.show({
					controller         : ('OrderStatusUpdateCntrl',['$mdDialog',OrderStatusUpdateCntrl]),
					controllerAs       : 'statusUpdate',
					templateUrl        : '/static/modules/order/dialogs/status-update.html?nd=' + Date.now(),
					parent             : angular.element(document.body),
					clickOutsideToClose: false,
					fullscreen         : useFullScreen,
					openFrom           : '#options',
					closeTo            : '#options',
				});
			}

		};
	};
	/*
		@OrderStatusUpdateCntrl controller function for the update status for orders dialog
	*/
	function OrderStatusUpdateCntrl($mdDialog){
		var self = this;
		this.pickup = {
			isPickup: true,
			data : {
				pickup_attempted : false,
				delivery_remarks : null
			}
		};
		this.delivery = {
			isPickup: false ,
			data : {
				delivered_at : null,
				delivery_attempted : false,
				delivery_remarks: null,
				cod_collected_amount: null
			}
		};

		this.cancel = function() {
			$mdDialog.cancel();
		};
		this.updatePickupAttempted = function(answer){
			answer.data.pickup_attempted = true;
			$mdDialog.hide(answer);
		};
		this.updatePickup = function(answer){
			answer.data.pickup_attempted = false;
			$mdDialog.hide(answer);
		};
		this.updateDeliveryAttempted = function(answer){
			answer.data.delivery_attempted = true;
			$mdDialog.hide(answer);
		};
		this.updateDelivery = function(answer){
			answer.data.delivery_attempted = false;
			$mdDialog.hide(answer);
		};
	}

	angular.module('order')
	.factory('OrderStatusUpdate', [
		'$mdMedia',
		'$mdDialog',
		orderDgAssign
	]);
})();
(function(){
	'use strict';
	var opsOrderCntrl = function ($state,$mdSidenav,$mdDialog,$mdMedia,$stateParams,DeliveryGuy,Order,Vendor,orders,constants,orderSelection,Pincodes,$q,orderDgAssign,OrderStatusUpdate){
		/*
			 Variable definations for the route(Url)
		*/
		var self = this;
		this.params = $stateParams;
		this.params.order_status = ($stateParams.order_status)? $stateParams.order_status.split(','): [];
		this.params.pincodes     = ($stateParams.pincodes)    ? $stateParams.pincodes.split(','): [];
		this.params.date         = new Date(this.params.date);
		this.searchedDg          = this.params.dg_username;
		this.searchVendor        = this.params.vendor_id;
		this.searchOrderActive = (this.params.search !== undefined) ? true : false;
		/*
			 scope Orders variable assignments are done from this section for the controller
		*/
		this.orders = orders.payload.data.data;
		this.orderFrom = ( ( ( this.params.page -1 ) * 50 ) + 1 );
		this.orderTo  = (this.orderFrom-1) + orders.payload.data.data.length;
		this.total_pages = orders.payload.data.total_pages;
		this.total_orders = orders.payload.data.total_orders;
		this.pending_orders_count = orders.payload.data.pending_orders_count;
		this.unassigned_orders_count = orders.payload.data.unassigned_orders_count;
		this.pincodes = Pincodes.payload.data;
		/*
			@ status_list: scope order status for eg: 'INTRANSIT' ,'DELIVERED' variable assignments.
			@ time_list: scope order time for time filer variable assignments.
		*/
		this.status_list = constants.status;
		this.time_list = constants.time;
		/*
			@backFromSearch is a function to revert back from a searched dorder view to complete list view of orders
		*/ 
		this.backFromSearch = function(){
			self.params.search = undefined;
			self.searchOrderActive = false;
			self.getOrders();
			
		};
		/*
			@ All method defination for the controller starts from here on.
		*/
		/*
			 @ toggleFilter : main sidenav toggle function, this function toggle the sidebar of the filets of the orders page page.
		*/
		this.toggleFilter = function(){
			$mdSidenav('order-filter').toggle();
		};
		/*
			@pagerange: funxtion for total pages generations for pagination
		*/
		this.pageRange = function (n){
			return new Array(n);
		};
		/*
			@paginate is a function to paginate to the next and previous page of the order list
			@statusSelection is a fucntion to select or unselect the status data in order filter
			@pincodesSelection is a function select unselect multiple pincode in order filter
		*/
		this.paginate = {
			nextpage : function(){
				self.params.page = self.params.page + 1;
				self.getOrders();
			},
			previouspage : function(){
				self.params.page = self.params.page - 1;
				self.getOrders();
			}
		};
		this.statusSelection = {
			toggle : function (item , list){
				var idx = list.indexOf(item.value);
        		if (idx > -1) list.splice(idx, 1);
        		else list.push(item.value);
			},
			exists : function (item, list) {
        		return list.indexOf(item.value) > -1;

      		}
		};
		this.pincodesSelection = {
			toggle : function (item , list){
				var idx = list.indexOf(item.pincode);
        		if (idx > -1) list.splice(idx, 1);
        		else list.push(item.pincode);
			},
			exists : function (item, list) {
        		return list.indexOf(item.pincode) > -1;

      		}
		};
		/*
			@dgSearchTextChange is a function for Delivery guy search for filter. When ever the filtered dg change, 
			this function is called.

			@selectedDgChange is a callback function after delivery guy selection in the filter.
		*/
		this.dgSearchTextChange = function(text){
			var search = {
				search : text
			};
			return DeliveryGuy.dgPageQuery.query(search).$promise.then(function (response){
				return response.payload.data.data;
			});
		};
		this.selectedDgChange = function(dg){
			if(dg){
				self.params.dg_username = dg.phone_number;
			}
			else{
				self.params.dg_username = undefined;
			}
		};
		/*
			@dgSearchTextChange is a function for Delivery guy search for filter. When ever the filtered dg change, 
			this function is called.

			@selectedDgChange is a callback function after delivery guy selection in the filter.
		*/
		this.vendorSearchTextChange = function(text){
			var search = {
				search : text
			};
			return Vendor.query(search).$promise.then(function (response){
				return response.payload.data.data;
			});
		};
		this.selectedVendorChange = function(vendor){
			if(vendor){
				self.params.vendor_id = vendor.id;
			}
			else{
				self.params.vendor_id = undefined;
			}
		};
		/*
			@getOrders rleoads the order controller according too the filter to get the new filtered data.
		*/
		this.handleOrdeSelection = {
			selectActive : orderSelection.isSelected(),
			numberOfSelectedOrder : orderSelection.slectedItemLength(),
			update : function () {
				self.handleOrdeSelection.selectActive = orderSelection.isSelected();
				self.handleOrdeSelection.numberOfSelectedOrder = orderSelection.slectedItemLength();
			},
			toggle : function(item){
				orderSelection.toggle(item);
				self.handleOrdeSelection.update();
			},
			exists : function(item){
				return orderSelection.exists(item);
			},
			clear : function (){
				orderSelection.clearAll();
				self.handleOrdeSelection.update();
			}
		};
		/*
			@assignDg is a function to open dg assignment dialog box and assign delivery guy and pickup guy for the 
			selected orders once user confirms things.
		*/
		self.assignDg = function(){
			orderDgAssign.openDgDialog()
			.then(function(assign_data) {
				assign_data.pickup.delivery_ids = orderSelection.getAllItemsIds();
				assign_data.delivery.delivery_ids = orderSelection.getAllItemsIds();
				self.assignOrders(assign_data);
			});
		};
		self.assignDgForSingleOrder = function(order){
			orderDgAssign.openDgDialog()
			.then(function(assign_data) {
				assign_data.pickup.delivery_ids = [order.id];
				assign_data.delivery.delivery_ids = [order.id];
				self.assignOrders(assign_data);
			});
		};
		/*
			@assignOrders is a function to call the order assign api from Order service and handle the response.
		*/
		self.assignOrders = function(assign_data){
			var array = [];
			if(assign_data.pickup.dg_id){
				array.push(Order.assignOrders.assign(assign_data.pickup).$promise);
			}
			if(assign_data.delivery.dg_id){
				array.push(Order.assignOrders.assign(assign_data.delivery).$promise);
			}
			$q.all(array).then(function(data){
				orderSelection.clearAll();
				self.getOrders();
			});
		};

		this.statusUpdateForSingleDialog = function(order){
			OrderStatusUpdate.openStatusDialog()
			.then(function(status_data) {
				status_data.delivery_ids = [order.id];
				if(status_data.isPickup){
					self.updatePickupStatus(status_data);
				}
				else{
					self.updateDeliveryStatus(status_data);
				}
			});
		};

		this.statusUpdateDialog = function(){
			OrderStatusUpdate.openStatusDialog()
			.then(function(status_data) {
				status_data.delivery_ids = orderSelection.getAllItemsIds();
				if(status_data.isPickup){
					self.updatePickupStatus(status_data);
				}
				else{
					self.updateDeliveryStatus(status_data);
				}
			});
		};
		self.updatePickupStatus = function(status_data){
			var array = [];
			for(var i=0; i< status_data.delivery_ids.length;i++){
				status_data.data.id = status_data.delivery_ids[i];
				array.push(Order.updatePickup.update(status_data.data).$promise);
			}
			$q.all(array).then(function(data){
				orderSelection.clearAll();
				self.getOrders();
			});
		};
		self.updateDeliveryStatus = function(status_data){
			var array = [];
			for(var i=0; i< status_data.delivery_ids.length;i++){
				status_data.data.id = status_data.delivery_ids[i];
				array.push(Order.updateDelivered.update(status_data.data).$promise);
			}
			$q.all(array).then(function(data){
				orderSelection.clearAll();
				self.getOrders();
			});
		};
		/*
			@getOrders rleoads the order controller according too the filter to get the new filtered data.
		*/
		this.getOrders = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('order')
	.controller('opsOrderCntrl', [
		'$state',
		'$mdSidenav',
		'$mdDialog',
		'$mdMedia',
		'$stateParams',
		'DeliveryGuy',
		'Order',
		'Vendor',
		'orders',
		'constants',
		'orderSelection',
		'Pincodes',
		'$q',
		'orderDgAssign',
		'OrderStatusUpdate',
		opsOrderCntrl
	]);
})();
(function(){
	'use strict';
	angular.module('deliveryguy', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home.dgList', {
			url: "^/deliveryguy/list?date&attendance&search&page",
			templateUrl: "/static/modules/deliveryguy/list/list.html",
			controllerAs : 'dgList',
    		controller: "dgListCntrl",
    		resolve : {
    			DeliveryGuy : 'DeliveryGuy',
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER,constants.userRole.HR];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    			dgs: ['DeliveryGuy','$stateParams', function (DeliveryGuy,$stateParams){
    						$stateParams.date = ($stateParams.date !== undefined) ? new Date($stateParams.date).toISOString() : new Date().toISOString();
    						$stateParams.attendance = ($stateParams.attendance!== undefined) ? $stateParams.attendance : 'ALL';
    						$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    						return DeliveryGuy.dgPageQuery.query($stateParams).$promise;
    					}]
    		}
		})
		.state('home.dgCreate', {
			url: "^/deliveryguy/create",
			templateUrl: "/static/modules/deliveryguy/create/create.html",
			controllerAs : 'dgCreate',
    		controller: "dgCreateCntrl",
    		resolve : {
    			DeliveryGuy : 'DeliveryGuy',
    			access: ["Access","constants", function (Access,constants) { 
    						return Access.hasRole(constants.userRole.HR); 
    					}],
    			leadUserList : ['DeliveryGuy','$q', function (DeliveryGuy,$q){
		    				return $q.all ({
		    					TeamLead : DeliveryGuy.dgTeamLeadQuery.query().$promise,
		    					OpsManager : DeliveryGuy.dgOpsManagerQuery.query().$promise
		    				});
    					}],
    		}
		})
		.state('home.dgDetail', {
			url: "^/deliveryguy/detail/:id",
			templateUrl: "/static/modules/deliveryguy/detail/detail.html",
			controllerAs : 'dgDetail',
		 	controller: "dgDetailCntrl",
		 	resolve  : {
		 		DeliveryGuy : 'DeliveryGuy',
		 		access: ["Access","constants", function (Access,constants) { 
		 					var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER,constants.userRole.HR];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    			DG    : ['DeliveryGuy','$stateParams',function(DeliveryGuy,$stateParams){
    						var dg =  new DeliveryGuy.dg();
    						return DeliveryGuy.dg.get($stateParams).$promise;
    					}],
    			leadUserList : ['DeliveryGuy','$q', function (DeliveryGuy,$q){
		    				return $q.all ({
		    					TeamLead : DeliveryGuy.dgTeamLeadQuery.query().$promise,
		    					OpsManager : DeliveryGuy.dgOpsManagerQuery.query().$promise
		    				});
    					}],
		 	}
		});
	}]);
})();
(function(){
	'use strict';
	/*
		Constant for storing all the static value required for dgs.
		1. Dg shift timings
		2. Dg transportation mode
	*/
	var dgConstantData = {
		shift_timings : [
			{
				start_time : '06:00:00',
				end_time   : '15:00:00'
			},
			{
				start_time : '07:00:00',
				end_time   : '16:00:00'
			},
			{
				start_time : '09:00:00',
				end_time   : '18:00:00'
			},
			{
				start_time : '10:00:00',
				end_time   : '19:00:00'
			},
			{
				start_time : '10:30:00',
				end_time   : '19:30:00'
			},
			{
				start_time : '11:00:00',
				end_time   : '20:00:00'
			},
			{
				start_time : '13:00:00',
				end_time   : '22:00:00'
			},
			{
				start_time : '14:00:00',
				end_time   : '23:00:00'
			}
		],
		transportation_mode : [
			{
				key: 'Biker',
				value : 'BIKER'
			},
			{
				key: 'Walker',
				value : 'WALKER'
			},
			{
				key: 'Car Driver',
				value : 'CAR_DRIVER'
			}
		]
	};

	angular.module('deliveryguy')
	.constant('dgConstants', dgConstantData);
})();
(function(){
	'use strict';
	/*
		filter to convert a time string to specific format for displaying it in dropdown. 
		For eg: 09:00:00 with beconverted to a format to 09:00 AM, 
		which can be shown in dropdowns or any place for ease of user.
	*/
	var timeAsDate = function($filter){
		return function(input){
			if(input) {
				var time = input.split(':');
				return moment().hour(time[0]).minute(time[1]).format('hh:mm A');
			}
			else {
				return false;
			}
			
		};
	};
	angular.module('deliveryguy')
	.filter('timeAsDate',[
		'$filter',
		timeAsDate
	]);
})();
(function(){
	'use strict';
	/*
		dgListCntrl is the controller for the delivery guy list page. 
		Its resolved after loading all the dgs from the server.
			
	*/
	var dgListCntrl = function($state,$mdSidenav,$stateParams,dgs,constants,DeliveryGuy){
		var self = this;
		this.params = $stateParams;
		this.params.date = new Date(this.params.date);
		this.dg_status = constants.dg_status;
		this.searchDgActive = (this.params.search !== undefined) ? true : false;
		/*
			@dgs: resolved dgs list accordign to the url prameters.
		*/
		this.dgs = dgs.payload.data.data;
		this.total_pages = dgs.payload.data.total_pages;
		this.total_dgs = dgs.payload.data.total_dg_count;

		/*
			 @ toggleFilter : main sidenav toggle function, this function toggle the sidebar of the filets of the dg page page.
		*/
		this.toggleFilter = function(){
			$mdSidenav('dgList-filter').toggle();
		};
		/*
			@paginate is a function to paginate to the next and previous page of the delivery guy list
		*/
		this.paginate = {
			nextpage : function(){
				self.params.page = self.params.page + 1;
				self.getDgs();
			},
			previouspage : function(){
				self.params.page = self.params.page - 1;
				self.getDgs();
			}
		};
		/*
			@backFromSearch is a function to revert back from a searched delivery guy name to complete list view of delivery guys
		*/ 
		this.backFromSearch = function(){
			self.params.search = undefined;
			self.searchDgActive = false;
			self.getDgs();
			
		};
		this.downloadAttendance = function(){
			var attendance_params = {
				start_date : moment(self.params.date).format(),
				end_date   : moment(self.params.date).format()
			};
			DeliveryGuy.dgsAttendance.query(attendance_params,function(response){
				alasql.fn.IsoToDate = function(n){
					return moment(n).format('DD-MM-YYYY');
				};
				var str = 'SELECT name AS Name,IsoToDate(attendance -> 0 -> date) AS Date,attendance -> 0 -> worked_hrs AS Hours';
				alasql( str+' INTO XLSX("attendance.xlsx",{headers:true}) FROM ?',[response.payload.data]);
			});
		};
		/*
			@getOrders rleoads the order controller according too the filter to get the new filtered data.
		*/
		this.getDgs = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('deliveryguy')
	.controller('dgListCntrl', [
		'$state',
		'$mdSidenav',
		'$stateParams',
		'dgs',
		'constants',
		'DeliveryGuy',
		dgListCntrl 
	]);
})();
(function(){
	'use strict';
	/*
		dgCreateCntrl is the controller for the delivery guy create page. 
		Its resolved only after loading all the operation manager and team leads.
			
	*/
	var dgCreateCntrl = function ($state,$mdSidenav,dgConstants,DeliveryGuy,leadUserList,PreviousState){
		var self = this;
		/*
			@shift_timings,@transportation_mode : 
			is the list of all the available shift timings and transportation modes for creating dg,
			this is currently static as constant data in constants/constants.js
		*/
		self.shift_timings = dgConstants.shift_timings;
		self.transportation_mode = dgConstants.transportation_mode;
		/*
			@OpsManagers: resolved operation manager list.
			@TeamLeads  : resolved team leads list.
		*/
		self.OpsManagers = leadUserList.OpsManager.payload.data;
		self.TeamLeads   = leadUserList.TeamLead.payload.data;
		/*
			@dg: is a instance of delliveryguy.dg resource for saving the dg data a with ease
		*/
		self.dg = new DeliveryGuy.dg();
		/*
			function to redirect back to the previous page or parent page.
		*/
		self.goBack =function(){
			if(PreviousState.isAvailable()){
				PreviousState.redirectToPrevious();
			}
			else{
				$state.go('home.dgList');
			}
		};
		/*
			create : A function for creation delivery guys and using angular resource.
			It redirects to list view on succesfull creation of dg or handle's error on creation.
		*/
		self.create = function(){
			self.dg.shift_timing = angular.fromJson(self.dg.shift_timing);
			self.dg.$save(function(){
				self.goBack();
			});
		};
	};

	angular.module('deliveryguy')
	.controller('dgCreateCntrl', [
		'$state',
		'$mdSidenav', 
		'dgConstants',
		'DeliveryGuy',
		'leadUserList',
		'PreviousState',
		dgCreateCntrl
	]);
})();
(function(){
	'use strict';

	var dgDetailCntrl = function($state,$stateParams,$mdDialog,$mdMedia,DeliveryGuy,dgConstants,leadUserList,DG,PreviousState){
		var self = this;
		self.params = $stateParams;
		self.DG = DG.payload.data;
		self.attendance_date = moment().date(1).toDate();
		self.attendanceMinDate = moment('2015-01-01').toDate();
		self.attendanceMaxDate = moment().toDate();
		self.OpsManagers = leadUserList.OpsManager.payload.data;
		self.TeamLeads   = leadUserList.TeamLead.payload.data;
		self.showEditDialog = function(){
			var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'));
			$mdDialog.show({
				controller         : ('EditDgCntrl',['$mdDialog','dgConstants','DG','OpsManagers','TeamLeads',EditDgCntrl]),
				controllerAs       : 'dgEdit',
				templateUrl        : '/static/modules/deliveryguy/dialogs/edit.html',
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				fullscreen         : useFullScreen,
				openFrom           : '#dgEditDialog',
				closeTo            : '#dgEditDialog',
				locals             : {
					            DG : self.DG,
					   OpsManagers : self.OpsManagers,
				   		 TeamLeads : self.TeamLeads
				},
			})
			.then(function(dg) {
				dg.shift_time = angular.fromJson(dg.shift_time);
				DeliveryGuy.dg.$update(dg,function(response){
					self.getDgDetails();
				});
			}, function() {
				self.status = 'You cancelled the dialog.';
			});
		};
		/*
			function to redirect back to the previous page or parent page.
		*/
		self.goBack = function(){
			if(PreviousState.isAvailable()){
				PreviousState.redirectToPrevious();
			}
			else{
				$state.go('home.dgList');
			}
		};

		self.onlyMonthsPredicate = function(date) {
			var day = moment(date).date();
			return day === 1;
		};
		self.getTeamMembers = function(){
			DeliveryGuy.dg.associated_dgs({id:self.DG.id},function(response){
				self.associated_dg_list = response.payload.data;
			});
		};
		self.toTeamlead = function(){
			$mdDialog.show({
				controller         : ('AddTeamLeadCntrl',['$mdDialog','DG','DeliveryGuy',AddTeamLeadCntrl]),
				controllerAs       : 'dgTeamLead',
				templateUrl        : '/static/modules/deliveryguy/dialogs/teamlead.html',
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				fullscreen         : true,
				locals             : {
					DG : self.DG,
				},
			})
			.then(function(data) {
				if(self.DG.is_teamlead){
					DeliveryGuy.dg.$update(data,function(response){
						self.getDgDetails();
					});
				}
				else{
					DeliveryGuy.dg.promoteToTL(data,function(response){
						self.getDgDetails();
					});
				}
			}, function() {
				self.status = 'You cancelled the dialog.';
			});
		};

		self.getAttendance = function(){
			var attendance_params = {
				id    : self.DG.id,
				month : moment(self.attendance_date).month() + 1,
				year  : moment(self.attendance_date).year()
			};
			DeliveryGuy.dg.attendance(attendance_params,function(response){
				self.dg_monthly_attendance = response.payload.data.attendance;
			});
		};

		self.getDgDetails = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	function EditDgCntrl($mdDialog,dgConstants,DG,OpsManagers,TeamLeads){
		var dgEdit = this;
		dgEdit.DG = DG;
		dgEdit.DG.team_lead_dg_ids   = [];
		dgEdit.DG.ops_manager_ids = [];
		dgEdit.DG.team_leads.forEach(function(lead){
			if(lead.dg_id){
				dgEdit.DG.team_lead_dg_ids.push(lead.dg_id);
			}
		});		
		dgEdit.DG.ops_managers.forEach(function(ops){
			dgEdit.DG.ops_manager_ids.push(ops.employee_id);
		});	
		dgEdit.OpsManagers = OpsManagers;
		dgEdit.TeamLeads = TeamLeads;
		dgEdit.shift_timings = dgConstants.shift_timings;
		dgEdit.transportation_mode = dgConstants.transportation_mode;

		dgEdit.cancel = function() {
			$mdDialog.cancel();
		};
		dgEdit.answer = function(answer) {
			$mdDialog.hide(answer);
		};
	}

	function AddTeamLeadCntrl($mdDialog,DG,DeliveryGuy){
		var dgTeamLead = this;
		dgTeamLead.DG = DG;
		dgTeamLead.selectedTeamMembers = [];
		dgTeamLead.selectedPincodes = [];
		dgTeamLead.teamLeadData = {
			id: DG.id,
			pincodes : [],
			associate_dgs : []
		};

		dgTeamLead.cancel = function() {
			$mdDialog.cancel();
		};

		DeliveryGuy.dgServicablePincodes.query().$promise.then(function (response){
				dgTeamLead.pincodes =  response.payload.data;
		});

		dgTeamLead.addTeamDgs = function(chip){
			dgTeamLead.teamLeadData.associate_dgs.push(chip.id);
		};
		dgTeamLead.removeTeamDgs = function(chip){
			var index = dgTeamLead.teamLeadData.associate_dgs.indexOf(chip.id);
			dgTeamLead.teamLeadData.associate_dgs.splice(index,1);
		};
		dgTeamLead.addTlPincode = function(chip){
			dgTeamLead.teamLeadData.pincodes.push(chip.pincode);
		};
		dgTeamLead.removeTlPincode = function(chip){
			var index = dgTeamLead.teamLeadData.pincodes.indexOf(chip.pincode);
			dgTeamLead.teamLeadData.pincodes.splice(index,1);
		};

		dgTeamLead.dgSearch = function(text){
			var search = {
				search : text
			};
			return DeliveryGuy.dgPageQuery.query(search).$promise.then(function (response){
				return response.payload.data.data;
			});
		};

		dgTeamLead.transformChip = function(chip) {
			// If it is an object, it's already a known chip
			if (angular.isObject(chip)) {
				return {name: chip.name, phone_number: chip.phone_number,id: chip.id};
			}
		};

		dgTeamLead.transformPinChip = function(chip) {
			// If it is an object, it's already a known chip
			if (angular.isObject(chip)) {
				return chip;
			}
		};

		dgTeamLead.submitTlData = function(){
			$mdDialog.hide(dgTeamLead.teamLeadData);
		};
	}

	angular.module('deliveryguy')
	.controller('dgDetailCntrl', [
		'$state',
		'$stateParams',
		'$mdDialog',
		'$mdMedia',
		'DeliveryGuy',
		'dgConstants',
		'leadUserList',
		'DG',
		'PreviousState',
		dgDetailCntrl
	]);
})();
(function(){
	'use strict';
	angular.module('vendor', [])
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.vendorList',{
			url: "^/vendor/list?date&search&page",
			templateUrl: "/static/modules/vendor/list/list.html",
			controllerAs : 'vendorList',
    		controller: "vendorListCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER,constants.userRole.ACCOUNTS,constants.userRole.HR];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    			vendors: ['Vendor','$stateParams', function (Vendor,$stateParams){
    						$stateParams.date = ($stateParams.date !== undefined) ? new Date($stateParams.date).toISOString() : new Date().toISOString();
    						$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    						return Vendor.query($stateParams).$promise;
    					}]
    		}
		});
	}]);
})();
(function(){
	'use strict';
	var vendorListCntrl = function($state,$mdSidenav,$stateParams,vendors){
		var self = this;
		self.params = $stateParams;
		this.searchVendorActive = (this.params.search !== undefined) ? true : false;
		/*
			@vendors: resolved vendors list accordign to the url prameters.
		*/
		self.vendors = vendors.payload.data.data;
		self.total_pages = vendors.payload.data.total_pages;
		self.total_vendors = vendors.payload.data.total_vendor_count;
		/*
			@paginate is a function to paginate to the next and previous page of the delivery guy list
		*/
		self.paginate = {
			nextpage : function(){
				self.params.page = self.params.page + 1;
				self.getVendors();
			},
			previouspage : function(){
				self.params.page = self.params.page - 1;
				self.getVendors();
			}
		};

		/*
			@backFromSearch is a function to revert back from a searched delivery guy name to complete list view of delivery guys
		*/ 
		self.backFromSearch = function(){
			self.params.search = undefined;
			self.searchVendorActive = false;
			self.getVendors();
			
		};
		/*
			@getOrders rleoads the order controller according too the filter to get the new filtered data.
		*/
		self.getVendors = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('vendor')
	.controller('vendorListCntrl', [
		'$state',
		'$mdSidenav',
		'$stateParams',
		'vendors',
		vendorListCntrl
	]);
})();