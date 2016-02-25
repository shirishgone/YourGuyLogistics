(function(){
	'use strict';
	var homeCntrl = function($state,$mdSidenav,$mdDialog,constants,UserProfile){
		// Show tabs page accorfing to the credentials.
		this.tabs =  constants.permissible_tabs[UserProfile.role];
		// Controller logic for common items between vendor and admin.
		var self = this;
		this.user_name = UserProfile.name;
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
			UserProfile.$clearUserRole();
			UserProfile.$refresh().then(function (vendor){
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
			abstract: true,
			controllerAs : 'home',
    		controller: "homeCntrl",
    		resolve: {
    			UserProfile : 'UserProfile',
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
		'UserProfile',
		homeCntrl
	]);
})();