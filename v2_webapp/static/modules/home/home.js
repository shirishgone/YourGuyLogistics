(function(){
	'use strict';
	var homeCntrl = function($rootScope,$state,$mdSidenav,$mdDialog,$mdToast,constants,UserProfile,Notification){
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
			});
		};
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
					hideDelay: 600000,
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
		'Notification',
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