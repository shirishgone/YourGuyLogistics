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
					else if(user.role === constants.userRole.ACCOUNTS){
						$state.go('home.cod.deposit');
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
	var homeCntrl = function($rootScope,$state,$mdSidenav,$mdDialog,$mdToast,$interval,constants,UserProfile,Notification,Notice){
		// Show tabs page accorfing to the credentials.
		AWS.config.update({accessKeyId: constants.ACCESS_KEY, secretAccessKey: constants.SECRET_KEY});
		var self = this;
		this.tabs =  constants.permissible_tabs[UserProfile.$getUserRole()];
		this.user_name = UserProfile.$getUsername();
		/*
			create a function for alasql library for converting iso date string into a human readable date string.
		*/
		alasql.fn.IsoToDate = function(n){
			return moment(n).format('DD-MM-YYYY');
		};
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
			},function(){
				self.toggleSideNav();
			});
		};
		/*
			@showLogoutDialog: function to show the confirmation dialog box when logout button is clicked.
		*/
		this.getNoticeCount = function(){
			Notice.pendingNotificationCount.get(function(resp){
				if(self.count!== undefined && self.count != resp.payload.data){
					$rootScope.$broadcast('notificationUpdated');
				}
				self.count = resp.payload.data;
			});
		};
		if(UserProfile.$getUserRole() === constants.userRole.OPS || UserProfile.$getUserRole() === constants.userRole.OPS_MANAGER){
				self.getNoticeCount();
		}

		$interval(function(){
			if(UserProfile.$getUserRole() === constants.userRole.OPS || UserProfile.$getUserRole() === constants.userRole.OPS_MANAGER){
				self.getNoticeCount();
			}
		}, 120000);
		/*
			event for handleing error cases, whenever the error event is fired this, function is called
			and it shows a toast with a error messgae for small duration and then it disappeares.
		*/
		$rootScope.$on('errorOccured', function(){
			Notification.loaderComplete();
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
		/*
			event for handleing success cases, whenever the succes event is fired this, function is called
			and it shows a toast with a success messgae for small duration and then it disappeares.
		*/
		$rootScope.$on('eventSuccess', function(){
			Notification.loaderComplete();
			if($rootScope.successMessage){
				$mdToast.show({
					controller: 'SuccessToastCntrl',
					controllerAs : 'successToast',
					templateUrl: '/static/modules/home/success-toast-template.html',
					hideDelay: 5000,
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
		'$interval',
		'constants',
		'UserProfile',
		'Notification',
		'Notice',
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
	])
	.controller('SuccessToastCntrl', [
		'$mdToast',
		'$rootScope', 
		function($mdToast,$rootScope){
			this.msg = $rootScope.successMessage;

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
    'reports',
    'Cod',
    'feedback',
    'notification',
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
			order           : true,
			createOrder     : false,
			assignOrder     : true,
			updateOrder     : true,
			dg              : true,
			dgEdit          : false,
			dgCreate        : false,
			dgPromteTeamLead: false,
			vendor          : true,
			reports         : true,
			COD             : false,
			customer        : false,
			products        : false,
			feedback        : true,
			tutorial        : false,
			notification    : true
		},
		vendor: {
			order           :true,
			createOrder     :true,
			assignOrder     :false,
			updateOrder     :false,
			dg              :false,
			dgEdit          :false,
			dgCreate        :false,
			dgPromteTeamLead:false,
			vendor          :false,
			reports         :true,
			COD             :false,
			customer        :true,
			products        :true,
			feedback        :true,
			tutorial        :true,
			notification    :false
		},
		hr:{
			order           :false,
			createOrder     :false,
			assignOrder     :false,
			updateOrder     :false,
			dg              :true,
			dgEdit          :true,
			dgCreate        :true,
			dgPromteTeamLead:true,
			vendor          :false,
			reports         :false,
			COD             :false,
			customer        :false,
			products        :false,
			feedback        :false,
			tutorial        :false,
			notification    :false
		},
		operations_manager:{
			order           :true,
			createOrder     : false,
			assignOrder     : true,
			updateOrder     : true,
			dg              : true,
			dgEdit          : false,
			dgCreate        : false,
			dgPromteTeamLead: false,
			vendor          : true,
			reports         : true,
			COD             : false,
			customer        : false,
			products        : false,
			feedback        : true,
			tutorial        : false,
			notification    : true
		},
		accounts: {
			order           : false,
			createOrder     : false,
			assignOrder     : false,
			updateOrder     : false,
			dg              : false,
			dgEdit          : false,
			dgCreate        : false,
			dgPromteTeamLead: false,
			vendor          : false,
			reports         : false,
			COD             : true,
			customer        : false,
			products        : false,
			feedback        : false,
			tutorial        : false,
			notification    : false
		},
		sales : {
			order           : true,
			createOrder     : false,
			assignOrder     : false,
			updateOrder     : false,
			dg              : true,
			dgEdit          : false,
			dgCreate        : false,
			dgPromteTeamLead: false,
			vendor          : true,
			reports         : true,
			COD             : false,
			customer        : false,
			products        : false,
			feedback        : true,
			tutorial        : false,
			notification    : false
		},
		sales_manager : {
			order           : true,
			createOrder     : false,
			assignOrder     : false,
			updateOrder     : false,
			dg              : true,
			dgEdit          : false,
			dgCreate        : false,
			dgPromteTeamLead: false,
			vendor          : true,
			reports         : true,
			COD             : false,
			customer        : false,
			products        : false,
			feedback        : true,
			tutorial        : false,
			notification    : true
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
		permissible_tabs: permissible_tabs,
		ACCESS_KEY : 'AKIAJTRSKA2PKKWFL5PA',
	    SECRET_KEY : 'grJpBB1CcH8ShN6g88acAkDjvklYdgX7OENAx4g/',
	    S3_BUCKET : 'yourguy-pod'
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
		permissible_tabs : permissible_tabs,
		ACCESS_KEY : 'AKIAJTRSKA2PKKWFL5PA',
	    SECRET_KEY : 'grJpBB1CcH8ShN6g88acAkDjvklYdgX7OENAx4g/',
	    S3_BUCKET : 'yourguy-pod'
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
		permissible_tabs: permissible_tabs,
		ACCESS_KEY : 'AKIAJTRSKA2PKKWFL5PA',
	    SECRET_KEY : 'grJpBB1CcH8ShN6g88acAkDjvklYdgX7OENAx4g/',
	    S3_BUCKET  : 'yourguy-pod-test'
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
	var COD = function($resource,constants){
		return {
			getDeposits : $resource(constants.v3baseUrl+'cod/bank_deposits_list/'),
			verifyDeposits : $resource(constants.v3baseUrl+'cod/verify_bank_deposit/',{},{
				update :{
					method: 'PUT'
				},
			}),
			getVerifiedDeposits : $resource(constants.v3baseUrl+'cod/verified_bank_deposits_list/'),
			tranferToClient : $resource(constants.v3baseUrl+'cod/transfer_to_client/',{},{
				send :{
					method: 'POST'
				},
			}),
			transactionHistory: $resource(constants.v3baseUrl+'cod/vendor_transaction_history/')
		};
	};
	angular.module('ygVendorApp')
	.factory('COD', [
		'$resource',
		'constants', 
		COD
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
				},
				deactivate : {
					url : constants.v3baseUrl+'deliveryguy/:id'+'/deactivate/',
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
					isArray : false,
					cache: true
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
	var Feedback = function($resource,constants){
		return {
			getGroups : $resource(constants.v3baseUrl+'freshdesk/groups/',{}, {
				query : {
					method : 'GET',
					cache : true
				}
			}),
			getTicketsById : $resource(constants.v3baseUrl+'freshdesk/get_ticket/'),
			getTickets : $resource(constants.v3baseUrl+'freshdesk/all_tickets/',{},{
				query :{
					method: 'GET',
				}
			}),
			addNotes : $resource(constants.v3baseUrl+'freshdesk/add_note/',{},{
				update :{
					method: 'POST',
				}
			}),
			resolve : $resource(constants.v3baseUrl+'freshdesk/resolve/',{},{
				update :{
					method: 'PUT',
				}
			}),
		};
	};
	angular.module('ygVendorApp')
	.factory('Feedback', [
		'$resource',
		'constants',
		Feedback
	]);

})();
(function(){
	'use strict';
	var Notice = function ($resource,constants){
		return {
			getNotifications : $resource(constants.v3baseUrl+'notification/',{},{
				query :{
					method: 'GET',
				}
			}),
			pendingNotificationCount :$resource(constants.v3baseUrl+'notification/pending/'),
			markAsRead : $resource(constants.v3baseUrl+'notification/:id/read/',{id:'@id'},{
				update :{
					method: 'POST',
				}
			}),
		};
	};
	
	angular.module('ygVendorApp')
	.factory('Notice', [
		'$resource',
		'constants', 
		Notice
	]);
})();
(function(){
	'use strict';
	var Notification = function($rootScope,$state,$document){
		return {
			loaderStart : function(){
				angular.element($document[0].getElementsByClassName('request-loader')).removeClass('request-loader-hidden');
			},
			loaderComplete : function(){
				angular.element($document[0].getElementsByClassName('request-loader')).addClass('request-loader-hidden');
			},
			showError : function(msg){
				$rootScope.errorMessage = msg;
				$rootScope.$broadcast('errorOccured');
			},
			showSuccess : function(msg){
				$rootScope.successMessage = msg;
				$rootScope.$broadcast('eventSuccess');
			}
		};
	};
	angular.module('ygVendorApp')
	.factory('Notification', [
		'$rootScope',
		'$state',
		'$document',
		Notification
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
			}),
			updatePickupAttempted : $resource(constants.v3baseUrl+'order/:id/pickup_attempted/',{id:"@id"},{
				update : {
					method: 'PUT'
				}
			}),
			updateDeliveryAttempted : $resource(constants.v3baseUrl+'order/:id/delivery_attempted/',{id:"@id"},{
				update : {
					method: 'PUT'
				}
			}),
			editCODAmount : $resource(constants.v3baseUrl+'order/:id/update_cod/',{id:"@id"},{
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
	var Reports = function($resource,constants){
		return {
			getReport : $resource(constants.v3baseUrl+"dashboard_stats/", {} , {
				stats : {
					method: 'GET'
				}
			}),
			reportsExcel : $resource(constants.v3baseUrl+"excel_download/")

		};
	};
	angular.module('ygVendorApp')
	.factory('Reports', [
		'$resource', 
		'constants',
		Reports
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

	var stateChangeHandler = function ($rootScope, Access, $state,$document,constants){
		$rootScope.$on("$stateChangeError",function (event, toState, toParams, fromState, fromParams, error){
			console.log(error);
			angular.element($document[0].getElementsByClassName('request-loader')).addClass('request-loader-hidden');
			if (error == Access.UNAUTHORIZED) {
				$state.go("login");
			} else if (error == Access.FORBIDDEN) {
				$state.go("forbidden");
			}
		});
		$rootScope.$on("$stateChangeStart",function (event, toState, toParams, fromState, fromParams){
			angular.element($document[0].getElementsByClassName('request-loader')).removeClass('request-loader-hidden');
			// var toProps = Object.getOwnPropertyNames(toParams);
   // 			var fromProps = Object.getOwnPropertyNames(fromParams);
   // 			if(fromState.name === toState.name && toParams.hasOwnProperty('page')){
   // 				for( var key in toParams){
   // 					if(key !== 'page' && key !== 'date') {
   // 						console.log(typeof toParams[key]+"-->"+key);
   // 						// console.log(toParams.pincodes);
   // 						if(toParams[key] !== fromParams[key]){
   // 							console.log(key);
   // 							console.log(toParams);
   // 							console.log(fromParams);
   // 							toParams.page = 1;
   // 							return;
   // 						}
   // 					}
   // 				}
   // 			}
			if (toState.redirectTo) {
				event.preventDefault();
				$state.go(toState.redirectTo, toParams);
			}
			else if(toState.name === 'home') {
				Access.hasAnyRole([constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER])
				.then(function(response){
					$state.go('home.opsorder');
				},function(error){
					Access.hasRole(constants.userRole.HR)
					.then(function(response){
						$state.go('home.dgList');
					},function(error){
						Access.hasRole(constants.userRole.ACCOUNTS)
						.then(function(response){
							$state.go('home.cod.deposit');
						},function(error){
							Access.hasRole(constants.userRole.VENDOR)
							.then(function(response){
								$state.go('forbidden');
							},function(error){
								$state.go('forbidden');
							});
						});
					});
				});
			}
		});
		$rootScope.$on("$stateChangeSuccess",function (event, toState, toParams, fromState, fromParams){
			if(toState.name != fromState.name){
				$rootScope.previousState = {
					state : fromState.name,
					params : fromParams
				};
			}
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
		'constants',
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
				'<div class="ydPagination md-whiteframe-z2" layout="row" layout-align="start center">',
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
			url: "^/all-orders?date&vendor_id&dg_username&order_status&page&start_time&end_time&is_cod&search&delivery_ids&pincodes&is_retail&vendor_name&dg_name",
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
						    $stateParams.is_cod = ($stateParams.is_cod == 'true')? Boolean($stateParams.is_cod): undefined;
						    $stateParams.is_retail = ($stateParams.is_retail == 'true')? Boolean($stateParams.is_retail): undefined;

						    if(Array.isArray($stateParams.order_status)){
    							$stateParams.order_status = ($stateParams.order_status.length > 0) ? $stateParams.order_status.toString(): undefined;
    						}
    						
    						if(Array.isArray($stateParams.pincodes)){
    							$stateParams.pincodes = ($stateParams.pincodes.length > 0) ? $stateParams.pincodes.toString(): undefined;
    						}
    						return Order.getOrders.query($stateParams).$promise;
    					}],
    			Pincodes: ['DeliveryGuy',function(DeliveryGuy){
    						return DeliveryGuy.dgServicablePincodes.query().$promise;
    					}]
    		}
		})
        .state('home.orderDetail', {
            url: "^/order/detail/:id",
            templateUrl: "/static/modules/order/detail/detail.html",
            controllerAs : 'orderDetail',
            controller: "orderDetailCntrl",
            resolve: {
                access: ["Access","constants", function (Access,constants) { 
                            var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER,constants.userRole.VENDOR];
                            return Access.hasAnyRole(allowed_user); 
                        }],
                order: ['Order','$stateParams', function (Order,$stateParams){
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
	var codEdit = function($mdMedia,$mdDialog){
		return {
			openCodDialog : function(){
				return $mdDialog.show({
					controller         : ('EditCodCntrl',['$mdDialog',EditCodCntrl]),
					controllerAs       : 'editCod',
					templateUrl        : '/static/modules/order/dialogs/edit-cod.html?nd=' + Date.now(),
					parent             : angular.element(document.body),
					clickOutsideToClose: false,
					fullscreen         : false,
					openFrom           : '#options',
					closeTo            : '#options',
				});
			}

		};
	};
	/*
		@EditCodCntrl controller function for the edit cod for orders dialog
	*/
	function EditCodCntrl($mdDialog){
		var self = this;
		this.cod_object = {
		};

		this.cancel = function() {
			$mdDialog.cancel();
		};
		this.answer = function(answer){
			$mdDialog.hide(answer);
		};
	}

	angular.module('order')
	.factory('EditCod', [
		'$mdMedia',
		'$mdDialog',
		codEdit
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
		this.status_object = {
			data : {}
		};

		this.cancel = function() {
			$mdDialog.cancel();
		};
		this.answer = function(answer){
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
			 Check if any filter is applied or not to show no-content images
		*/
		var filterApplied = function(){
			if(self.params.order_status.length  !== 0 || 
				self.params.vendor_id   !== undefined || 
				self.params.dg_username !== undefined || 
				self.params.search      !== undefined || 
				self.params.end_time    !== undefined || 
				self.params.start_time  !== undefined || 
				self.params.is_retail   !== false     ||
				self.params.is_cod      !== false     || 
				self.params.pincodes    !== undefined){
				return true;
			}
			else{
				return false;
			}
		};
		/*
			 Variable definations for the route(Url)
		*/
		var self = this;
		this.params = $stateParams;
		this.params.order_status = ($stateParams.order_status)? $stateParams.order_status.split(','): [];
		this.params.pincodes     = ($stateParams.pincodes)    ? $stateParams.pincodes.split(','): [];
		this.params.date         = new Date(this.params.date);
		this.searchedDg          = this.params.dg_name;
		this.searchVendor        = this.params.vendor_name;
		this.searchOrderActive = (this.params.search !== undefined) ? true : false;
		/*
			 scope Orders variable assignments are done from this section for the controller
		*/
		this.orders = orders.payload.data.data;
		this.total_pages = orders.payload.data.total_pages;
		this.total_orders = orders.payload.data.total_orders;
		this.pending_orders_count = orders.payload.data.pending_orders_count;
		this.unassigned_orders_count = orders.payload.data.unassigned_orders_count;
		this.pincodes = Pincodes.payload.data;

		if(self.orders.length === 0 && filterApplied()){
			self.noContent = true;
		}
		else if(self.orders.length === 0 && !filterApplied()){
			self.noContent = true;
		}
		else{
			self.noContent = false;
		}
		/*
			@ status_list: scope order status for eg: 'INTRANSIT' ,'DELIVERED' variable assignments.
			@ time_list: scope order time for time filer variable assignments.
		*/
		this.status_list = constants.status;
		this.time_list = constants.time;
		/*
			@revertToPageOne is a function to revert back to first page if any kind of filter is applied
		*/ 
		this.revertToPageOne = function(){
			self.params.page = 1;
			self.getOrders();
		};
		/*
			@resetParams funcion to reset the filter.
		*/
		this.resetParams = function(){
			self.params = {};
			self.getOrders();
		};
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
				self.params.dg_name = dg.name;
			}
			else{
				self.params.dg_username = undefined;
				self.params.dg_name = undefined;
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
				self.params.vendor_name = vendor.name;
			}
			else{
				self.params.vendor_id = undefined;
				self.params.vendor_name = undefined;
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
				if(status_data.status == 'pickup'){
					self.updatePickupStatus(status_data);
				}
				else if(status_data.status == 'delivered'){
					self.updateDeliveryStatus(status_data);
				}
				else if(status_data.status == 'pickup_attempted'){
					self.updatePickupAttemtedStatus(status_data);
				}
				else if(status_data.status == 'delivery_attempted'){
					self.updateDeliveryAtemptedStatus(status_data);
				}
			});
		};

		this.statusUpdateDialog = function(){
			OrderStatusUpdate.openStatusDialog()
			.then(function(status_data) {
				status_data.delivery_ids = orderSelection.getAllItemsIds();
				if(status_data.status == 'pickup'){
					self.updatePickupStatus(status_data);
				}
				else if(status_data.status == 'delivered'){
					self.updateDeliveryStatus(status_data);
				}
				else if(status_data.status == 'pickup_attempted'){
					self.updatePickupAttemtedStatus(status_data);
				}
				else if(status_data.status == 'delivery_attempted'){
					self.updateDeliveryAtemptedStatus(status_data);
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
		self.updateDeliveryAtemptedStatus = function(status_data){
			var array = [];
			for(var i=0; i< status_data.delivery_ids.length;i++){
				status_data.data.id = status_data.delivery_ids[i];
				array.push(Order.updateDeliveryAttempted.update(status_data.data).$promise);
			}
			$q.all(array).then(function(data){
				orderSelection.clearAll();
				self.getOrders();
			});
		};
		self.updatePickupAttemtedStatus = function(status_data){
			var array = [];
			for(var i=0; i< status_data.delivery_ids.length;i++){
				status_data.data.id = status_data.delivery_ids[i];
				array.push(Order.updatePickupAttempted.update(status_data.data).$promise);
			}
			$q.all(array).then(function(data){
				orderSelection.clearAll();
				self.getOrders();
			});
		};
		this.revertOrSelect = function(order){
			if(orderSelection.isSelected()){
				self.handleOrdeSelection.toggle(order);
			}
			else{
				$state.go('home.orderDetail',{id:order.id});
			}
		};
		/*
			@getOrders rleoads the order controller according too the filter to get the new filtered data.
		*/
		this.getOrders = function(){
			if (!self.params.vendor_id) {
				self.params.vendor_name = undefined;
			}
			if (!self.params.dg_username) {
				self.params.dg_name = undefined;
			}
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
	var orderDetailCntrl = function($state,$stateParams,$rootScope,order,DeliveryGuy,Order,orderDgAssign,OrderStatusUpdate,EditCod,PreviousState,constants,$q,Notification){
		var s3 = new AWS.S3();
		var self = this;
		self.params = $stateParams;
		self.order = order.payload.data;

		function drawConvertedImage(bufferStr , name) {
			var image_proof = new Image();
			var ctxImageWidht;
			var ctxImageHeight;
			image_proof.src = "data:image/png;base64,"+ bufferStr;
			image_proof.onload = function(){
				var canvas = document.createElement('canvas');
				var context = canvas.getContext('2d');
				if(image_proof.width >= image_proof.height){
					ctxImageWidht = 1024;
					ctxImageHeight = 768;
				}
				else{
					ctxImageWidht = 768;
					ctxImageHeight = 1024;
				}
				context.canvas.width = ctxImageWidht;
				context.canvas.height = ctxImageHeight;
				context.drawImage(image_proof, 0,0 ,image_proof.width ,image_proof.height, 0, 0, ctxImageWidht ,ctxImageHeight);
				var link = document.createElement('a');
				var evt = document.createEvent("HTMLEvents");
				evt.initEvent("click");
				link.href = canvas.toDataURL();
				link.download = name+'.png';
				link.dispatchEvent(evt);
			};
		}
		function convertBinaryToImage (data){
			var deferred = $q.defer();
			var str = "", array = new Uint8Array(data.Body);
			for (var j = 0, len = array.length; j < len; j++) {
				str += String.fromCharCode(array[j]);
			}
			var base64string = window.btoa(str);
			if(base64string){
				deferred.resolve(base64string);
			}
			else {
				deferred.reject('error creating base64 data');
			}
			return deferred.promise;
		}
		function getS3Images (img , cb){
			s3.getObject({Bucket : constants.S3_BUCKET,Key: img.Key}, function (err, data){
				if(err){
					cb(err);
				}
				else{
					var base64ConvertedData = convertBinaryToImage(data);
					base64ConvertedData.then(function (bs64data){
						drawConvertedImage(bs64data,img.Key);
						cb();
					},function (err){
						cb(err);
					});
				}
			});
		}
		var _safari = function(){
			var isSafari = /Safari/.test(navigator.userAgent) && /Apple Computer/.test(navigator.vendor);
			if(isSafari){
				var test_popup = window.open('');
				if(test_popup === null || typeof(test_popup) === undefined){
					return true;
				}
				else{
					return false;
				}
			}
			else{
				return false;
			}
		};
		/*
			function to redirect back to the previous page or parent page.
		*/
		self.goBack = function(){
			if(PreviousState.isAvailable()){
				PreviousState.redirectToPrevious();
			}
			else{
				$state.go('home.opsorder');
			}
		};
		self.downloadPop = function(){ 
			var param = {
				Bucket : constants.S3_BUCKET,
				Prefix : self.params.id+'/'+self.order.pickup_datetime.slice(0,10)+'/pop'
			};
			self.download_image(param);
		};

		self.downloadPod = function(){ 
			var param = {
				Bucket : constants.S3_BUCKET,
				Prefix : self.params.id+'/'+self.order.pickup_datetime.slice(0,10)+'/pod'
			};
			self.download_image(param);
		};

		self.download_image = function(param){
			Notification.loaderStart();
			s3.listObjects(param, function (err, data){
				if(err){
					Notification.loaderComplete();
					Notification.showError(err);
				}
				else{
					if (data.Contents.length === 0) {
						Notification.loaderComplete();
						Notification.showError('No Proof Found');
						return;
					}
					if( _safari() ) {
						var msg = 'To view the proofs! \nOption 1: Go to Safari —> Preferences —> Security —>  Block popup windows (Disable)\nOption 2: Use Chrome browser to download the images';
						Notification.loaderComplete();
						Notification.showError(msg);
						return;
					}
					else{
						async.map( data.Contents , getS3Images , function(err, result) {
							if(err){
								Notification.loaderComplete();
								Notification.showError(err);
							}
							else {
								Notification.loaderComplete();
								Notification.showSuccess('Proof Download Successful');
							}
						});
        			}// end of else
      			} // end of else 
    		}); // end of listObject
		};
		/*
			@assignDgForSingleOrder is a function to open dg assignment dialog box and assign delivery guy and pickup guy for the 
			order once user confirms things.
		*/
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
			Notification.loaderStart();
			$q.all(array).then(function(data){
				self.getOrder();
			});
		};

		self.updatePickupStatus = function(status_data){
			var array = [];
			for(var i=0; i< status_data.delivery_ids.length;i++){
				status_data.data.id = status_data.delivery_ids[i];
				array.push(Order.updatePickup.update(status_data.data).$promise);
			}
			Notification.loaderStart();
			$q.all(array).then(function(data){
				self.getOrder();
			});
		};
		self.updateDeliveryStatus = function(status_data){
			var array = [];
			for(var i=0; i< status_data.delivery_ids.length;i++){
				status_data.data.id = status_data.delivery_ids[i];
				array.push(Order.updateDelivered.update(status_data.data).$promise);
			}
			Notification.loaderStart();
			$q.all(array).then(function(data){
				self.getOrder();
			});
		};
		self.updateDeliveryAtemptedStatus = function(status_data){
			var array = [];
			for(var i=0; i< status_data.delivery_ids.length;i++){
				status_data.data.id = status_data.delivery_ids[i];
				array.push(Order.updateDeliveryAttempted.update(status_data.data).$promise);
			}
			Notification.loaderStart();
			$q.all(array).then(function(data){
				self.getOrder();
			});
		};
		self.updatePickupAttemtedStatus = function(status_data){
			var array = [];
			for(var i=0; i< status_data.delivery_ids.length;i++){
				status_data.data.id = status_data.delivery_ids[i];
				array.push(Order.updatePickupAttempted.update(status_data.data).$promise);
			}
			Notification.loaderStart();
			$q.all(array).then(function(data){
				self.getOrder();
			});
		};
		self.statusUpdateDialog = function(order){
			OrderStatusUpdate.openStatusDialog()
			.then(function(status_data) {
				status_data.delivery_ids = [order.id];
				if(status_data.status == 'pickup'){
					self.updatePickupStatus(status_data);
				}
				else if(status_data.status == 'delivered'){
					self.updateDeliveryStatus(status_data);
				}
				else if(status_data.status == 'pickup_attempted'){
					self.updatePickupAttemtedStatus(status_data);
				}
				else if(status_data.status == 'delivery_attempted'){
					self.updateDeliveryAtemptedStatus(status_data);
				}
			});
		};
		/*
			@editCod is a function to allow the users to edit cod of the particular order.
		*/
		self.editCodDialog = function(order){
			EditCod.openCodDialog()
			.then(function(cod_data){
				Notification.loaderStart();
				cod_data.id = order.id;
				Order.editCODAmount.update(cod_data,function(response){
					Notification.showSuccess('COD amount updated successfully');
					self.getOrder();
				});
			});
		};
		/*
			@getOrder rleoads the order controller according too the filter to get the new filtered data.
		*/
		self.getOrder = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('order')
	.controller('orderDetailCntrl', [
		'$state',
		'$stateParams',
		'$rootScope',
		'order',
		'DeliveryGuy',
		'Order',
		'orderDgAssign',
		'OrderStatusUpdate',
		'EditCod',
		'PreviousState',
		'constants',
		'$q',
		'Notification',
		orderDetailCntrl
	]);

})();
(function(){
	'use strict';
	angular.module('deliveryguy', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home.dgList', {
			url: "^/deliveryguy/list?start_date&end_date&attendance&search&page",
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
    						var x,y;
	    					if(!$stateParams.start_date){
	    						x =  moment();
								x.startOf('day');
	    					}
	    					else{
	    						$stateParams.start_date = moment(new Date($stateParams.start_date));
	    						$stateParams.start_date.startOf('day');
	    					}
	    					if(!$stateParams.end_date){
	    						y =  moment();
								y.endOf('day');
	    					}
	    					else{
	    						$stateParams.end_date = moment(new Date($stateParams.end_date));
	    						$stateParams.end_date.endOf('day');
	    					}
    						$stateParams.start_date = ($stateParams.start_date !== undefined) ? $stateParams.start_date.toISOString() : x.toISOString();
    						$stateParams.end_date = ($stateParams.end_date !== undefined) ?  $stateParams.end_date.toISOString() : y.toISOString();
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
	var dgListCntrl = function($state,$mdSidenav,$stateParams,dgs,constants,DeliveryGuy,Notification){
		var self = this;
		this.params = $stateParams;
		this.params.start_date = new Date(this.params.start_date);
		this.params.end_date = new Date(this.params.end_date);
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
			@resetParams funcion to reset the filter.
		*/
		this.resetParams = function(){
			self.params = {};
			self.getDgs();
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
			@revertToPageOne is a function to revert back to first page if any kind of filter is applied
		*/ 
		this.revertToPageOne = function(){
			self.params.page = 1;
			self.getDgs();
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
			Notification.loaderStart();
			var attendance_params = {
				start_date : moment(self.params.start_date).startOf('day').toISOString(),
				end_date   : moment(self.params.end_date).endOf('day').toISOString()
			};
			// console.log(attendance_params);
			DeliveryGuy.dgsAttendance.query(attendance_params,function(response){
				alasql('SEARCH / AS @a UNION ALL(attendance / AS @b RETURN(@a.name AS Name , IsoToDate(@b.date) AS DATE, @b.worked_hrs AS Hours)) INTO XLSX("attendance.xlsx",{headers:true}) FROM ?',[response.payload.data]);
				// var str = 'SELECT name AS Name,IsoToDate(attendance -> 0 -> date) AS Date,attendance -> 0 -> worked_hrs AS Hours';
				// alasql( str+' INTO XLSX("attendance.xlsx",{headers:true}) FROM ?',[response.payload.data]);
				Notification.loaderComplete();
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
		'Notification',
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

	var dgDetailCntrl = function($state,$stateParams,$mdDialog,$mdMedia,DeliveryGuy,dgConstants,leadUserList,DG,PreviousState,Notification){
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
				templateUrl        : '/static/modules/deliveryguy/dialogs/edit.html?nd=' + Date.now(),
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
				Notification.loaderStart();
				dg.shift_time = angular.fromJson(dg.shift_time);
				DeliveryGuy.dg.$update(dg,function(response){
					self.getDgDetails();
					Notification.loaderComplete();
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
		/*
		*/
		self.deactivateDgDialog = function(){
			var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'));
			$mdDialog.show({
				controller         : ('DeactivateDgCntrl',['$mdDialog','DG',DeactivateDgCntrl]),
				controllerAs       : 'dgDeactivate',
				templateUrl        : '/static/modules/deliveryguy/dialogs/deactivate.html?nd=' + Date.now(),
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				fullscreen         : useFullScreen,
				locals             : {
					            DG : self.DG
				},
			})
			.then(function(dg) {
				Notification.loaderStart();
				DeliveryGuy.dg.deactivate(dg,function(response){
					Notification.loaderComplete();
					Notification.showSuccess('DG deactivated successfully');
					self.getDgDetails();
				});
			});
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
				templateUrl        : '/static/modules/deliveryguy/dialogs/teamlead.html?nd=' + Date.now(),
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				fullscreen         : true,
				locals             : {
					DG : self.DG,
				},
			})
			.then(function(data) {
				Notification.loaderStart();
				if(self.DG.is_teamlead){
					DeliveryGuy.dg.$update(data,function(response){
						Notification.loaderComplete();
						self.getDgDetails();
					});
				}
				else{
					DeliveryGuy.dg.promoteToTL(data,function(response){
						Notification.loaderComplete();
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
		dgEdit.DG = angular.copy(DG);
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

		dgEdit.findShiftTime = function(shift_time){
			return dgEdit.shift_timings.findIndex(function(shift){
				return shift.start_time == shift_time.start_time;
			});
		};
		dgEdit.DG.shift_time = dgEdit.shift_timings[dgEdit.findShiftTime(dgEdit.DG.shift_time)];
		console.log(dgEdit.DG.shift_time);

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

	function DeactivateDgCntrl($mdDialog,DG){
		var dgDeactivate = this;
		dgDeactivate.DG = DG;

		dgDeactivate.cancel = function() {
			$mdDialog.cancel();
		};

		dgDeactivate.answer = function(answer){
			answer.id = dgDeactivate.DG.id;
			$mdDialog.hide(answer);
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
		'Notification',
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
(function(){
	'use strict';
	var reportsCntrl = function($state,$stateParams,Reports,Vendor,report,Notification){
		var self = this;
		self.params = $stateParams;
		self.searchVendor  = self.params.vednor_name;
		this.searchVendorActive = (this.params.vendor_id !== undefined) ? true : false;
		self.report_stats = report.payload.data;

		self.params.start_date = new Date(self.params.start_date);
		self.params.end_date   = new Date(self.params.end_date);
		self.maxStartDate = moment().toDate();
		self.minStartDate = moment("2015-01-01").toDate();
		self.maxEndDate = moment(self.params.start_date).add(3 , 'months').toDate();

		/*
			@backFromSearch is a function to revert back from a searched vendor view to default view of reports
		*/ 
		this.backFromSearch = function(){
			self.params.vendor_id = undefined;
			self.params.vednor_name = undefined;
			self.searchVendorActive = false;
			self.getReports();
		};
		
		self.vendorSearchTextChange = function(text){
			var search = {
				search : text
			};
			return Vendor.query(search).$promise.then(function (response){
				if(self.params.vendor_id){
					response.payload.data.data.push({name:'All Vendors'});
				}
				return response.payload.data.data;
			});
		};
		self.selectedVendorChange = function(vendor){
			if(vendor.id){
				self.params.vendor_id = vendor.id;
				self.params.vednor_name = vendor.name;
			}
			else{
				self.params.vendor_id = undefined;
				self.params.vednor_name = undefined;
			}
			self.getReports();
		};
		self.manipulateGraph = function(){
			self.graphData = {
				chart : {
					plotGradientColor : " ",
					plotSpacePercent : "60",
					caption: "Order Details",
					xaxisname: "Dates",
					showalternatehgridcolor: "0",
					placevaluesinside: "1",
					toolTipSepChar : '=',
					showborder: "0",
					showvalues: "0",
					showplotborder: "0",
					showcanvasborder: "0",
					theme: "fint"
				},
				categories : [
					{
						category: []
					}
				],
				dataset : [
					{
						seriesname: "Total Delivered",
						color: "39B54A",
						data:[]
					},
					{
						seriesname: "Total Attempted",
						color: "00CCFF",
						data:[]
					},
					{
						seriesname: "Total Intransit",
						color: "FCC06A",
						data:[]
					},
					{
						seriesname: "Total Queued",
						color: "FE5E64",
						data:[]
					},
					{
						seriesname: "Total Cancelled",
						color: "A6A6A6",
						data:[]
					},
				]
			};
			for(var i =0; i < self.report_stats.orders.length;i++){
				self.graphData.categories[0].category[i] = {};
				self.graphData.categories[0].category[i].label = self.report_stats.orders[i].date.slice(8,10);
				self.graphData.dataset[0].data[i] = {
					value : self.report_stats.orders[i].delivered_count ,
					toolText : "Total Delivered:"+self.report_stats.orders[i].delivered_count+"{br} Total Placed:"+self.report_stats.orders[i].total_orders_count+"{br}"+new Date(self.report_stats.orders[i].date).toDateString()
				};
				self.graphData.dataset[1].data[i] = {
					value : self.report_stats.orders[i].delivery_attempted_count+self.report_stats.orders[i].pickup_attempted_count,
					toolText : "Total Attempted:"+(self.report_stats.orders[i].delivery_attempted_count+self.report_stats.orders[i].pickup_attempted_count)+"{br} Total Placed:"+self.report_stats.orders[i].total_orders_count+"{br}"+new Date(self.report_stats.orders[i].date).toDateString()
				};
				self.graphData.dataset[2].data[i] = {
					value    : self.report_stats.orders[i].intransit_count,
					toolText : "Total Intransit:"+self.report_stats.orders[i].intransit_count+"{br} Total Placed:"+self.report_stats.orders[i].total_orders_count+"{br}"+new Date(self.report_stats.orders[i].date).toDateString()
				};
				self.graphData.dataset[3].data[i] = {
					value    : self.report_stats.orders[i].queued_count,
					toolText : "Total Queued:"+self.report_stats.orders[i].queued_count+"{br} Total Placed:"+self.report_stats.orders[i].total_orders_count+"{br}"+new Date(self.report_stats.orders[i].date).toDateString()
				};
				self.graphData.dataset[4].data[i] = {
					value    : self.report_stats.orders[i].cancelled_count,
					toolText : "Total Cancelled:"+self.report_stats.orders[i].cancelled_count+"{br} Total Placed:"+self.report_stats.orders[i].total_orders_count+"{br}"+new Date(self.report_stats.orders[i].date).toDateString()
				};
			}
		};

		if(self.report_stats.total_orders !== 0){
			self.manipulateGraph();
		}

		self.date_change = function(){
			if( moment(self.params.end_date).diff(self.params.start_date,'months') > 3 ){
				self.params.end_date = moment(self.params.start_date).add(3, 'months').toDate();
			}
			if( moment(self.params.end_date).diff(self.params.start_date,'days') < 0 ){
				self.params.end_date = self.params.start_date;
			}
			self.getReports();
		};


		self.downloadReportExcel = function(){
			Notification.loaderStart();
			Reports.reportsExcel.get(self.params,function(response){
				alasql('SELECT * INTO XLSX("YG_REPORT.xlsx",{headers:true}) FROM ?',[response.payload.data]);
				Notification.loaderComplete();
			});
		};
		/*
			@getReports rleoads the order controller according too the filter to get the new filtered data.
		*/
		self.getReports = function(){
			Notification.loaderStart();
			if (!self.params.vendor_id) {
				self.params.vednor_name = undefined;
			}
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('reports', [
		'ng-fusioncharts'
	])
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.reports', {
			url: "^/reports?start_date&end_date&vendor_id&vednor_name",
			templateUrl  : "/static/modules/reports/reports.html",
			controllerAs : 'reports',
    		controller   : "reportsCntrl",
    		resolve: {
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER,constants.userRole.VENDOR];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    			report: ['Reports','$stateParams', function (Reports,$stateParams){
    						// var x = new Date();
    						// x.setHours(0);
    						// x.setMinutes(0);
    						// x.setSeconds(0);
    						// x.setDate(1);
    						var x,y;
	    					if(!$stateParams.start_date){
	    						x =  moment();
								x.startOf('day');
	    					}
	    					else{
	    						$stateParams.start_date = moment(new Date($stateParams.start_date));
	    						$stateParams.start_date.startOf('day');
	    					}
	    					if(!$stateParams.end_date){
	    						y =  moment();
								y.endOf('day');
	    					}
	    					else{
	    						$stateParams.end_date = moment(new Date($stateParams.end_date));
	    						$stateParams.end_date.endOf('day');
	    					}
    						$stateParams.start_date = ($stateParams.start_date !== undefined) ? $stateParams.start_date.toISOString() : x.toISOString();
    						$stateParams.end_date   = ($stateParams.end_date !== undefined) ? $stateParams.end_date.toISOString() : y.toISOString();
    						return Reports.getReport.stats($stateParams).$promise;
    					}]
    		}
		});
	}])
	.controller('reportsCntrl', [
		'$state',
		'$stateParams',
		'Reports',
		'Vendor',
		'report',
		'Notification',
		reportsCntrl 
	]);
})();
(function(){
	'use strict';
	var codCntrl = function($state,$stateParams,$mdSidenav){
		if($state.current.name == 'home.cod.deposit'){
			this.selectedIndex = 0;
		}
		else if($state.current.name == 'home.cod.transfer'){
			this.selectedIndex = 1;
		}
		else if($state.current.name == 'home.cod.history'){
			this.selectedIndex = 2;
		}
		else {
			this.selectedIndex = 0;
		}
		/*
			 @ toggleFilter : main sidenav toggle function, this function toggle the sidebar of the filets of the orders page page.
		*/
		this.toggleFilter = function(){
			$mdSidenav('cod-filter').toggle();
		};
		
	};

	angular.module('Cod', [])
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.cod',{
			url: "^/cod",
			templateUrl: "/static/modules/cod/cod.html",
			controllerAs : 'cod',
    		controller: "codCntrl",
   			redirectTo: 'home.cod.deposit',
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.ACCOUNTS];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    		}
		});
	}])
	.controller('codCntrl', [
		'$state',
		'$stateParams',
		'$mdSidenav',
		codCntrl
	]);
})();
(function(){
	'use strict';
	function VerifyDepositCntrl($mdDialog,deposit){
		var self = this;
		self.deposit = deposit;
		self.cancel = function() {
			$mdDialog.cancel();
		};
		self.answer = function(answer) {
			answer.is_accepted = true;
			$mdDialog.hide(answer);
		};
	}

	function DeclineDepositCntrl($mdDialog,deposit){
		var self = this;
		self.deposit = deposit;
		self.verifyAmount = function(data){
			if(!data || !data.pending_salary_deduction){
				return true;
			}
			else{
				if(parseFloat(data.pending_salary_deduction) > 0 && parseFloat(data.pending_salary_deduction) <= self.deposit.cod_amount){
					return false;
				}
				else {
					return true;
				}
			}
		};

		self.cancel = function() {
			$mdDialog.cancel();
		};
		self.answer = function(answer) {
			answer.pending_salary_deduction = parseFloat(answer.pending_salary_deduction);
			answer.is_accepted = false;
			answer.transaction_id = self.deposit.transaction_id;
			$mdDialog.hide(answer);
		};
	}

	var codDepositCntrl = function($state,$stateParams,$mdDialog,deposits,COD,Notification){
		// variable definations
		var self = this;
		self.params = $stateParams;
		self.deposits = deposits.payload.data.all_transactions;
		self.total_pages = deposits.payload.data.total_pages;
		self.total_deposits = deposits.payload.data.total_count;
		
		this.searchVendor = this.params.vendor_id;
		if(this.params.start_date){
			this.params.start_date = new Date(this.params.start_date);
		}
		if(this.params.end_date){
			this.params.end_date = new Date(this.params.end_date);
		}
		/*
			@showImage is a function to show the image of the deposit reciept which dg submits as a proof 
			of the cod amount deposited in the bank account.
		*/
		self.showImage = function(url){
			url = url.replace(/:/g,'%3A');
			var image_url = 'https://s3-ap-southeast-1.amazonaws.com/bank-deposit-test/'+url;
			self.showImageSection = true;
			self.depositImage = image_url;
		};
		/*
			@verifyDeposit function to open verify deposit popup and send a verify request to server.
		*/
		self.verifyDeposit = function(dp){
			$mdDialog.show({
				controller         : ('EditDgCntrl',['$mdDialog','deposit',VerifyDepositCntrl]),
				controllerAs       : 'verifyDeposit',
				templateUrl        : '/static/modules/cod/dialog/verify-deposit.html?nd=' + Date.now(),
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				locals             : {
					       deposit : dp,
				},
			})
			.then(function(dp) {
				Notification.loaderStart();
				COD.verifyDeposits.update(dp,function(response){
					Notification.showSuccess('Deposit Verified Successfully');
					Notification.loaderComplete();
					self.getDeposits();
				});
			});
		};
		/*
			@declineDeposit is a function to open decline deposit dialog and send a decline request to server.
		*/
		self.declineDeposit = function(dp){
			$mdDialog.show({
				controller         : ('EditDgCntrl',['$mdDialog','deposit',DeclineDepositCntrl]),
				controllerAs       : 'declineDeposit',
				templateUrl        : '/static/modules/cod/dialog/decline-deposit.html?nd=' + Date.now(),
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				locals             : {
					       deposit : dp,
				},
			})
			.then(function(data) {
				Notification.loaderStart();
				COD.verifyDeposits.update(data,function(response){
					Notification.loaderComplete();
					Notification.showSuccess('Deposit Declined Successfully');
					self.getDeposits();
				});
			});
		};
		/*
			@paginate is a function to paginate to the next and previous page 
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
			@vendorSearchTextChange is a function for vendor guy search for filter. When ever the filtered vendor change, 
			this function is called.

			@selectedVendorChange is a callback function after vendor guy selection in the filter.
		*/
		self.vendorSearchTextChange = function(text){
			var search = {
				search : text
			};
			return Vendor.query(search).$promise.then(function (response){
				return response.payload.data.data;
			});
		};

		self.selectedVendorChange = function(vendor){
			if(vendor){
				self.params.vendor_id = vendor.id;
			}
			else{
				self.params.vendor_id = undefined;
			}
		};
		/*
			@revertToPageOne is a function to revert back to first page if any kind of filter is applied
		*/ 
		this.revertToPageOne = function(){
			self.params.page = 1;
			self.getDeposits();
		};
		/*
			@resetParams funcion to reset the filter.
		*/
		self.resetParams = function(){
			self.params = {};
			self.getDeposits();
		};
		/*
			@getDeposits rleoads the cod controller according too the filter to get the new filtered data.
		*/
		this.getDeposits = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('Cod')
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.cod.deposit',{
			url: "^/cod/deposits?page&start_date&end_date&vendor_id",
			templateUrl: "/static/modules/cod/deposit/deposit.html",
			controllerAs : 'deposit',
    		controller: "codDepositCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
					var allowed_user = [constants.userRole.ACCOUNTS];
					return Access.hasAnyRole(allowed_user); 
    			}],
    			deposits : ['COD','$stateParams',function(COD,$stateParams){
    				$stateParams.start_date = ($stateParams.start_date !== undefined) ? new Date($stateParams.start_date).toISOString() : undefined;
    				$stateParams.end_date = ($stateParams.end_date !== undefined) ? new Date($stateParams.end_date).toISOString() : undefined;
    				$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    				return COD.getDeposits.get($stateParams).$promise;
    			}],
    		}
		});
	}])
	.controller('codDepositCntrl', [
		'$state',
		'$stateParams',
		'$mdDialog',
		'deposits',
		'COD',
		'Notification',
		codDepositCntrl
	]);
})();
(function(){
	'use strict';
	function TransferDepositCntrl($mdDialog,deposits){
		var self = this;
		self.total_cod_amount = 0;
		self.deposits = deposits;
		self.deposits.forEach(function(dp){
			self.total_cod_amount += dp.cod_amount;
		});
		self.cancel = function() {
			$mdDialog.cancel();
		};
		self.answer = function(answer) {
			$mdDialog.hide(answer);
		};
	}

	var codTransferCntrl = function($state,$stateParams,$mdDialog,varifiedDeposits,COD,Notification,Vendor){
		var self = this;
		self.params = $stateParams;
		self.varifiedDeposits = varifiedDeposits.payload.data.all_transactions;
		self.total_pages = varifiedDeposits.payload.data.total_pages;
		self.total_deposits = varifiedDeposits.payload.data.total_count;
		this.searchVendor = this.params.vendor_name;

		if(this.params.start_date){
			this.params.start_date = new Date(this.params.start_date);
		}
		if(this.params.end_date){
			this.params.end_date = new Date(this.params.end_date);
		}
		/*
			@paginate is a function to paginate to the next and previous page 
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
		this.handleSelection =  {
			selectedItemArray : [],
			selectedVendor : undefined,
			toggle : function (item){
				if(self.handleSelection.selectedItemArray.length > 0){
					if(item.vendor_id != self.handleSelection.selectedVendor){
						alert("You cannot select different vendor");
						return;
					}
				}
				else{
					self.handleSelection.selectedVendor = item.vendor_id;
				}
				var idx = self.handleSelection.selectedItemArray.indexOf(item);
        		if (idx > -1) self.handleSelection.selectedItemArray.splice(idx, 1);
        		else self.handleSelection.selectedItemArray.push(item);
			},
			exists : function (item) {
        		return self.handleSelection.selectedItemArray.indexOf(item) > -1;

      		},
			addItem : function(item){
				item.selected = true;
				self.handleSelection.selectedItemArray.push(item);
			},
			removeItem : function (item){
				var index = self.selectedItemArray.indexOf(item);
				if(index > -1) {
					item.selected = false;
					self.handleSelection.selectedItemArray.splice(index,1);
					return true;
				}
				else{
					return false;
				}
			},
			isSelected : function(){
				if(self.handleSelection.selectedItemArray.length > 0){
					return true;
				}
				else {
					return false;
				}
			},
			clearAll : function (){
				self.handleSelection.selectedItemArray = [];
				self.handleSelection.selectedVendor = undefined;
				return self.handleSelection.selectedItemArray;
			},
			slectedItemLength : function (){
				return self.handleSelection.selectedItemArray.length;
			},
			getAlltransactionIds : function(){
				var array = [];
				self.handleSelection.selectedItemArray.forEach(function(tr){
					array.push(tr.delivery_id);
				});
				return array;
			}
		};
		/*
			@transferDeposit function to open transfer deposit popup and send a transfer request to server.
		*/
		self.transferDeposit = function(){
			$mdDialog.show({
				controller         : ('EditDgCntrl',['$mdDialog','deposits',TransferDepositCntrl]),
				controllerAs       : 'transferDeposit',
				templateUrl        : '/static/modules/cod/dialog/transfer-deposit.html',
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				locals             : {
					       deposits : self.handleSelection.selectedItemArray,
				},
			})
			.then(function(dp) {
				dp.total_cod_transferred = parseInt(dp.total_cod_transferred);
				dp.delivery_ids = self.handleSelection.getAlltransactionIds();
				dp.vendor_id = self.handleSelection.selectedVendor;
				Notification.loaderStart();
				COD.tranferToClient.send(dp,function(response){
					Notification.showSuccess('Transfered Successfully');
					Notification.loaderComplete();
					self.handleSelection.clearAll();
					self.getDeposits();
				},function(err){
					Notification.loaderComplete();
				});
			});
		};		
		/*
			@dgSearchTextChange is a function for Delivery guy search for filter. When ever the filtered dg change, 
			this function is called.

			@selectedVendorChange is a callback function after vendor guy selection in the filter.
		*/
		self.vendorSearchTextChange = function(text){
			var search = {
				search : text
			};
			return Vendor.query(search).$promise.then(function (response){
				return response.payload.data.data;
			});
		};

		self.selectedVendorChange = function(vendor){
			if(vendor){
				self.params.vendor_id = vendor.id;
				self.params.vendor_name = vendor.name;
			}
			else{
				self.params.vendor_id = undefined;
				self.params.vendor_name = undefined;
			}
		};
		/*
			@revertToPageOne is a function to revert back to first page if any kind of filter is applied
		*/ 
		this.revertToPageOne = function(){
			self.params.page = 1;
			self.getDeposits();
		};
		/*
			@resetParams funcion to reset the filter.
		*/
		self.resetParams = function(){
			self.params = {};
			self.getDeposits();
		};
		/*
			@getDeposits rleoads the cod controller according too the filter to get the new filtered data.
		*/
		this.getDeposits = function(){
			if (!self.params.vendor_id) {
				self.params.vendor_name = undefined;
			}
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('Cod')
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.cod.transfer',{
			url: "^/cod/transfer?page&start_date&end_date&vendor_id&vendor_name",
			templateUrl: "/static/modules/cod/transfer/transfer.html",
			controllerAs : 'transfer',
    		controller: "codTransferCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
					var allowed_user = [constants.userRole.ACCOUNTS];
					return Access.hasAnyRole(allowed_user); 
    			}],
    			varifiedDeposits : ['COD','$stateParams',function(COD,$stateParams){
    				$stateParams.start_date = ($stateParams.start_date !== undefined) ? new Date($stateParams.start_date).toISOString() : undefined;
    				$stateParams.end_date = ($stateParams.end_date !== undefined) ? new Date($stateParams.end_date).toISOString() : undefined;
    				$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    				return COD.getVerifiedDeposits.get($stateParams).$promise;
    			}],
    		}
		});
	}])
	.controller('codTransferCntrl', [
		'$state',
		'$stateParams',
		'$mdDialog',
		'varifiedDeposits',
		'COD',
		'Notification',
		'Vendor',
		codTransferCntrl
	]);
})();
(function(){
	'use strict';
	var codHistoryCntrl = function($state,$stateParams,historyDeposits,Notification,Vendor){
		var self = this;
		self.params = $stateParams;
		self.historyDeposits = historyDeposits.payload.data.all_transactions;
		self.total_pages = historyDeposits.payload.data.total_pages;
		self.total_deposits = historyDeposits.payload.data.total_count;
		this.searchVendor = this.params.vendor_name;

		if(this.params.start_date){
			this.params.start_date = new Date(this.params.start_date);
		}
		if(this.params.end_date){
			this.params.end_date = new Date(this.params.end_date);
		}
		/*
			@paginate is a function to paginate to the next and previous page 
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
			@dgSearchTextChange is a function for Delivery guy search for filter. When ever the filtered dg change, 
			this function is called.

			@selectedVendorChange is a callback function after vendor guy selection in the filter.
		*/
		self.vendorSearchTextChange = function(text){
			var search = {
				search : text
			};
			return Vendor.query(search).$promise.then(function (response){
				return response.payload.data.data;
			});
		};

		self.selectedVendorChange = function(vendor){
			if(vendor){
				self.params.vendor_id = vendor.id;
				self.params.vendor_name = vendor.name;
			}
			else{
				self.params.vendor_id = undefined;
				self.params.vendor_name = undefined;
			}
		};
		/*
			@revertToPageOne is a function to revert back to first page if any kind of filter is applied
		*/ 
		this.revertToPageOne = function(){
			self.params.page = 1;
			self.getDeposits();
		};
		/*
			@resetParams funcion to reset the filter.
		*/
		self.resetParams = function(){
			self.params = {};
			self.getDeposits();
		};
		/*
			@getDeposits rleoads the cod controller according too the filter to get the new filtered data.
		*/
		this.getDeposits = function(){
			if (!self.params.vendor_id) {
				self.params.vendor_name = undefined;
			}
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('Cod')
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.cod.history',{
			url: "^/cod/history?page&start_date&end_date&vendor_id&vendor_name",
			templateUrl: "/static/modules/cod/history/history.html",
			controllerAs : 'history',
    		controller: "codHistoryCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
					var allowed_user = [constants.userRole.ACCOUNTS];
					return Access.hasAnyRole(allowed_user); 
    			}],
    			historyDeposits : ['COD','$stateParams',function(COD,$stateParams){
    				$stateParams.start_date = ($stateParams.start_date !== undefined) ? new Date($stateParams.start_date).toISOString() : undefined;
    				$stateParams.end_date = ($stateParams.end_date !== undefined) ? new Date($stateParams.end_date).toISOString() : undefined;
    				$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    				return COD.transactionHistory.get($stateParams).$promise;
    			}],
    		}
		});
	}])
	.controller('codHistoryCntrl', [
		'$state',
		'$stateParams',
		'historyDeposits',
		'Notification',
		'Vendor',
		codHistoryCntrl
	]);
})();
(function(){
	'use strict';

	angular.module('feedback', [])
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.feedbackList',{
			url: "^/feedback/list?page",
			templateUrl: "/static/modules/feedback/list/list.html",
			controllerAs : 'feedbackList',
    		controller: "feedbackListCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER,constants.userRole.VENDOR];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    			tickets: ['Feedback','$stateParams', function (Feedback,$stateParams){
    						$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    						return Feedback.getTickets.query($stateParams).$promise;
    					}],
    			groups: ['Feedback', function (Feedback){
    						return Feedback.getGroups.query().$promise;
    					}]
    		}
		})
		.state('home.feedbackDetail',{
			url: "^/feedback/detail/:ticket_id",
			templateUrl: "/static/modules/feedback/detail/detail.html",
			controllerAs : 'feedbackDetail',
    		controller: "feedbackDetailCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER,constants.userRole.VENDOR];
    						return Access.hasAnyRole(allowed_user); 
    					}],
                ticket: ['Feedback','$stateParams', function (Feedback,$stateParams){
                            return Feedback.getTicketsById.get($stateParams).$promise;
                        }],
                groups: ['Feedback', function (Feedback){
                            return Feedback.getGroups.query().$promise;
                        }]
    		}
		});
	}]);
})();
(function(){
	'use strict';
	var feedbackListCntrl = function($state,$stateParams,Feedback,tickets,groups){
		var self =  this;
		this.params = $stateParams;
		this.tickets = tickets.payload.data.data;
		this.total_pages = tickets.payload.data.total_pages;
		this.total_tickets = tickets.payload.data.total_tickets;
		this.groups = groups.payload.data;
		/*
			@paginate object to handle pagination.
		*/
		this.paginate = {
			nextpage : function(){
				self.params.page = self.params.page + 1;
				self.getTickets();
			},
			previouspage : function(){
				self.params.page = self.params.page - 1;
				self.getTickets();
			}
		};
		/*
			@getGroupName function that returns the feedback type based on the group id of the ticket
		*/
		this.getGroupName = function(id){
			if(self.groups){
				for(var i=0 ; i< self.groups.length;i++){
					if(id == self.groups[i].group.id){
						return self.groups[i].group.name;
					}
				}
			}
		};

		/*
			@getTickets rleoads the tickets controller according too the filter to get the new filtered data.
		*/
		this.getTickets = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};

	};

	angular.module('feedback')
	.controller('feedbackListCntrl', [
		'$state',
		'$stateParams',
		'Feedback',
		'tickets',
		'groups',
		feedbackListCntrl
	]);
})();
(function(){
	'use strict';
	var feedbackDetailCntrl = function($state,$stateParams,$mdDialog,Feedback,ticket,groups,Notification,PreviousState,UserProfile,constants){
		console.log(ticket);
		var self =  this;
		this.params = $stateParams;
		this.ticket = ticket.payload.data.helpdesk_ticket;
		this.groups = groups.payload.data;
		/*
			function to redirect back to the previous page or parent page.
		*/
		self.goBack = function(){
			if(PreviousState.isAvailable()){
				PreviousState.redirectToPrevious();
			}
			else{
				$state.go('home.feedbackList');
			}
		};
		/*
			@getGroupName function that returns the feedback type based on the group id of the ticket
		*/
		this.getGroupName = function(id){
			if(self.groups){
				for(var i=0 ; i< self.groups.length;i++){
					if(id == self.groups[i].group.id){
						return self.groups[i].group.name;
					}
				}
			}
		};
		/*
			@getUsername function that returns the name of the user who has updated the note
		*/
		this.getUsername =  function(id){
			if(id == self.ticket.requester_id){
				return self.ticket.requester_name;
			}
			else{
				return self.ticket.responder_name;
			}
		};
		this.showConfirm = function(ev) {
		    // Appending dialog to document.body to cover sidenav in docs app
		    var confirm = $mdDialog.confirm()
		    .title('Are you sure you want to resolve this issue')
		    .ariaLabel('Resolve Feedback')
		    .targetEvent(ev)
		    .ok('Confirm')
		    .cancel('Cancel');
		    $mdDialog.show(confirm).then(function() {
		    	self.closeComplain({});
		    });
		};
		/*
			@addNotes function to add a note for the feedback
		*/
		this.addNotes = function(data){
			Notification.loaderStart();
			data.id = self.ticket.display_id;
			if(UserProfile.$getUserRole() === constants.userRole.VENDOR){
				data.note.helpdesk_note.user_id = self.ticket.requester_id;
			}
			else{
				data.note.helpdesk_note.user_id = self.ticket.responder_id;
			}
			Feedback.addNotes.update(data,function(response){
				self.getTicket();
			});
		};
		/*
			@closeComplain function to close the feedback
		*/
		this.closeComplain = function(data){
			Notification.loaderStart();
			data.id = self.ticket.display_id;
			data.resolve = {
				helpdesk_ticket :{
					status: "5"
				}
			};
			Feedback.resolve.update(data,function(response){
				self.getTicket();
			});
		};
		/*
			@getTickets rleoads the tickets controller according too the filter to get the new filtered data.
		*/
		this.getTicket = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};

	};

	angular.module('feedback')
	.controller('feedbackDetailCntrl', [
		'$state',
		'$stateParams',
		'$mdDialog',
		'Feedback',
		'ticket',
		'groups',
		'Notification',
		'PreviousState',
		'UserProfile',
		'constants',
		feedbackDetailCntrl
	]);
})();
(function(){
	'use strict';
    var notificationCntrl = function($scope,$state,$stateParams,$rootScope,Notice,notices){
        var self = this;
        self.params =  $stateParams;
        self.notices = notices.payload.data.data;
        self.total_notifications =  notices.payload.data.total_notifications;
        self.total_pages =  notices.payload.data.total_pages;

        /*
            @paginate object to handle pagination.
        */
        this.paginate = {
            nextpage : function(){
                self.params.page = self.params.page + 1;
                self.getTickets();
            },
            previouspage : function(){
                self.params.page = self.params.page - 1;
                self.getTickets();
            }
        };
        $rootScope.$on('notificationUpdated',self.getNotification);

        this.makeAsRead = function(notice){
            Notice.markAsRead.update({id: notice.notification_id},function(response){
            $scope.home.getNoticeCount();
            notice.delivery_id = notice.delivery_id.split(',');
            if(notice.delivery_id.length == 1 && notice.delivery_id.indexOf("") === -1){
                $state.go('home.orderDetail',{id:notice.delivery_id.join()});
            }
            else if(notice.delivery_id.length > 1) {
              $state.go('home.opsorder',{delivery_ids:notice.delivery_id.join()});
            }
            else {
              self.getNotification();
            }
      });
        };
        /*
            @getNotifications rleoads the notification controller according too the filter to get the new filtered data.
        */
        this.getNotifications = function(){
            $state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
        };
    };

	angular.module('notification', [])
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.notification',{
			url: "^/notification?page",
			templateUrl: "/static/modules/notification/notification.html",
			controllerAs : 'notification',
    		controller: "notificationCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    			notices: ['Notice','$stateParams', function (Notice,$stateParams){
    						$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    						return Notice.getNotifications.query($stateParams).$promise;
    					}]
    		}
		});
	}])
    .controller('notificationCntrl', [
        '$scope',
        '$state',
        '$stateParams',
        '$rootScope',
        'Notice',
        'notices',
        notificationCntrl
    ]);
})();
(function(){
	'use strict';
	angular.module('notification')
	.filter('fromNow', function(){
		return function (date) {
			return moment(date).fromNow();
		};
	});

})();