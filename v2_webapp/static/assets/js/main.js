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
			// $state.go('home.opsorder');
		}
		else if(vendorClients.$hasRole(constants.userRole.VENDOR)){
			this.vendor = true;
			// $state.go('home.order');
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
		'deliveryguy',
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
  			'default' : '700'
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
		userRole  : { ADMIN : 'operations', VENDOR : 'vendor'},
		status    : STATUS_OBJECT,
		time      :time_data,
		dg_status : dg_checkin_status
	};
	var prodConstants = {
		v1baseUrl : 'http://yourguy.herokuapp.com/api/v1/',
		v2baseUrl : 'http://yourguy.herokuapp.com/api/v2/',
		v3baseUrl : 'http://yourguy.herokuapp.com/api/v3/',
		userRole  : { ADMIN : 'operations', VENDOR : 'vendor'},
		status    : STATUS_OBJECT,
		time      : time_data,
		dg_status : dg_checkin_status
	};
	var testConstants = {
		v1baseUrl : 'https://yourguytestserver.herokuapp.com/api/v1/',
		v2baseUrl : 'https://yourguytestserver.herokuapp.com/api/v2/',
		v3baseUrl : 'https://yourguytestserver.herokuapp.com/api/v3/',
		userRole  : { ADMIN : 'operations', VENDOR: 'vendor'},
		status    : STATUS_OBJECT,
		time      : time_data,
		dg_status : dg_checkin_status
	};

	angular.module('ygVendorApp')
	.constant('constants', testConstants);
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
	var DeliverGuy = function ($resource,constants){
		return {
			dg : $resource(constants.v3baseUrl+'deliveryguy/:id',{id:"@id"},{
				query :{
					method: 'GET',
					isArray: true
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
				if($rootScope.previousState){
					return true;
				}
				else{
					return false;
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
						'<p ng-if="pending">Pending: {{pending}} </p>',
						'<p ng-if="unassigned">Unassigned: {{unassigned}} </p>',
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
	var opsOrderCntrl = function ($state,$mdSidenav,$stateParams,vendorClients,DeliverGuy,orders,constants,orderSelection){
		/*
			 Variable definations
		*/
		var self = this;
		this.params = $stateParams;
		this.statusArray = ($stateParams.dg === undefined) ? [] : $stateParams.dg.split(',');
		this.params.date = new Date(this.params.date);
		this.vendor_list = vendorClients.vendors;
		/*
			 scope Orders variable assignments are done from this section for the controller
		*/
		this.orders = orders.data;
		this.orderFrom = ( ( ( this.params.page -1 ) * 50 ) + 1 );
		this.orderTo  = (this.orderFrom-1) + orders.data.length;
		this.total_pages = orders.total_pages;
		this.total_orders = orders.total_orders;
		this.pending_orders_count = orders.pending_orders_count;
		this.unassigned_orders_count = orders.unassigned_orders_count;
		/*
			@ status_list: scope order status for eg: 'INTRANSIT' ,'DELIVERED' variable assignments.
			@ time_list: scope order time for time filer variable assignments.
		*/
		this.status_list = constants.status;
		this.time_list = constants.time;
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
		/*
			@dgSearchTextChange is a function for Delivery guy search for filter. When ever the filtered dg change, 
			this function is called.

			@selectedDgChange is a callback function after delivery guy selection in the filter.
		*/
		this.dgSearchTextChange = function(text){
			var search = {
				search : text
			};
			return DeliverGuy.dgPageQuery.query(search).$promise.then(function (response){
				return response.data;
			});
		};
		this.selectedDgChange = function(dg){
			if(dg){
				self.params.dg = dg.phone_number;
			}
			else{
				self.params.dg = undefined;
			}
			self.getOrders();
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
			@getOrders rleoads the order controller according too the filter to get the new filtered data.
		*/
		this.getOrders = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	var vendorOrderCntrl = function ($state){
		console.log("vendor");
	};

	angular.module('order', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home.opsorder', {
			url: "^/all-orders?date&vendor&dg&status&page",
			templateUrl: "/static/modules/order/opsOrders.html",
			controllerAs : 'opsOrder',
    		controller: "opsOrderCntrl",
    		resolve: {
    			vendorClients : 'vendorClients',
    			DeliveryGuy : 'DeliveryGuy',
    			access: ["Access","constants", function (Access,constants) { 
    						return Access.hasRole(constants.userRole.ADMIN); 
    					}],
    			orders: ['Order','$stateParams', function (Order,$stateParams){
    						$stateParams.date = ($stateParams.date !== undefined) ? new Date($stateParams.date).toISOString() : new Date().toISOString();
    						$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    						return Order.getOrders.query($stateParams).$promise;
    					}],
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
		'$stateParams',
		'vendorClients',
		'DeliveryGuy',
		'orders',
		'constants',
		'orderSelection',
		opsOrderCntrl
	])
	.controller('vendorOrderCntrl', [
		'$state',
		vendorOrderCntrl
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
	angular.module('deliveryguy', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home.dgList', {
			url: "^/deliveryguy/list?date&attendance&search&page",
			templateUrl: "/static/modules/deliveryguy/list/list.html",
			controllerAs : 'dgList',
    		controller: "dgListCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
    						return Access.hasRole(constants.userRole.ADMIN); 
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
    						return Access.hasRole(constants.userRole.ADMIN); 
    					}],
    			leadUserList : ['DeliveryGuy','$q', function (DeliveryGuy,$q){
		    				return $q.all ({
		    					TeamLead : DeliveryGuy.dgTeamLeadQuery.query().$promise,
		    					OpsManager : DeliveryGuy.dgOpsManagerQuery.query().$promise
		    				});
    					}],
    		}
		});
		// .state('home.dgDetail', {
		// 	url: "^/deliveryguy/detail",
		// 	templateUrl: "/static/modules/deliveryguy/detail/detail.html",
		// 	controllerAs : 'dgList',
		//  controller: "dgListCntrl",
		// });
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
				start_time : '06:00',
				end_time   : '15:-1'
			},
			{
				start_time : '07:00',
				end_time   : '16:00'
			},
			{
				start_time : '09:00',
				end_time   : '18:00'
			},
			{
				start_time : '10:00',
				end_time   : '19:00'
			},
			{
				start_time : '10:30',
				end_time   : '19:30'
			},
			{
				start_time : '11:00',
				end_time   : '20:00'
			},
			{
				start_time : '13:00',
				end_time   : '22:00'
			},
			{
				start_time : '14:00',
				end_time   : '23:00'
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
	var dgListCntrl = function($state,$mdSidenav,$stateParams,dgs,constants){
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
		dgListCntrl 
	]);
})();
(function(){
	'use strict';
	/*
		dgCreateCntrl is the controller for the delivery guy create page. 
		Its resolved only after loading all the operation manager and team leads.
			
	*/
	var dgCreateCntrl = function ($mdSidenav,$stateParams,dgConstants,DeliveryGuy,leadUserList,PreviousState){
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
			if(PreviousState.isAvailable){
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
		'$mdSidenav', 
		'$stateParams',
		'dgConstants',
		'DeliveryGuy',
		'leadUserList',
		'PreviousState',
		dgCreateCntrl
	]);
})();